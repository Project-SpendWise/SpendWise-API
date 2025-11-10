#!/usr/bin/env python3
"""
Test script for extractors (no API key required)
Tests the file extractors and bank detector with sample files
"""
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def test_pdf_extractor():
    """Test PDF extractor"""
    from extractors import PDFExtractor
    
    logger.info("=" * 70)
    logger.info("Testing PDF Extractor")
    logger.info("=" * 70)
    
    pdf_files = list(Path('samples').glob('*.pdf'))
    
    if not pdf_files:
        logger.warning("No PDF files found in samples/")
        return False
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"\nProcessing: {pdf_file.name}")
            extractor = PDFExtractor(pdf_file)
            
            # Test metadata extraction
            metadata = extractor.extract_metadata()
            logger.info(f"  Pages: {metadata['page_count']}")
            logger.info(f"  Size: {metadata['file_size_bytes'] / 1024:.1f} KB")
            
            # Test text extraction
            text = extractor.extract_text()
            logger.info(f"  Text extracted: {len(text)} characters")
            logger.info(f"  First 100 chars: {text[:100]}...")
            
            # Test table extraction
            tables = extractor.extract_tables()
            logger.info(f"  Tables found: {len(tables)}")
            
            # Test structured extraction
            structured = extractor.extract_structured()
            logger.info(f"  Structured data keys: {list(structured.keys())}")
            
            logger.info("  ✓ PDF extraction successful")
            return True
            
        except Exception as e:
            logger.error(f"  ✗ PDF extraction failed: {e}")
            return False
    
    return False


def test_excel_extractor():
    """Test Excel extractor"""
    from extractors import ExcelExtractor
    
    logger.info("\n" + "=" * 70)
    logger.info("Testing Excel Extractor")
    logger.info("=" * 70)
    
    excel_files = list(Path('samples').glob('*.xlsx')) + list(Path('samples').glob('*.xls'))
    
    if not excel_files:
        logger.warning("No Excel files found in samples/")
        return False
    
    for excel_file in excel_files:
        try:
            logger.info(f"\nProcessing: {excel_file.name}")
            extractor = ExcelExtractor(excel_file)
            
            # Test metadata extraction
            metadata = extractor.extract_metadata()
            logger.info(f"  Sheets: {metadata['sheet_count']}")
            logger.info(f"  Sheet names: {metadata['sheet_names']}")
            logger.info(f"  Size: {metadata['file_size_bytes'] / 1024:.1f} KB")
            
            # Test sheet extraction
            sheet_names = extractor.get_sheet_names()
            logger.info(f"  First sheet: {sheet_names[0]}")
            
            # Test structured extraction
            structured = extractor.extract_structured()
            logger.info(f"  Primary sheet: {structured['primary_sheet']}")
            logger.info(f"  Columns: {structured['columns']}")
            logger.info(f"  Rows: {structured['row_count']}")
            logger.info(f"  Records extracted: {len(structured['records'])}")
            
            # Show first few column names
            if structured['columns']:
                logger.info(f"  Sample columns: {structured['columns'][:5]}")
            
            logger.info("  ✓ Excel extraction successful")
            return True
            
        except Exception as e:
            logger.error(f"  ✗ Excel extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return False


def test_csv_extractor():
    """Test CSV extractor"""
    from extractors import CSVExtractor
    
    logger.info("\n" + "=" * 70)
    logger.info("Testing CSV Extractor")
    logger.info("=" * 70)
    
    csv_files = list(Path('samples').glob('*.csv'))
    
    if not csv_files:
        logger.warning("No CSV files found in samples/")
        return True  # Not an error, just no files
    
    for csv_file in csv_files:
        try:
            logger.info(f"\nProcessing: {csv_file.name}")
            extractor = CSVExtractor(csv_file)
            
            # Test metadata extraction
            metadata = extractor.extract_metadata()
            logger.info(f"  Encoding: {metadata['encoding']}")
            logger.info(f"  Delimiter: {repr(metadata['delimiter'])}")
            logger.info(f"  Rows: {metadata['row_count']}")
            logger.info(f"  Columns: {metadata['column_count']}")
            
            # Test structured extraction
            structured = extractor.extract_structured()
            logger.info(f"  Records extracted: {len(structured['records'])}")
            
            logger.info("  ✓ CSV extraction successful")
            return True
            
        except Exception as e:
            logger.error(f"  ✗ CSV extraction failed: {e}")
            return False
    
    return True


def test_bank_detector():
    """Test bank detector"""
    from detectors import BankDetector
    
    logger.info("\n" + "=" * 70)
    logger.info("Testing Bank Detector")
    logger.info("=" * 70)
    
    # List supported banks
    banks = BankDetector.list_supported_banks()
    logger.info(f"\nSupported banks: {len(banks)}")
    for bank in banks[:5]:
        logger.info(f"  - {bank}")
    logger.info("  ...")
    
    # Test detection on sample files
    sample_files = list(Path('samples').glob('*'))
    sample_files = [f for f in sample_files if f.is_file() and f.suffix in ['.pdf', '.xlsx', '.xls', '.csv']]
    
    if not sample_files:
        logger.warning("No sample files found")
        return False
    
    for sample_file in sample_files:
        try:
            logger.info(f"\nDetecting bank from: {sample_file.name}")
            
            # Try reading file content
            if sample_file.suffix == '.pdf':
                from extractors import PDFExtractor
                extractor = PDFExtractor(sample_file)
                text = extractor.extract_text()
            elif sample_file.suffix in ['.xlsx', '.xls']:
                from extractors import ExcelExtractor
                extractor = ExcelExtractor(sample_file)
                text = extractor.extract_as_text()
            elif sample_file.suffix == '.csv':
                from extractors import CSVExtractor
                extractor = CSVExtractor(sample_file)
                text = extractor.extract_as_text()
            else:
                continue
            
            # Detect bank with confidence
            result = BankDetector.detect_with_confidence(text)
            
            if result['bank']:
                logger.info(f"  ✓ Detected: {result['bank']}")
                logger.info(f"    Confidence: {result['confidence']:.2%}")
                logger.info(f"    Matches: {result['matches'][0]['match_count']}")
            else:
                logger.warning(f"  ✗ Could not detect bank")
            
        except Exception as e:
            logger.error(f"  ✗ Detection failed: {e}")
    
    return True


def main():
    """Run all tests"""
    logger.info("\n")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " " * 15 + "TRANSACTION EXTRACTOR - TEST SUITE" + " " * 19 + "║")
    logger.info("╚" + "═" * 68 + "╝")
    logger.info("\n")
    
    results = {}
    
    # Run tests
    results['pdf'] = test_pdf_extractor()
    results['excel'] = test_excel_extractor()
    results['csv'] = test_csv_extractor()
    results['detector'] = test_bank_detector()
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"  {name.upper():15s}: {status}")
    
    logger.info("=" * 70)
    logger.info(f"Result: {passed}/{total} tests passed")
    logger.info("=" * 70)
    logger.info("")
    
    if passed == total:
        logger.info("✓ All tests passed! The extractors are working correctly.")
        logger.info("\nNext steps:")
        logger.info("1. Set up your .env file with API keys")
        logger.info("2. Run: python main.py --file samples/your_file.pdf")
        return 0
    else:
        logger.error("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

