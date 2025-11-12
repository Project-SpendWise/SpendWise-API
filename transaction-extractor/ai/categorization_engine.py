"""
AI-Powered Transaction Categorization Engine
Uses Groq API to categorize transactions for analysis
"""
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class TransactionCategoryEngine:
    """AI-powered categorization engine for transactions using Groq"""
    
    # Standard transaction categories for financial analysis
    CATEGORIES = {
        "Food & Dining": {
            "Restaurants",
            "Groceries",
            "Fast Food",
            "Coffee & Beverages",
            "Food Delivery"
        },
        "Shopping": {
            "Clothing & Apparel",
            "Electronics",
            "Home & Garden",
            "Online Shopping",
            "Department Stores"
        },
        "Bills & Utilities": {
            "Electricity",
            "Water",
            "Gas",
            "Internet & Phone",
            "Cable & TV",
            "Insurance"
        },
        "Transportation": {
            "Gas & Fuel",
            "Public Transit",
            "Parking",
            "Taxi & Rideshare",
            "Vehicle Maintenance"
        },
        "Entertainment": {
            "Movies & Theater",
            "Sports & Recreation",
            "Music & Concerts",
            "Gaming",
            "Streaming Services"
        },
        "Healthcare": {
            "Doctor & Medical",
            "Pharmacy",
            "Dental",
            "Hospital",
            "Health Insurance"
        },
        "Education": {
            "Tuition",
            "Books & Supplies",
            "Courses & Training"
        },
        "Personal Care": {
            "Hair & Beauty",
            "Gym & Fitness",
            "Personal Services"
        },
        "Travel": {
            "Hotels",
            "Flights",
            "Car Rental",
            "Travel Services"
        },
        "Financial": {
            "Bank Fees",
            "Interest",
            "Investment",
            "Loan Payment",
            "Transfer Fees"
        },
        "Income": {
            "Salary",
            "Freelance",
            "Investment Returns",
            "Refunds",
            "Other Income"
        },
        "Transfers": {
            "Internal Transfer",
            "External Transfer",
            "Payment to Others"
        },
        "Other": {
            "Uncategorized",
            "Miscellaneous"
        }
    }
    
    def __init__(self, api_key: str = "", model: str = "llama-3.3-70b-versatile", base_url: str = ""):
        """
        Initialize categorization engine with Groq
        
        Args:
            api_key: Groq API key
            model: Model name to use (default: llama-3.3-70b-versatile)
            base_url: Base URL for Groq API
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.groq.com/openai/v1"
        
        if not api_key:
            raise ValueError("Groq API key is required")
        
        # Initialize Groq client (uses OpenAI-compatible API)
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=self.base_url
            )
            logger.info(f"Initialized Transaction Category Engine with model: {model}")
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
    def _create_categorization_prompt(
        self,
        transactions: List[Dict[str, Any]],
        period_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create categorization prompt for the AI model
        
        Args:
            transactions: List of transaction dictionaries
            period_context: Optional period context (income, running balance, etc.)
            
        Returns:
            Formatted prompt
        """
        # Format transactions for the prompt
        transactions_text = []
        for i, txn in enumerate(transactions, 1):
            txn_text = f"{i}. Date: {txn.get('date', 'N/A')}\n"
            txn_text += f"   Description: {txn.get('description', 'N/A')}\n"
            txn_text += f"   Amount: {txn.get('amount', 0):.2f} {txn.get('currency', 'TRY')}\n"
            txn_text += f"   Type: {txn.get('transaction_type', 'N/A')}\n"
            if txn.get('channel'):
                txn_text += f"   Channel: {txn.get('channel')}\n"
            transactions_text.append(txn_text)
        
        categories_list = "\n".join([f"- {cat}: {', '.join(subcats)}" for cat, subcats in self.CATEGORIES.items()])
        
        # Add period context if available
        context_info = ""
        if period_context:
            income = period_context.get('income_amount', 0.0)
            total_expenses_so_far = period_context.get('total_expenses_so_far', 0.0)
            remaining_balance = income - total_expenses_so_far
            period_id = period_context.get('period_id', 'unknown')
            
            context_info = f"""
PERIOD CONTEXT:
- Period ID: {period_id}
- Income for this period: {income:.2f} TRY
- Expenses so far in this period: {total_expenses_so_far:.2f} TRY
- Remaining balance: {remaining_balance:.2f} TRY

IMPORTANT: When categorizing, consider the available income. Spending should be realistic relative to the income amount.
"""
        
        prompt = f"""You are an expert in categorizing financial transactions for personal finance analysis.

Your task is to categorize each transaction into the most appropriate category and subcategory based on the transaction description, amount, and context.
{context_info}

AVAILABLE CATEGORIES AND SUBCATEGORIES:
{categories_list}

INSTRUCTIONS:
1. Analyze each transaction's description carefully
2. Consider Turkish language keywords and merchant names
3. For Turkish transactions, look for:
   - "MARKET", "SÜPERMARKET", "MIGROS", "A101", "BIM" → Food & Dining > Groceries
   - "RESTORAN", "CAFE", "KAHVE" → Food & Dining > Restaurants or Coffee & Beverages
   - "AKARYAKIT", "BENZIN", "PETROL" → Transportation > Gas & Fuel
   - "ELEKTRİK", "SU", "DOĞALGAZ" → Bills & Utilities
   - "HASTANE", "ECZANE", "DOKTOR" → Healthcare
   - "KART KOMİSYONU", "BANKA ÜCRETİ" → Financial > Bank Fees
   - "MAAŞ", "MAAŞ ÖDEMESİ" → Income > Salary
   - "HAVALE", "EFT", "TRANSFER" → Transfers
4. Use context clues from merchant names and transaction channels
5. For POS transactions, infer category from merchant name
6. For transfers, determine if it's income, payment, or internal transfer
7. If uncertain, choose the most likely category

TRANSACTIONS TO CATEGORIZE:
{chr(10).join(transactions_text)}

OUTPUT FORMAT (JSON array):
[
  {{
    "transaction_id": "transaction_id_from_input",
    "category": "Category Name",
    "subcategory": "Subcategory Name",
    "confidence": 0.95,
    "tags": ["tag1", "tag2"]
  }}
]

Return ONLY the JSON array, no additional text or explanation. Ensure the array has exactly {len(transactions)} items, one for each transaction."""
        
        return prompt
    
    def categorize_with_groq(self, prompt: str, temperature: float = 0.1, max_tokens: int = 4096) -> List[Dict[str, Any]]:
        """
        Categorize transactions using Groq API
        
        Args:
            prompt: Categorization prompt
            temperature: Model temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            List of categorized transactions
        """
        try:
            logger.info(f"Calling Groq API for categorization with model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in categorizing financial transactions. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            logger.info(f"Received categorization response, length: {len(result)}")
            
            # Parse JSON (handle markdown code blocks if present)
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            # Try to parse JSON with error recovery
            try:
                categorized_data = json.loads(result)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error: {e}. Attempting recovery...")
                # Try to fix common JSON issues
                result = result.replace(',}', '}').replace(',]', ']')
                try:
                    categorized_data = json.loads(result)
                    logger.info("JSON recovery successful")
                except json.JSONDecodeError:
                    # If still fails, try to extract JSON array
                    import re
                    json_match = re.search(r'\[.*\]', result, re.DOTALL)
                    if json_match:
                        result = json_match.group(0)
                        categorized_data = json.loads(result)
                        logger.info("Extracted JSON from response")
                    else:
                        raise
            
            if not isinstance(categorized_data, list):
                raise ValueError("Expected a JSON array but got a different type")
            
            return categorized_data
            
        except Exception as e:
            logger.error(f"Error calling Groq API for categorization: {e}")
            raise
    
    def categorize_transactions(
        self,
        transactions: List[Dict[str, Any]],
        batch_size: int = 50,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        delay_between_batches: float = 2.5,
        period_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Categorize a list of transactions using Groq AI
        
        Args:
            transactions: List of transaction dictionaries
            batch_size: Number of transactions to process per batch
            temperature: Model temperature
            max_tokens: Maximum tokens per request
            delay_between_batches: Seconds to wait between batches
            
        Returns:
            List of transactions with added category information
        """
        import time
        
        total_transactions = len(transactions)
        logger.info(f"Starting categorization for {total_transactions} transactions (batch_size: {batch_size})")
        
        if total_transactions == 0:
            return []
        
        categorized_transactions = []
        
        # Process in batches to avoid token limits and rate limits
        batches = [transactions[i:i + batch_size] for i in range(0, total_transactions, batch_size)]
        total_batches = len(batches)
        
        logger.info(f"Split into {total_batches} batches for categorization")
        
        for batch_idx, batch in enumerate(batches, 1):
            logger.info(f"Categorizing batch {batch_idx}/{total_batches} ({len(batch)} transactions)...")
            
            try:
                # Create prompt for this batch with period context
                # Update running balance for this batch
                batch_context = None
                if period_context:
                    # Calculate expenses so far (before this batch)
                    expenses_before = sum(
                        abs(float(t.get('amount', 0)))
                        for t in transactions[:batch_idx * batch_size - len(batch)]
                        if t.get('transaction_type') == 'debit'
                    )
                    batch_context = {
                        **period_context,
                        'total_expenses_so_far': expenses_before
                    }
                
                prompt = self._create_categorization_prompt(batch, batch_context)
                
                # Get categorizations from AI
                categorizations = self.categorize_with_groq(prompt, temperature, max_tokens)
                
                # Create a mapping of transaction_id to categorization
                cat_map = {cat.get('transaction_id'): cat for cat in categorizations}
                
                # Merge categorizations with transactions
                for txn in batch:
                    txn_id = txn.get('transaction_id')
                    if txn_id and txn_id in cat_map:
                        cat_info = cat_map[txn_id]
                        # Add category fields to transaction
                        txn['category'] = cat_info.get('category', 'Other')
                        txn['subcategory'] = cat_info.get('subcategory', 'Uncategorized')
                        txn['category_confidence'] = cat_info.get('confidence', 0.5)
                        txn['tags'] = cat_info.get('tags', [])
                    else:
                        # Fallback if transaction not found in categorization results
                        # Try index-based matching as backup
                        txn_idx = batch.index(txn)
                        if txn_idx < len(categorizations):
                            cat_info = categorizations[txn_idx]
                            txn['category'] = cat_info.get('category', 'Other')
                            txn['subcategory'] = cat_info.get('subcategory', 'Uncategorized')
                            txn['category_confidence'] = cat_info.get('confidence', 0.5)
                            txn['tags'] = cat_info.get('tags', [])
                        else:
                            # Final fallback
                            txn['category'] = 'Other'
                            txn['subcategory'] = 'Uncategorized'
                            txn['category_confidence'] = 0.0
                            txn['tags'] = []
                    
                    categorized_transactions.append(txn)
                
                logger.info(f"Batch {batch_idx}: Categorized {len(batch)} transactions")
                
                # Wait before next batch (except after last batch)
                if batch_idx < total_batches:
                    logger.info(f"Waiting {delay_between_batches}s before next batch...")
                    time.sleep(delay_between_batches)
                    
            except Exception as e:
                logger.error(f"Error categorizing batch {batch_idx}: {e}")
                # Add fallback categorization for failed batch
                for txn in batch:
                    txn['category'] = 'Other'
                    txn['subcategory'] = 'Uncategorized'
                    txn['category_confidence'] = 0.0
                    txn['tags'] = []
                    categorized_transactions.append(txn)
                
                # Wait before continuing
                if batch_idx < total_batches:
                    time.sleep(delay_between_batches)
        
        logger.info(f"Categorization complete: {len(categorized_transactions)} transactions categorized")
        
        return categorized_transactions
    
    def categorize_single_transaction(
        self,
        transaction: Dict[str, Any],
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Categorize a single transaction (useful for real-time categorization)
        
        Args:
            transaction: Single transaction dictionary
            temperature: Model temperature
            max_tokens: Maximum tokens
            
        Returns:
            Transaction with added category information
        """
        categorized = self.categorize_transactions(
            [transaction],
            batch_size=1,
            temperature=temperature,
            max_tokens=max_tokens,
            delay_between_batches=0
        )
        
        return categorized[0] if categorized else transaction

