"""
Categorization Validator Module
Validates categorizations and re-categorizes suspicious transactions
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CategorizationValidator:
    """Validates transaction categorizations and re-categorizes suspicious ones"""
    
    def __init__(
        self,
        max_spending_ratio: float = 1.0,
        suspicious_single_txn_ratio: float = 0.5,
        suspicious_category_ratio: float = 0.3,
        api_key: str = "",
        model: str = "llama-3.3-70b-versatile",
        base_url: str = ""
    ):
        """
        Initialize categorization validator
        
        Args:
            max_spending_ratio: Maximum spending as ratio of income (default: 1.0 = 100%)
            suspicious_single_txn_ratio: Single transaction > this ratio of income is suspicious (default: 0.5 = 50%)
            suspicious_category_ratio: Single category > this ratio of income is suspicious (default: 0.3 = 30%)
            api_key: Groq API key for re-categorization
            model: Model name for re-categorization
            base_url: Base URL for Groq API
        """
        self.max_spending_ratio = max_spending_ratio
        self.suspicious_single_txn_ratio = suspicious_single_txn_ratio
        self.suspicious_category_ratio = suspicious_category_ratio
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.groq.com/openai/v1"
        
        if not api_key:
            raise ValueError("Groq API key is required for validation")
        
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=self.base_url
            )
            logger.info(f"Initialized CategorizationValidator with model: {model}")
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
    def validate_periods(
        self,
        periods: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate categorizations across all periods
        
        Args:
            periods: List of period dictionaries with categorized transactions
            
        Returns:
            Dictionary with validation results and warnings
        """
        logger.info(f"Validating categorizations across {len(periods)} periods")
        
        validation_results = {
            'warnings': [],
            'suspicious_transactions': [],
            'period_issues': []
        }
        
        for period in periods:
            period_id = period.get('period_id', 'unknown')
            income_amount = period.get('income_amount', 0.0)
            transactions = period.get('transactions', [])
            
            # Skip pre-income period for spending validation
            if period_id == 'pre-income' or income_amount == 0:
                continue
            
            # Check 1: Total spending exceeds income (code-based validation)
            total_expenses = period.get('total_expenses', 0.0)
            remaining_from_income = period.get('remaining_from_income', income_amount - total_expenses)
            
            if total_expenses > income_amount * self.max_spending_ratio:
                warning = {
                    'type': 'spending_exceeds_income',
                    'period_id': period_id,
                    'income_amount': income_amount,
                    'total_expenses': total_expenses,
                    'excess': total_expenses - income_amount,
                    'severity': 'high'
                }
                validation_results['warnings'].append(warning)
                validation_results['period_issues'].append(period_id)
                logger.warning(
                    f"Period {period_id}: Spending ({total_expenses:.2f}) exceeds income ({income_amount:.2f})"
                )
            
            # Check 2: Single transaction exceeds threshold
            for txn in transactions:
                if txn.get('transaction_type') == 'debit':
                    txn_amount = abs(float(txn.get('amount', 0)))
                    if txn_amount > income_amount * self.suspicious_single_txn_ratio:
                        validation_results['suspicious_transactions'].append({
                            'transaction_id': txn.get('transaction_id'),
                            'period_id': period_id,
                            'amount': txn_amount,
                            'income_amount': income_amount,
                            'ratio': txn_amount / income_amount,
                            'current_category': txn.get('category', 'Unknown'),
                            'reason': f'Single transaction ({txn_amount:.2f}) exceeds {self.suspicious_single_txn_ratio * 100}% of income'
                        })
            
            # Check 3: Category totals seem unrealistic
            category_totals = {}
            for txn in transactions:
                if txn.get('transaction_type') == 'debit':
                    category = txn.get('category', 'Other')
                    amount = abs(float(txn.get('amount', 0)))
                    category_totals[category] = category_totals.get(category, 0) + amount
            
            for category, total in category_totals.items():
                if total > income_amount * self.suspicious_category_ratio:
                    warning = {
                        'type': 'category_exceeds_threshold',
                        'period_id': period_id,
                        'category': category,
                        'category_total': total,
                        'income_amount': income_amount,
                        'ratio': total / income_amount,
                        'severity': 'medium'
                    }
                    validation_results['warnings'].append(warning)
                    logger.warning(
                        f"Period {period_id}: Category '{category}' ({total:.2f}) exceeds "
                        f"{self.suspicious_category_ratio * 100}% of income"
                    )
        
        logger.info(
            f"Validation complete: {len(validation_results['warnings'])} warnings, "
            f"{len(validation_results['suspicious_transactions'])} suspicious transactions"
        )
        
        return validation_results
    
    def re_categorize_suspicious(
        self,
        suspicious_transactions: List[Dict[str, Any]],
        period_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Re-categorize suspicious transactions with additional context
        
        Args:
            suspicious_transactions: List of suspicious transaction dictionaries
            period_context: Period context (income, other transactions, etc.)
            
        Returns:
            List of re-categorized transactions
        """
        if not suspicious_transactions:
            return []
        
        logger.info(f"Re-categorizing {len(suspicious_transactions)} suspicious transactions")
        
        # Prepare context
        income_amount = period_context.get('income_amount', 0.0)
        total_expenses = period_context.get('total_expenses', 0.0)
        period_txns = period_context.get('transactions', [])
        
        # Format transactions for prompt
        txn_texts = []
        for txn in suspicious_transactions:
            txn_texts.append(
                f"ID: {txn.get('transaction_id')}\n"
                f"Date: {txn.get('date', 'N/A')}\n"
                f"Description: {txn.get('description', 'N/A')}\n"
                f"Amount: {txn.get('amount', 0):.2f} {txn.get('currency', 'TRY')}\n"
                f"Current Category: {txn.get('category', 'Unknown')}\n"
                f"Current Subcategory: {txn.get('subcategory', 'Unknown')}\n"
                f"Issue: {txn.get('reason', 'N/A')}"
            )
        
        prompt = f"""You are re-categorizing financial transactions that were flagged as suspicious.

CONTEXT:
- Period Income: {income_amount:.2f} TRY
- Total Expenses in Period: {total_expenses:.2f} TRY
- Issue: Spending exceeds available income or single transaction is unusually large

These transactions were initially categorized, but the categorization seems unrealistic given the available income. Please re-evaluate each transaction considering:
1. The available income in this period
2. Whether the transaction might be a transfer, loan, or refund rather than an expense
3. Whether the category should be changed to better reflect the actual nature of the transaction
4. Common spending patterns (e.g., food typically doesn't exceed 30% of income)

SUSPICIOUS TRANSACTIONS:
{chr(10).join(f'{i+1}. {txn}' for i, txn in enumerate(txn_texts))}

AVAILABLE CATEGORIES:
- Food & Dining: Restaurants, Groceries, Fast Food, Coffee & Beverages, Food Delivery
- Shopping: Clothing & Apparel, Electronics, Home & Garden, Online Shopping, Department Stores
- Bills & Utilities: Electricity, Water, Gas, Internet & Phone, Cable & TV, Insurance
- Transportation: Gas & Fuel, Public Transit, Parking, Taxi & Rideshare, Vehicle Maintenance
- Entertainment: Movies & Theater, Sports & Recreation, Music & Concerts, Gaming, Streaming Services
- Healthcare: Doctor & Medical, Pharmacy, Dental, Hospital, Health Insurance
- Education: Tuition, Books & Supplies, Courses & Training
- Personal Care: Hair & Beauty, Gym & Fitness, Personal Services
- Travel: Hotels, Flights, Car Rental, Travel Services
- Financial: Bank Fees, Interest, Investment, Loan Payment, Transfer Fees
- Income: Salary, Freelance, Investment Returns, Refunds, Other Income
- Transfers: Internal Transfer, External Transfer, Payment to Others
- Other: Uncategorized, Miscellaneous

OUTPUT FORMAT (JSON array):
[
  {{
    "transaction_id": "transaction_id_from_input",
    "category": "Revised Category Name",
    "subcategory": "Revised Subcategory Name",
    "confidence": 0.95,
    "reasoning": "Explanation of why this category is more appropriate given the income context"
  }}
]

Return ONLY the JSON array, one entry per transaction in the same order."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in categorizing financial transactions with income context. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4096
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON
            import json
            import re
            
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            try:
                re_categorized = json.loads(result)
            except json.JSONDecodeError:
                json_match = re.search(r'\[.*\]', result, re.DOTALL)
                if json_match:
                    re_categorized = json.loads(json_match.group(0))
                else:
                    logger.error("Could not parse re-categorization results")
                    return suspicious_transactions  # Return original
            
            # Update transactions with new categorizations
            updated_transactions = []
            for i, txn in enumerate(suspicious_transactions):
                if i < len(re_categorized):
                    recat = re_categorized[i]
                    updated_txn = {
                        **txn,
                        'category': recat.get('category', txn.get('category', 'Other')),
                        'subcategory': recat.get('subcategory', txn.get('subcategory', 'Uncategorized')),
                        'category_confidence': recat.get('confidence', 0.5),
                        're_categorized': True,
                        're_categorization_reasoning': recat.get('reasoning', 'Re-categorized due to income context')
                    }
                    updated_transactions.append(updated_txn)
                    logger.info(
                        f"Re-categorized transaction {txn.get('transaction_id')}: "
                        f"{txn.get('category')} -> {recat.get('category')}"
                    )
                else:
                    updated_transactions.append(txn)
            
            return updated_transactions
            
        except Exception as e:
            logger.error(f"Error in re-categorization: {e}")
            return suspicious_transactions  # Return original on error

