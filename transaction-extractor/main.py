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
from ai import AIExtractionEngine
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
        
        logger.info(f"Initialized TransactionExtractor with Groq model: {ai_config['model']}")
    
    def extract_from_file(self, file_path: str | Path, auto_batch: bool = True, batch_size: int = 30, batch_delay: float = None) -> dict:
        """
        Extract transactions from a file with automatic batch processing for large files
        
        Args:
            file_path: Path to the bank statement file
            auto_batch: Automatically use batch processing for large files
            batch_size: Number of transactions per batch
            batch_delay: Seconds to wait between batches (None = use config default)
            
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
        
        # Add file metadata
        extracted_data['source_file'] = {
            'filename': file_path.name,
            'filepath': str(file_path),
            'file_type': suffix[1:],
            'file_size_bytes': file_path.stat().st_size,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        # Add bank detection info
        extracted_data['bank_detection'] = {
            'detected_bank': detected_bank,
            'confidence': confidence,
            'detection_method': 'automatic'
        }
        
        logger.info(f"Extraction complete: {len(extracted_data.get('transactions', []))} transactions extracted")
        
        return extracted_data
    
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
        extracted_data = extractor.extract_from_file(
            file_path=args.file,
            auto_batch=use_batch,
            batch_size=args.batch_size,
            batch_delay=args.batch_delay
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

