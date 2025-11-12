"""
Income Detection Module
Identifies income transactions using rule-based detection and AI confirmation
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class IncomeDetector:
    """Detects income transactions from a list of transactions"""
    
    # Turkish keywords that indicate income
    INCOME_KEYWORDS = [
        "MAAŞ",
        "MAAŞ ÖDEMESİ",
        "MAAŞ ÖDEME",
        "SALARY",
        "PAYROLL",
        "ÜCRET",
        "GELİR",
        "HASILAT",
        "FAİZ GELİRİ",
        "DİVİDEND",
        "YATIRIM GETİRİSİ"
    ]
    
    # Keywords that indicate it's NOT income (transfers, refunds, etc.)
    NON_INCOME_KEYWORDS = [
        "HAVALE",
        "EFT",
        "TRANSFER",
        "İADE",
        "REFUND",
        "GERİ ÖDEME",
        "BORÇ",
        "KREDİ"
    ]
    
    def __init__(self, min_amount: float = 5000.0, api_key: str = "", model: str = "llama-3.3-70b-versatile", base_url: str = ""):
        """
        Initialize income detector
        
        Args:
            min_amount: Minimum amount to consider as income (default: 5000 TRY)
            api_key: Groq API key for AI confirmation (optional)
            model: Model name for AI confirmation
            base_url: Base URL for Groq API
        """
        self.min_amount = min_amount
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.groq.com/openai/v1"
        self.client = None
        
        if api_key:
            try:
                import openai
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url=self.base_url
                )
                logger.info(f"Initialized IncomeDetector with AI confirmation (model: {model})")
            except ImportError:
                logger.warning("openai package not available, AI confirmation disabled")
    
    def detect_income(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect income transactions from a list of transactions
        Uses code-based detection: looks for large credit amounts (monthly income pattern)
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of income transactions with confidence scores
        """
        logger.info(f"Detecting income transactions from {len(transactions)} total transactions")
        
        # Sort transactions by date to analyze patterns
        sorted_transactions = sorted(
            transactions,
            key=lambda x: self._parse_date(x.get('date', ''))
        )
        
        income_candidates = []
        
        # Step 1: Code-based detection - look for large credit amounts
        # This is the primary indicator for monthly income
        for txn in sorted_transactions:
            # Only consider credit transactions
            if txn.get('transaction_type') != 'credit':
                continue
            
            amount = abs(float(txn.get('amount', 0)))
            description = str(txn.get('description', '')).upper()
            balance_after = txn.get('balance_after')
            
            # Skip if amount is too small
            if amount < self.min_amount:
                continue
            
            confidence = 0.0
            reasons = []
            
            # Primary detection: Large credit amount (likely monthly income)
            # Monthly income is typically a large, regular amount
            if amount >= self.min_amount * 2:  # Large credit amount (2x minimum = 10,000 TRY default)
                # Check if this looks like a regular income pattern
                # Look at balance change - income typically causes significant balance increase
                if balance_after is not None:
                    # Find previous transaction to calculate balance change
                    txn_date = self._parse_date(txn.get('date', ''))
                    prev_txn = None
                    for prev in reversed(sorted_transactions):
                        if self._parse_date(prev.get('date', '')) < txn_date:
                            prev_txn = prev
                            break
                    
                    if prev_txn and prev_txn.get('balance_after') is not None:
                        prev_balance = float(prev_txn.get('balance_after', 0))
                        balance_increase = float(balance_after) - prev_balance
                        
                        # If balance increase matches the credit amount, it's likely income
                        if abs(balance_increase - amount) < 1.0:  # Allow small rounding differences
                            confidence = 0.95
                            reasons.append(f"Large credit ({amount:,.2f} TRY) with matching balance increase")
                        else:
                            confidence = 0.85
                            reasons.append(f"Large credit ({amount:,.2f} TRY)")
                    else:
                        confidence = 0.85
                        reasons.append(f"Large credit ({amount:,.2f} TRY)")
                else:
                    confidence = 0.80
                    reasons.append(f"Large credit ({amount:,.2f} TRY)")
            
            # Secondary check: Income keywords (but prioritize amount-based detection)
            has_income_keyword = any(keyword in description for keyword in self.INCOME_KEYWORDS)
            has_non_income_keyword = any(keyword in description for keyword in self.NON_INCOME_KEYWORDS)
            
            if has_income_keyword and not has_non_income_keyword:
                # Boost confidence if already detected by amount
                if confidence > 0:
                    confidence = min(0.98, confidence + 0.1)
                    reasons.append("Also contains income keyword")
                else:
                    confidence = 0.7
                    reasons.append("Contains income keyword")
            elif has_non_income_keyword and amount < self.min_amount * 3:
                # Reduce confidence if has non-income keywords and not very large
                confidence = max(0.3, confidence - 0.2)
                reasons.append("Contains non-income keywords")
            
            if confidence > 0:
                income_candidates.append({
                    'transaction': txn,
                    'confidence': confidence,
                    'reasons': reasons,
                    'amount': amount
                })
        
        # Sort by amount (descending) - largest amounts first (most likely income)
        income_candidates.sort(key=lambda x: x['amount'], reverse=True)
        
        logger.info(f"Found {len(income_candidates)} income candidates")
        
        # Step 2: Filter to most likely income (top candidates by amount)
        # Take top candidates that are significantly larger than others
        if income_candidates:
            # Get amounts
            amounts = [c['amount'] for c in income_candidates]
            if len(amounts) > 1:
                # Calculate median to identify outliers (likely income)
                amounts_sorted = sorted(amounts, reverse=True)
                median = amounts_sorted[len(amounts_sorted) // 2]
                
                # Income is typically much larger than regular credits
                # Take transactions that are at least 1.5x the median
                threshold = median * 1.5
            else:
                threshold = self.min_amount
            
            confirmed_income = [
                {
                    **candidate['transaction'],
                    'income_confidence': candidate['confidence'],
                    'income_detection_reasons': candidate['reasons']
                }
                for candidate in income_candidates
                if candidate['amount'] >= threshold or candidate['confidence'] >= 0.9
            ]
        else:
            confirmed_income = []
        
        logger.info(f"Confirmed {len(confirmed_income)} income transactions (using code-based detection)")
        
        return confirmed_income
    
    def _parse_date(self, date_str: Any) -> datetime:
        """Parse date string to datetime object"""
        if isinstance(date_str, datetime):
            return date_str
        
        if not date_str:
            return datetime.min
        
        from dateutil import parser
        try:
            return parser.parse(str(date_str))
        except:
            return datetime.min
    
    def _ai_confirm_income(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use AI to confirm income transactions
        
        Args:
            candidates: List of income candidate dictionaries
            
        Returns:
            List of confirmed income transactions
        """
        if not self.client:
            return []
        
        # Prepare prompt with candidate transactions
        candidates_text = []
        for i, candidate in enumerate(candidates, 1):
            txn = candidate['transaction']
            candidates_text.append(
                f"{i}. Date: {txn.get('date', 'N/A')}\n"
                f"   Description: {txn.get('description', 'N/A')}\n"
                f"   Amount: {txn.get('amount', 0):.2f} {txn.get('currency', 'TRY')}\n"
                f"   Type: {txn.get('transaction_type', 'N/A')}\n"
                f"   Rule-based confidence: {candidate['confidence']:.2f}"
            )
        
        prompt = f"""You are an expert in identifying income transactions from bank statements.

Analyze the following credit transactions and determine which ones are actual income (salary, freelance payments, investment returns, etc.) vs transfers, refunds, or other non-income credits.

INCOME INDICATORS:
- Salary/payroll payments (MAAŞ, SALARY, PAYROLL)
- Regular income patterns
- Large amounts from known employers
- Investment returns, dividends
- Freelance payments

NON-INCOME INDICATORS:
- Transfers from other accounts (HAVALE, EFT, TRANSFER)
- Refunds (İADE, REFUND)
- Loan disbursements (KREDİ, BORÇ)
- Reversals of previous transactions

TRANSACTIONS TO ANALYZE:
{chr(10).join(candidates_text)}

OUTPUT FORMAT (JSON array):
[
  {{
    "transaction_index": 1,
    "is_income": true,
    "confidence": 0.95,
    "reason": "Contains MAAŞ keyword and is a regular salary payment"
  }}
]

Return ONLY the JSON array, one entry per transaction in the same order."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in identifying income transactions. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2048
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON
            import json
            import re
            
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            # Try to parse
            try:
                ai_results = json.loads(result)
            except json.JSONDecodeError:
                # Try to extract JSON array
                json_match = re.search(r'\[.*\]', result, re.DOTALL)
                if json_match:
                    ai_results = json.loads(json_match.group(0))
                else:
                    logger.warning("Could not parse AI confirmation results, using rule-based only")
                    ai_results = []
            
            # Merge AI results with candidates
            confirmed_income = []
            for i, candidate in enumerate(candidates):
                if i < len(ai_results):
                    ai_result = ai_results[i]
                    if ai_result.get('is_income', False):
                        # Combine rule-based and AI confidence
                        combined_confidence = (candidate['confidence'] + ai_result.get('confidence', 0.5)) / 2
                        confirmed_income.append({
                            **candidate['transaction'],
                            'income_confidence': combined_confidence,
                            'income_detection_reasons': candidate['reasons'] + [ai_result.get('reason', 'AI confirmed')]
                        })
                else:
                    # Fallback: use rule-based if AI didn't return result
                    if candidate['confidence'] >= 0.7:
                        confirmed_income.append({
                            **candidate['transaction'],
                            'income_confidence': candidate['confidence'],
                            'income_detection_reasons': candidate['reasons']
                        })
            
            return confirmed_income
            
        except Exception as e:
            logger.error(f"Error in AI confirmation: {e}, using rule-based results only")
            # Fallback to rule-based
            return [
                {
                    **candidate['transaction'],
                    'income_confidence': candidate['confidence'],
                    'income_detection_reasons': candidate['reasons']
                }
                for candidate in candidates
                if candidate['confidence'] >= 0.7
            ]

