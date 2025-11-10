"""
CSV Extractor for bank statements
Extracts data from CSV files
"""
import pandas as pd
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CSVExtractor:
    """Extract data from CSV bank statements"""
    
    def __init__(self, file_path: str | Path, encoding: str = 'utf-8'):
        """
        Initialize CSV extractor
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding (default: utf-8, common alternatives: iso-8859-9 for Turkish)
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        if not self.file_path.suffix.lower() == '.csv':
            raise ValueError(f"File must be a CSV: {file_path}")
        
        self.encoding = encoding
        self._detect_encoding()
    
    def _detect_encoding(self):
        """Try to detect the correct encoding"""
        encodings_to_try = ['utf-8', 'iso-8859-9', 'windows-1254', 'latin1']
        
        for enc in encodings_to_try:
            try:
                with open(self.file_path, 'r', encoding=enc) as f:
                    f.read(1024)  # Try to read first 1KB
                self.encoding = enc
                logger.info(f"Detected encoding: {enc}")
                return
            except UnicodeDecodeError:
                continue
        
        # If all fail, use utf-8 with error handling
        self.encoding = 'utf-8'
        logger.warning(f"Could not detect encoding, using utf-8 with error handling")
    
    def _detect_delimiter(self) -> str:
        """
        Detect CSV delimiter
        
        Returns:
            Detected delimiter
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding, errors='ignore') as f:
                sample = f.read(4096)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                logger.info(f"Detected delimiter: {repr(delimiter)}")
                return delimiter
        except Exception as e:
            logger.warning(f"Could not detect delimiter: {e}, using comma")
            return ','
    
    def extract_as_dataframe(self, delimiter: Optional[str] = None) -> pd.DataFrame:
        """
        Extract CSV as pandas DataFrame
        
        Args:
            delimiter: CSV delimiter (auto-detect if None)
            
        Returns:
            DataFrame with CSV data
        """
        try:
            if delimiter is None:
                delimiter = self._detect_delimiter()
            
            df = pd.read_csv(
                self.file_path,
                delimiter=delimiter,
                encoding=self.encoding,
                encoding_errors='ignore'
            )
            
            logger.info(f"Extracted CSV with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error extracting CSV as DataFrame: {e}")
            raise
    
    def extract_as_text(self, delimiter: Optional[str] = None) -> str:
        """
        Extract CSV data as formatted text
        
        Args:
            delimiter: CSV delimiter (auto-detect if None)
            
        Returns:
            Formatted text representation
        """
        try:
            df = self.extract_as_dataframe(delimiter)
            
            # Convert DataFrame to text
            text_lines = []
            
            # Add header
            headers = " | ".join([str(col) for col in df.columns])
            text_lines.append(headers)
            text_lines.append("-" * len(headers))
            
            # Add rows
            for _, row in df.iterrows():
                row_text = " | ".join([str(val) if pd.notna(val) else "" for val in row])
                text_lines.append(row_text)
            
            return "\n".join(text_lines)
        except Exception as e:
            logger.error(f"Error extracting as text: {e}")
            raise
    
    def extract_as_records(self, delimiter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract CSV data as list of dictionaries
        
        Args:
            delimiter: CSV delimiter (auto-detect if None)
            
        Returns:
            List of dictionaries (one per row)
        """
        try:
            df = self.extract_as_dataframe(delimiter)
            # Replace NaN with None for better JSON serialization
            df = df.where(pd.notna(df), None)
            records = df.to_dict('records')
            logger.info(f"Extracted {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"Error extracting as records: {e}")
            raise
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract CSV file metadata
        
        Returns:
            Dictionary with metadata
        """
        try:
            delimiter = self._detect_delimiter()
            df = self.extract_as_dataframe(delimiter)
            
            metadata = {
                'file_name': self.file_path.name,
                'file_size_bytes': self.file_path.stat().st_size,
                'encoding': self.encoding,
                'delimiter': delimiter,
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist()
            }
            
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            raise
    
    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all data from CSV file
        
        Returns:
            Dictionary with all extracted data
        """
        logger.info(f"Starting full extraction of CSV: {self.file_path.name}")
        
        df = self.extract_as_dataframe()
        metadata = self.extract_metadata()
        
        return {
            'data': df.where(pd.notna(df), None).to_dict('records'),
            'metadata': metadata
        }
    
    def extract_structured(self) -> Dict[str, Any]:
        """
        Extract data in a structured format optimized for AI processing
        
        Returns:
            Dictionary with structured data
        """
        df = self.extract_as_dataframe()
        text_representation = self.extract_as_text()
        records = self.extract_as_records()
        metadata = self.extract_metadata()
        
        return {
            'raw_text': text_representation,
            'records': records,
            'columns': df.columns.tolist(),
            'row_count': len(df),
            'metadata': metadata,
            'file_path': str(self.file_path),
            'file_type': 'csv'
        }
    
    @staticmethod
    def is_valid_csv(file_path: str | Path) -> bool:
        """
        Check if file is a valid CSV
        
        Args:
            file_path: Path to file
            
        Returns:
            True if valid CSV, False otherwise
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
            if not file_path.suffix.lower() == '.csv':
                return False
            
            # Try to read first few lines
            pd.read_csv(file_path, nrows=5)
            return True
        except Exception:
            return False

