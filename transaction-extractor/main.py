#!/usr/bin/env python3
"""
Transaction Extraction System - Main Script
Orchestrates the extraction pipeline for Turkish bank statements
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import Config
from extractors import PDFExtractor, ExcelExtractor, CSVExtractor
from detectors import BankDetector
from ai import (
    AIExtractionEngine,
    TransactionCategoryEngine,
    IncomeDetector,
    PeriodAnalyzer,
    CategorizationValidator
)
from models import BankStatement, Transaction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TransactionExtractor:
    """Main transaction extraction orchestrator using Groq AI"""
    
    def __init__(self):
        """Initialize transaction extractor with Groq"""
        # Validate config
        try:
            Config.validate()
        except Exception as e:
            logger.error(f"Configuration error: {e}")
            raise
        
        # Get Groq AI configuration
        ai_config = Config.get_ai_config()
        
        # Initialize Groq AI engine
        self.ai_engine = AIExtractionEngine(
            api_key=ai_config['api_key'],
            model=ai_config['model'],
            base_url=ai_config['base_url']
        )
        
        # Initialize categorization engine with better model
        self.category_engine = TransactionCategoryEngine(
            api_key=ai_config['api_key'],
            model=Config.CATEGORIZATION_MODEL,
            base_url=ai_config['base_url']
        )
        
        # Initialize income detector
        self.income_detector = IncomeDetector(
            min_amount=Config.INCOME_DETECTION_MIN_AMOUNT,
            api_key=ai_config['api_key'],
            model=Config.CATEGORIZATION_MODEL,
            base_url=ai_config['base_url']
        )
        
        # Initialize period analyzer
        self.period_analyzer = PeriodAnalyzer()
        
        # Initialize validator
        self.validator = CategorizationValidator(
            max_spending_ratio=Config.VALIDATION_MAX_SPENDING_RATIO,
            suspicious_single_txn_ratio=Config.VALIDATION_SUSPICIOUS_SINGLE_TXN_RATIO,
            suspicious_category_ratio=Config.VALIDATION_SUSPICIOUS_CATEGORY_RATIO,
            api_key=ai_config['api_key'],
            model=Config.CATEGORIZATION_MODEL,
            base_url=ai_config['base_url']
        )
        
        logger.info(f"Initialized TransactionExtractor with extraction model: {ai_config['model']}, categorization model: {Config.CATEGORIZATION_MODEL}")
    
    def extract_from_file(self, file_path: str | Path, auto_batch: bool = True, batch_size: int = 30, batch_delay: float = None, categorize: bool = True) -> dict:
        """
        Extract transactions from a file with automatic batch processing for large files
        
        Args:
            file_path: Path to the bank statement file
            auto_batch: Automatically use batch processing for large files
            batch_size: Number of transactions per batch
            batch_delay: Seconds to wait between batches (None = use config default)
            categorize: Whether to categorize transactions using AI (default: True)
            
        Returns:
            Extracted transaction data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Starting extraction from: {file_path.name}")
        
        # Step 1: Detect bank
        logger.info("Step 1: Detecting bank...")
        bank_detection = BankDetector.detect_with_confidence(file_path.read_text(errors='ignore'))
        detected_bank = bank_detection['bank']
        confidence = bank_detection['confidence']
        
        if detected_bank:
            logger.info(f"Detected bank: {detected_bank} (confidence: {confidence:.2%})")
        else:
            logger.warning("Could not detect bank, proceeding with generic extraction")
        
        # Step 2: Extract raw data based on file type
        logger.info("Step 2: Extracting raw data from file...")
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            extractor = PDFExtractor(file_path)
            raw_data_dict = extractor.extract_structured()
        elif suffix in ['.xlsx', '.xls']:
            extractor = ExcelExtractor(file_path)
            raw_data_dict = extractor.extract_structured()
        elif suffix == '.csv':
            extractor = CSVExtractor(file_path)
            raw_data_dict = extractor.extract_structured()
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
        
        # Check if we have records (structured data) and if batch processing is needed
        records = raw_data_dict.get('records', [])
        use_batch = auto_batch and len(records) > 50  # Use batch for files with >50 transactions
        
        if use_batch:
            logger.info(f"Large file detected ({len(records)} records). Using batch processing...")
            
            # Step 3: Batch AI-powered extraction
            logger.info("Step 3: Processing with AI engine (batch mode)...")
            delay = batch_delay if batch_delay is not None else Config.BATCH_DELAY
            extracted_data = self.ai_engine.extract_transactions_batch(
                records=records,
                bank_name=detected_bank,
                chunk_size=batch_size,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                delay_between_chunks=delay
            )
        else:
            # Standard single-pass extraction
            # Combine text and table data for AI processing
            raw_data_text = raw_data_dict.get('raw_text', '')
            if 'formatted_tables' in raw_data_dict:
                raw_data_text += "\n\n" + raw_data_dict['formatted_tables']
            
            logger.info(f"Extracted {len(raw_data_text)} characters of raw data")
            
            # Step 3: AI-powered extraction
            logger.info("Step 3: Processing with AI engine...")
            extracted_data = self.ai_engine.extract_transactions(
                raw_data=raw_data_text,
                bank_name=detected_bank,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
        
        # Step 4: Validate and fix dates
        logger.info("Step 4: Validating and fixing dates...")
        extracted_data = self.ai_engine.validate_and_fix_dates(extracted_data)
        
        # Step 5: Income-aware categorization pipeline
        if categorize:
            transactions = extracted_data.get('transactions', [])
            if transactions:
                # Step 5a: Detect income transactions
                logger.info("Step 5a: Detecting income transactions...")
                income_transactions = self.income_detector.detect_income(transactions)
                extracted_data['income_transactions'] = income_transactions
                logger.info(f"Detected {len(income_transactions)} income transactions")
                
                # Step 5b: Group transactions into periods
                logger.info("Step 5b: Grouping transactions into periods...")
                periods = self.period_analyzer.group_into_periods(transactions, income_transactions)
                extracted_data['income_periods'] = periods
                logger.info(f"Created {len(periods)} periods")
                
                # Step 5c: Categorize transactions with period context
                logger.info("Step 5c: Categorizing transactions with period context...")
                all_categorized_transactions = []
                
                for period in periods:
                    period_txns = period.get('transactions', [])
                    if not period_txns:
                        continue
                    
                    # Create period context for categorization
                    period_context = {
                        'period_id': period.get('period_id', 'unknown'),
                        'income_amount': period.get('income_amount', 0.0),
                        'total_expenses_so_far': 0.0
                    }
                    
                    # Categorize transactions in this period
                    categorized_period_txns = self.category_engine.categorize_transactions(
                        transactions=period_txns,
                        batch_size=50,
                        temperature=Config.TEMPERATURE,
                        max_tokens=Config.MAX_TOKENS,
                        delay_between_batches=Config.BATCH_DELAY,
                        period_context=period_context
                    )
                    
                    # Update period with categorized transactions
                    period['transactions'] = categorized_period_txns
                    all_categorized_transactions.extend(categorized_period_txns)
                
                extracted_data['transactions'] = all_categorized_transactions
                logger.info(f"Categorized {len(all_categorized_transactions)} transactions across {len(periods)} periods")
                
                # Step 5d: Validate categorizations
                logger.info("Step 5d: Validating categorizations...")
                validation_results = self.validator.validate_periods(periods)
                extracted_data['validation_warnings'] = validation_results.get('warnings', [])
                extracted_data['validation_suspicious_transactions'] = validation_results.get('suspicious_transactions', [])
                logger.info(f"Validation found {len(validation_results.get('warnings', []))} warnings and {len(validation_results.get('suspicious_transactions', []))} suspicious transactions")
                
                # Step 5e: Re-categorize suspicious transactions
                if validation_results.get('suspicious_transactions'):
                    logger.info("Step 5e: Re-categorizing suspicious transactions...")
                    suspicious_txns = validation_results.get('suspicious_transactions', [])
                    
                    # Group suspicious transactions by period
                    suspicious_by_period = {}
                    for txn_info in suspicious_txns:
                        period_id = txn_info.get('period_id')
                        if period_id not in suspicious_by_period:
                            suspicious_by_period[period_id] = []
                        # Find the actual transaction
                        txn_id = txn_info.get('transaction_id')
                        for period in periods:
                            if period.get('period_id') == period_id:
                                for txn in period.get('transactions', []):
                                    if txn.get('transaction_id') == txn_id:
                                        suspicious_by_period[period_id].append(txn)
                                        break
                    
                    # Re-categorize by period
                    for period_id, suspicious_list in suspicious_by_period.items():
                        period = next((p for p in periods if p.get('period_id') == period_id), None)
                        if period:
                            re_categorized = self.validator.re_categorize_suspicious(
                                suspicious_list,
                                period
                            )
                            
                            # Update transactions in period
                            for recat_txn in re_categorized:
                                txn_id = recat_txn.get('transaction_id')
                                for i, txn in enumerate(period.get('transactions', [])):
                                    if txn.get('transaction_id') == txn_id:
                                        period['transactions'][i] = recat_txn
                                        # Also update in all_categorized_transactions
                                        for j, all_txn in enumerate(all_categorized_transactions):
                                            if all_txn.get('transaction_id') == txn_id:
                                                all_categorized_transactions[j] = recat_txn
                                                break
                                        break
                    
                    logger.info(f"Re-categorized {len(suspicious_txns)} suspicious transactions")
                
                # Update periods in extracted_data
                extracted_data['income_periods'] = periods
                extracted_data['transactions'] = all_categorized_transactions
                
                # Add categorization summary for analysis
                extracted_data['categorization_summary'] = self._generate_categorization_summary(all_categorized_transactions)
                
                # Add period-based summary
                extracted_data['period_summary'] = self._generate_period_summary(periods)
                
            else:
                logger.warning("No transactions to categorize")
        else:
            logger.info("Step 5: Skipping categorization (--no-categorize flag set)")
        
        # Add file metadata
        extracted_data['source_file'] = {
            'filename': file_path.name,
            'filepath': str(file_path),
            'file_type': suffix[1:],
            'file_size_bytes': file_path.stat().st_size,
            'processed_at': datetime.now(datetime.UTC).isoformat()
        }
        
        # Add bank detection info
        extracted_data['bank_detection'] = {
            'detected_bank': detected_bank,
            'confidence': confidence,
            'detection_method': 'automatic'
        }
        
        logger.info(f"Extraction complete: {len(extracted_data.get('transactions', []))} transactions extracted")
        
        return extracted_data
    
    def _generate_categorization_summary(self, transactions: list) -> dict:
        """
        Generate a summary of categorized transactions for analysis
        
        Args:
            transactions: List of categorized transactions
            
        Returns:
            Summary dictionary with category statistics
        """
        from collections import defaultdict
        
        summary = {
            'total_transactions': len(transactions),
            'categories': defaultdict(lambda: {'count': 0, 'total_amount': 0.0, 'subcategories': defaultdict(lambda: {'count': 0, 'total_amount': 0.0})}),
            'by_type': {
                'debit': {'count': 0, 'total_amount': 0.0},
                'credit': {'count': 0, 'total_amount': 0.0}
            }
        }
        
        for txn in transactions:
            category = txn.get('category', 'Other')
            subcategory = txn.get('subcategory', 'Uncategorized')
            amount = abs(float(txn.get('amount', 0)))
            txn_type = txn.get('transaction_type', 'debit')
            
            # Update category stats
            summary['categories'][category]['count'] += 1
            summary['categories'][category]['total_amount'] += amount
            summary['categories'][category]['subcategories'][subcategory]['count'] += 1
            summary['categories'][category]['subcategories'][subcategory]['total_amount'] += amount
            
            # Update type stats
            summary['by_type'][txn_type]['count'] += 1
            summary['by_type'][txn_type]['total_amount'] += amount
        
        # Convert defaultdicts to regular dicts for JSON serialization
        summary['categories'] = {
            cat: {
                'count': stats['count'],
                'total_amount': round(stats['total_amount'], 2),
                'subcategories': {
                    subcat: {
                        'count': sub_stats['count'],
                        'total_amount': round(sub_stats['total_amount'], 2)
                    }
                    for subcat, sub_stats in stats['subcategories'].items()
                }
            }
            for cat, stats in summary['categories'].items()
        }
        
        # Round type totals
        summary['by_type']['debit']['total_amount'] = round(summary['by_type']['debit']['total_amount'], 2)
        summary['by_type']['credit']['total_amount'] = round(summary['by_type']['credit']['total_amount'], 2)
        
        return summary
    
    def _generate_period_summary(self, periods: list) -> dict:
        """
        Generate a summary of periods for analysis
        
        Args:
            periods: List of period dictionaries
            
        Returns:
            Summary dictionary with period statistics
        """
        summary = {
            'total_periods': len(periods),
            'total_income': sum(p.get('income_amount', 0.0) for p in periods),
            'total_expenses': sum(p.get('total_expenses', 0.0) for p in periods),
            'periods': []
        }
        
        for period in periods:
            period_summary = {
                'period_id': period.get('period_id', 'unknown'),
                'start_date': str(period.get('start_date', '')) if period.get('start_date') else None,
                'end_date': str(period.get('end_date', '')) if period.get('end_date') else None,
                 'income_amount': round(period.get('income_amount', 0.0), 2),
                 'starting_balance': round(period.get('starting_balance', 0.0), 2) if period.get('starting_balance') is not None else None,
                 'total_expenses': round(period.get('total_expenses', 0.0), 2),
                 'ending_balance': round(period.get('ending_balance', 0.0), 2) if period.get('ending_balance') is not None else None,
                 'remaining_from_income': round(period.get('remaining_from_income', 0.0), 2),
                 'transaction_count': len(period.get('transactions', []))
            }
            summary['periods'].append(period_summary)
        
        return summary
    
    def save_to_json(self, data: dict, output_path: str | Path):
        """
        Save extracted data to JSON file
        
        Args:
            data: Extracted transaction data
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved extracted data to: {output_path}")
    
    def extract_and_save(self, file_path: str | Path, output_dir: Optional[str | Path] = None) -> Path:
        """
        Extract transactions and save to JSON
        
        Args:
            file_path: Path to bank statement file
            output_dir: Directory to save output (default: config OUTPUT_DIR)
            
        Returns:
            Path to saved JSON file
        """
        file_path = Path(file_path)
        
        # Extract data
        extracted_data = self.extract_from_file(file_path)
        
        # Determine output path
        if output_dir is None:
            output_dir = Config.OUTPUT_DIR
        else:
            output_dir = Path(output_dir)
        
        output_filename = f"{file_path.stem}_extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = output_dir / output_filename
        
        # Save to file
        self.save_to_json(extracted_data, output_path)
        
        return output_path


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Extract transactions from Turkish bank statements',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --file statement.pdf
  python main.py --file statement.xlsx --output ./my_output/
  python main.py --file statement.csv --provider anthropic
  python main.py --list-banks
        """
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='Path to bank statement file (PDF, XLSX, XLS, or CSV)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output directory for JSON files (default: ./output/)'
    )
    
    parser.add_argument(
        '--list-banks',
        action='store_true',
        help='List supported Turkish banks'
    )
    
    parser.add_argument(
        '--no-batch',
        action='store_true',
        help='Disable automatic batch processing for large files'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=30,
        help='Number of transactions per batch (default: 30)'
    )
    
    parser.add_argument(
        '--batch-delay',
        type=float,
        help='Seconds to wait between batch requests (default: 2.5, based on Groq 30 RPM limit)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--no-categorize',
        action='store_true',
        help='Skip transaction categorization step'
    )
    
    args = parser.parse_args()
    
    # Set debug level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # List banks
    if args.list_banks:
        banks = BankDetector.list_supported_banks()
        print("\nSupported Turkish Banks:")
        print("=" * 50)
        for i, bank in enumerate(banks, 1):
            print(f"{i:2d}. {bank}")
        print("=" * 50)
        print(f"Total: {len(banks)} banks\n")
        return 0
    
    # Check for file argument
    if not args.file:
        parser.print_help()
        print("\nError: --file argument is required (or use --list-banks)")
        return 1
    
    try:
        # Initialize extractor
        extractor = TransactionExtractor()
        
        # Extract with batch settings
        use_batch = not args.no_batch
        should_categorize = not args.no_categorize
        extracted_data = extractor.extract_from_file(
            file_path=args.file,
            auto_batch=use_batch,
            batch_size=args.batch_size,
            batch_delay=args.batch_delay,
            categorize=should_categorize
        )
        
        # Determine output path
        output_dir = Path(args.output) if args.output else Config.OUTPUT_DIR
        output_filename = f"{Path(args.file).stem}_extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = output_dir / output_filename
        
        # Save to file
        extractor.save_to_json(extracted_data, output_path)
        
        print("\n" + "=" * 70)
        print("EXTRACTION SUCCESSFUL!")
        print("=" * 70)
        print(f"Input file:  {args.file}")
        print(f"Output file: {output_path}")
        print("=" * 70)
        
        # Show summary
        print("\nSummary:")
        print(f"  Bank:         {extracted_data.get('bank_name', 'Unknown')}")
        print(f"  Transactions: {len(extracted_data.get('transactions', []))}")
        print(f"  Currency:     {extracted_data.get('currency', 'TRY')}")
        
        # Show batch info if used
        metadata = extracted_data.get('extraction_metadata', {})
        if metadata.get('batch_processing'):
            print(f"  Batch Mode:   Yes ({metadata.get('total_chunks')} chunks, {metadata.get('chunk_size')} per chunk)")
        
        if extracted_data.get('statement_period_start') and extracted_data.get('statement_period_end'):
            print(f"  Period:       {extracted_data['statement_period_start']} to {extracted_data['statement_period_end']}")
        
        # Show period summary if available
        if 'period_summary' in extracted_data:
            period_summary = extracted_data['period_summary']
            print(f"\n  Income Periods:")
            print(f"    Total Periods: {period_summary.get('total_periods', 0)}")
            print(f"    Total Income:  {period_summary.get('total_income', 0):,.2f} {extracted_data.get('currency', 'TRY')}")
            print(f"    Total Expenses: {period_summary.get('total_expenses', 0):,.2f} {extracted_data.get('currency', 'TRY')}")
            
            # Show period details
            periods = period_summary.get('periods', [])
            if periods:
                print(f"\n  Period Details:")
                for period in periods[:5]:  # Show first 5 periods
                    period_id = period.get('period_id', 'unknown')
                    income = period.get('income_amount', 0) or 0
                    start_balance = period.get('starting_balance')
                    expenses = period.get('total_expenses', 0) or 0
                    end_balance = period.get('ending_balance')
                    remaining = period.get('remaining_from_income', 0) or 0
                    print(f"    {period_id}:")
                    if start_balance is not None:
                        print(f"      Income: {income:,.2f} → Starting Balance: {start_balance:,.2f}")
                    else:
                        print(f"      Income: {income:,.2f}")
                    if end_balance is not None:
                        print(f"      Expenses: {expenses:,.2f} → Ending Balance: {end_balance:,.2f} (Remaining: {remaining:,.2f})")
                    else:
                        print(f"      Expenses: {expenses:,.2f} (Remaining: {remaining:,.2f})")
                    print(f"      Transactions: {period.get('transaction_count', 0)}")
        
        # Show categorization summary if available
        if 'categorization_summary' in extracted_data:
            cat_summary = extracted_data['categorization_summary']
            print(f"\n  Categorization:")
            print(f"    Categories: {len(cat_summary.get('categories', {}))}")
            print(f"    Total Debits:  {cat_summary.get('by_type', {}).get('debit', {}).get('total_amount', 0):,.2f} {extracted_data.get('currency', 'TRY')}")
            print(f"    Total Credits: {cat_summary.get('by_type', {}).get('credit', {}).get('total_amount', 0):,.2f} {extracted_data.get('currency', 'TRY')}")
            
            # Show top categories
            categories = cat_summary.get('categories', {})
            if categories:
                sorted_cats = sorted(categories.items(), key=lambda x: x[1]['total_amount'], reverse=True)
                print(f"\n  Top Categories by Amount:")
                for i, (cat, stats) in enumerate(sorted_cats[:5], 1):
                    print(f"    {i}. {cat}: {stats['total_amount']:,.2f} {extracted_data.get('currency', 'TRY')} ({stats['count']} transactions)")
        
        # Show validation warnings if any
        if 'validation_warnings' in extracted_data and extracted_data['validation_warnings']:
            warnings = extracted_data['validation_warnings']
            print(f"\n  Validation Warnings: {len(warnings)}")
            for warning in warnings[:3]:  # Show first 3 warnings
                w_type = warning.get('type', 'unknown')
                period_id = warning.get('period_id', 'unknown')
                print(f"    - {w_type} in {period_id}")
        
        print("\n")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Configuration or validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=args.debug)
        return 1


if __name__ == '__main__':
    sys.exit(main())

