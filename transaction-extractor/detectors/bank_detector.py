"""
Bank Detector
Automatically identifies Turkish banks from file content
"""
import re
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class BankDetector:
    """Detect Turkish bank from file content"""
    
    # Turkish bank patterns with variations
    BANK_PATTERNS = {
        "Garanti BBVA": [
            r"Garanti\s+BBVA",
            r"Garanti\s+Bankası",
            r"GARANTIBBVA",
            r"T\.\s*Garanti",
        ],
        "İş Bankası": [
            r"İş\s+Bankası",
            r"Türkiye\s+İş\s+Bankası",
            r"ISBANK",
            r"T\.\s*İş\s*Bankası",
        ],
        "Yapı Kredi": [
            r"Yapı\s+Kredi",
            r"Yapı\s+ve\s+Kredi\s+Bankası",
            r"YAPIKREDI",
            r"YKB",
        ],
        "Akbank": [
            r"Akbank",
            r"AKBANK",
            r"T\.\s*Akbank",
        ],
        "Ziraat Bankası": [
            r"Ziraat\s+Bankası",
            r"T\.\s*C\.\s*Ziraat\s+Bankası",
            r"ZIRAATBANK",
        ],
        "Halkbank": [
            r"Halk\s+Bankası",
            r"Halkbank",
            r"T\.\s*C\.\s*Halkbank",
        ],
        "Vakıfbank": [
            r"Vakıfbank",
            r"Vakıf\s+Bank",
            r"T\.\s*Vakıflar\s+Bankası",
        ],
        "Denizbank": [
            r"Denizbank",
            r"Deniz\s+Bank",
        ],
        "QNB Finansbank": [
            r"QNB\s+Finansbank",
            r"Finansbank",
            r"QNB\s+Finans",
        ],
        "TEB": [
            r"TEB",
            r"Türk\s+Ekonomi\s+Bankası",
            r"T\.\s*Ekonomi\s+Bankası",
        ],
        "ING Bank": [
            r"ING\s+Bank",
            r"ING",
        ],
        "HSBC": [
            r"HSBC",
            r"HSBC\s+Bank",
        ],
        "Kuveyt Türk": [
            r"Kuveyt\s+Türk",
            r"KuveytTürk",
        ],
        "Albaraka Türk": [
            r"Albaraka\s+Türk",
            r"AlbarakaTürk",
        ],
    }
    
    @classmethod
    def detect_from_text(cls, text: str) -> Optional[str]:
        """
        Detect bank from text content
        
        Args:
            text: Text content from file
            
        Returns:
            Bank name if detected, None otherwise
        """
        if not text:
            return None
        
        # Convert to string if not already
        text = str(text)
        
        # Try each bank pattern
        for bank_name, patterns in cls.BANK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    logger.info(f"Detected bank: {bank_name} (pattern: {pattern})")
                    return bank_name
        
        logger.warning("Could not detect bank from text")
        return None
    
    @classmethod
    def detect_from_structured_data(cls, data: Dict[str, Any]) -> Optional[str]:
        """
        Detect bank from structured data (Excel/CSV records)
        
        Args:
            data: Structured data from file
            
        Returns:
            Bank name if detected, None otherwise
        """
        # Convert entire data structure to string and search
        text_representation = str(data)
        return cls.detect_from_text(text_representation)
    
    @classmethod
    def detect_from_file(cls, file_path: str | Path) -> Optional[str]:
        """
        Detect bank from file using appropriate extractor
        
        Args:
            file_path: Path to file
            
        Returns:
            Bank name if detected, None otherwise
        """
        from extractors import PDFExtractor, ExcelExtractor, CSVExtractor
        
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.pdf':
                extractor = PDFExtractor(file_path)
                text = extractor.extract_text()
                return cls.detect_from_text(text)
            
            elif suffix in ['.xlsx', '.xls']:
                extractor = ExcelExtractor(file_path)
                text = extractor.extract_as_text()
                return cls.detect_from_text(text)
            
            elif suffix == '.csv':
                extractor = CSVExtractor(file_path)
                text = extractor.extract_as_text()
                return cls.detect_from_text(text)
            
            else:
                logger.error(f"Unsupported file format: {suffix}")
                return None
                
        except Exception as e:
            logger.error(f"Error detecting bank from file: {e}")
            return None
    
    @classmethod
    def get_bank_info(cls, bank_name: str) -> Dict[str, Any]:
        """
        Get additional information about a bank
        
        Args:
            bank_name: Name of the bank
            
        Returns:
            Dictionary with bank information
        """
        # This could be extended with more bank-specific info
        return {
            'name': bank_name,
            'country': 'Turkey',
            'currency': 'TRY',
            'patterns': cls.BANK_PATTERNS.get(bank_name, [])
        }
    
    @classmethod
    def list_supported_banks(cls) -> List[str]:
        """
        Get list of supported Turkish banks
        
        Returns:
            List of bank names
        """
        return list(cls.BANK_PATTERNS.keys())
    
    @classmethod
    def add_bank_pattern(cls, bank_name: str, patterns: List[str]):
        """
        Add a new bank or additional patterns for existing bank
        
        Args:
            bank_name: Name of the bank
            patterns: List of regex patterns
        """
        if bank_name in cls.BANK_PATTERNS:
            cls.BANK_PATTERNS[bank_name].extend(patterns)
            logger.info(f"Added {len(patterns)} patterns to {bank_name}")
        else:
            cls.BANK_PATTERNS[bank_name] = patterns
            logger.info(f"Added new bank: {bank_name} with {len(patterns)} patterns")
    
    @classmethod
    def detect_with_confidence(cls, text: str) -> Dict[str, Any]:
        """
        Detect bank with confidence score
        
        Args:
            text: Text content from file
            
        Returns:
            Dictionary with bank name and confidence
        """
        if not text:
            return {'bank': None, 'confidence': 0.0, 'matches': []}
        
        text = str(text)
        matches = []
        
        # Try each bank pattern and count matches
        for bank_name, patterns in cls.BANK_PATTERNS.items():
            match_count = 0
            matched_patterns = []
            
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    match_count += len(found)
                    matched_patterns.append(pattern)
            
            if match_count > 0:
                matches.append({
                    'bank': bank_name,
                    'match_count': match_count,
                    'patterns': matched_patterns
                })
        
        if not matches:
            return {'bank': None, 'confidence': 0.0, 'matches': []}
        
        # Sort by match count
        matches.sort(key=lambda x: x['match_count'], reverse=True)
        
        # Best match
        best_match = matches[0]
        total_matches = sum(m['match_count'] for m in matches)
        confidence = best_match['match_count'] / total_matches if total_matches > 0 else 0.0
        
        return {
            'bank': best_match['bank'],
            'confidence': confidence,
            'matches': matches
        }

