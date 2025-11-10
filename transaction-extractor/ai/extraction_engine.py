"""
AI Extraction Engine
Uses Groq API to extract structured transaction data from Turkish bank statements
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIExtractionEngine:
    """AI-powered extraction engine for bank transactions using Groq"""
    
    def __init__(self, api_key: str = "", model: str = "llama-3.3-70b-versatile", base_url: str = ""):
        """
        Initialize AI extraction engine with Groq
        
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
            logger.info(f"Initialized Groq AI engine with model: {model}")
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
    def _create_extraction_prompt(self, raw_data: str, bank_name: Optional[str] = None) -> str:
        """
        Create extraction prompt for the AI model
        
        Args:
            raw_data: Raw extracted data from file
            bank_name: Detected bank name (optional)
            
        Returns:
            Formatted prompt
        """
        bank_context = f"\nDetected Bank: {bank_name}\n" if bank_name else ""
        
        prompt = f"""You are an expert in extracting transaction data from Turkish bank statements.

{bank_context}
Your task is to analyze the following bank statement data and extract ALL transactions in a structured JSON format.

IMPORTANT INSTRUCTIONS:
1. Extract EVERY transaction you can find in the data
2. Parse dates in DD.MM.YYYY or similar Turkish date formats
3. Identify transaction type (debit/credit) based on:
   - Amount sign (negative = debit, positive = credit)
   - Turkish keywords: "Giden" (outgoing/debit), "Gelen" (incoming/credit)
   - "Çekilen" (withdrawn/debit), "Yatan" (deposited/credit)
4. Extract amounts as numbers (remove currency symbols and thousands separators)
5. Currency is usually TRY (Turkish Lira) unless specified otherwise
6. Identify transaction channel from keywords:
   - ATM: ATM transactions
   - POS: Card payments at merchants
   - Transfer: Money transfers (Havale, Transfer, EFT)
   - Online: Online/internet banking
   - Mobile: Mobile banking
7. Generate a unique transaction_id for each transaction (can be row number or reference)
8. Keep original description in Turkish

DATA TO ANALYZE:
{raw_data}

OUTPUT FORMAT (JSON):
{{
  "bank_name": "Bank name from the statement",
  "account_number": "Masked account number if found (e.g., ****1234)",
  "statement_period_start": "YYYY-MM-DD or null",
  "statement_period_end": "YYYY-MM-DD or null",
  "opening_balance": number or null,
  "closing_balance": number or null,
  "currency": "TRY",
  "transactions": [
    {{
      "transaction_id": "unique_id",
      "date": "YYYY-MM-DD",
      "description": "Transaction description in Turkish",
      "amount": number (negative for debit, positive for credit),
      "currency": "TRY",
      "transaction_type": "debit" or "credit",
      "balance_after": number or null,
      "reference_number": "reference if available" or null,
      "channel": "ATM" or "POS" or "Transfer" or "Online" or "Mobile" or null
    }}
  ]
}}

Return ONLY the JSON, no additional text or explanation."""
        
        return prompt
    
    def extract_with_groq(self, prompt: str, temperature: float = 0.1, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Extract data using Groq API
        
        Args:
            prompt: Extraction prompt
            temperature: Model temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Extracted data as dictionary
        """
        try:
            logger.info(f"Calling Groq API with model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in extracting structured data from Turkish bank statements. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            logger.info(f"Received response from Groq, length: {len(result)}")
            
            # Parse JSON (handle markdown code blocks if present)
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            # Try to parse JSON with error recovery
            try:
                extracted_data = json.loads(result)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error: {e}. Attempting recovery...")
                # Try to fix common JSON issues
                # 1. Remove any trailing commas
                result = result.replace(',}', '}').replace(',]', ']')
                # 2. Try parsing again
                try:
                    extracted_data = json.loads(result)
                    logger.info("JSON recovery successful")
                except json.JSONDecodeError:
                    # If still fails, try to extract JSON object
                    import re
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        result = json_match.group(0)
                        extracted_data = json.loads(result)
                        logger.info("Extracted JSON from response")
                    else:
                        raise
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            raise
    
    def extract_transactions(
        self,
        raw_data: str,
        bank_name: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Extract transactions from raw data using Groq
        
        Args:
            raw_data: Raw extracted data from file
            bank_name: Detected bank name (optional)
            temperature: Model temperature
            max_tokens: Maximum tokens
            
        Returns:
            Extracted transaction data
        """
        logger.info("Starting transaction extraction with Groq")
        
        # Create prompt
        prompt = self._create_extraction_prompt(raw_data, bank_name)
        
        # Call Groq API
        result = self.extract_with_groq(prompt, temperature, max_tokens)
        
        # Add metadata
        result['extraction_metadata'] = {
            'extracted_at': datetime.utcnow().isoformat(),
            'ai_provider': 'groq',
            'ai_model': self.model,
            'transaction_count': len(result.get('transactions', []))
        }
        
        logger.info(f"Successfully extracted {len(result.get('transactions', []))} transactions")
        
        return result
    
    def extract_transactions_batch(
        self,
        records: list,
        bank_name: Optional[str] = None,
        chunk_size: int = 30,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        delay_between_chunks: float = 2.5
    ) -> Dict[str, Any]:
        """
        Extract transactions from large datasets by processing in batches
        
        Args:
            records: List of transaction records (dictionaries)
            bank_name: Detected bank name (optional)
            chunk_size: Number of records per batch
            temperature: Model temperature
            max_tokens: Maximum tokens per request
            delay_between_chunks: Seconds to wait between chunks to avoid rate limits
            
        Returns:
            Combined extracted transaction data
        """
        import time
        
        total_records = len(records)
        logger.info(f"Starting batch extraction for {total_records} records (chunk_size: {chunk_size}, delay: {delay_between_chunks}s)")
        
        all_transactions = []
        combined_result = {
            'bank_name': bank_name or '',
            'currency': 'TRY',
            'transactions': [],
            'account_number': None,
            'statement_period_start': None,
            'statement_period_end': None,
            'opening_balance': None,
            'closing_balance': None
        }
        
        # Split into chunks
        chunks = [records[i:i + chunk_size] for i in range(0, total_records, chunk_size)]
        total_chunks = len(chunks)
        
        logger.info(f"Split into {total_chunks} chunks")
        
        for chunk_idx, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {chunk_idx}/{total_chunks} ({len(chunk)} records)...")
            
            # Convert chunk to text format
            chunk_text = self._format_records_as_text(chunk)
            
            # Extract transactions for this chunk
            try:
                chunk_result = self.extract_transactions(
                    raw_data=chunk_text,
                    bank_name=bank_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Collect transactions
                chunk_transactions = chunk_result.get('transactions', [])
                all_transactions.extend(chunk_transactions)
                logger.info(f"Chunk {chunk_idx}: Extracted {len(chunk_transactions)} transactions")
                
                # Update metadata from first chunk
                if chunk_idx == 1:
                    combined_result['bank_name'] = chunk_result.get('bank_name', bank_name or '')
                    combined_result['account_number'] = chunk_result.get('account_number')
                    combined_result['statement_period_start'] = chunk_result.get('statement_period_start')
                    combined_result['currency'] = chunk_result.get('currency', 'TRY')
                
                # Update period end and closing balance from last chunk
                if chunk_idx == total_chunks:
                    combined_result['statement_period_end'] = chunk_result.get('statement_period_end')
                    combined_result['closing_balance'] = chunk_result.get('closing_balance')
                
                # Wait before next chunk to avoid rate limits (except after last chunk)
                if chunk_idx < total_chunks:
                    logger.info(f"Waiting {delay_between_chunks}s before next chunk to avoid rate limits...")
                    time.sleep(delay_between_chunks)
                
            except Exception as e:
                logger.error(f"Error processing chunk {chunk_idx}: {e}")
                # Wait before continuing to avoid compounding rate limit issues
                if chunk_idx < total_chunks:
                    logger.warning(f"Waiting {delay_between_chunks}s before next chunk after error...")
                    time.sleep(delay_between_chunks)
                # Continue with next chunk
                continue
        
        # Add all transactions
        combined_result['transactions'] = all_transactions
        
        # Add batch metadata
        combined_result['extraction_metadata'] = {
            'extracted_at': datetime.utcnow().isoformat(),
            'ai_provider': 'groq',
            'ai_model': self.model,
            'transaction_count': len(all_transactions),
            'batch_processing': True,
            'total_chunks': total_chunks,
            'chunk_size': chunk_size,
            'total_records_processed': total_records
        }
        
        logger.info(f"Batch extraction complete: {len(all_transactions)} total transactions from {total_chunks} chunks")
        
        return combined_result
    
    def _format_records_as_text(self, records: list) -> str:
        """
        Format a list of records as text for AI processing
        
        Args:
            records: List of dictionaries
            
        Returns:
            Formatted text string
        """
        if not records:
            return ""
        
        # Get column names from first record
        columns = list(records[0].keys())
        
        # Create header
        lines = [" | ".join(str(col) for col in columns)]
        lines.append("-" * len(lines[0]))
        
        # Add data rows
        for record in records:
            row_values = [str(record.get(col, '')) for col in columns]
            lines.append(" | ".join(row_values))
        
        return "\n".join(lines)
    
    def validate_and_fix_dates(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fix date formats in extracted data
        
        Args:
            extracted_data: Data from AI extraction
            
        Returns:
            Data with fixed dates
        """
        from dateutil import parser
        
        def fix_date(date_str):
            """Try to parse and fix date string"""
            if not date_str:
                return None
            try:
                # Try parsing the date
                dt = parser.parse(date_str)
                return dt.strftime("%Y-%m-%d")
            except:
                return date_str
        
        # Fix period dates
        if 'statement_period_start' in extracted_data:
            extracted_data['statement_period_start'] = fix_date(extracted_data['statement_period_start'])
        if 'statement_period_end' in extracted_data:
            extracted_data['statement_period_end'] = fix_date(extracted_data['statement_period_end'])
        
        # Fix transaction dates
        for txn in extracted_data.get('transactions', []):
            if 'date' in txn:
                txn['date'] = fix_date(txn['date'])
        
        return extracted_data

