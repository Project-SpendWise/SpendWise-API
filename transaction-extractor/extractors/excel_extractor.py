"""
Excel Extractor for bank statements
Extracts data from XLSX and XLS files
"""
import pandas as pd
import openpyxl
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Patch openpyxl to handle corrupted styling in Excel files
def _patch_openpyxl():
    """Patch openpyxl Fill class to ignore styling errors"""
    import openpyxl.styles.fills
    original_fill_init = openpyxl.styles.fills.Fill.__init__
    
    def patched_fill_init(self, *args, **kwargs):
        try:
            original_fill_init(self, *args, **kwargs)
        except TypeError:
            # If styling fails, create empty Fill
            self.patternType = None
            self.fgColor = None
            self.bgColor = None
    
    openpyxl.styles.fills.Fill.__init__ = patched_fill_init
    logger.debug("Applied openpyxl styling patch")

# Apply patch on module import
_patch_openpyxl()


class ExcelExtractor:
    """Extract data from Excel bank statements"""
    
    def __init__(self, file_path: str | Path):
        """
        Initialize Excel extractor
        
        Args:
            file_path: Path to Excel file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        suffix = self.file_path.suffix.lower()
        if suffix not in ['.xlsx', '.xls']:
            raise ValueError(f"File must be an Excel file (.xlsx or .xls): {file_path}")
        
        self.file_type = suffix[1:]  # Remove the dot
    
    def get_sheet_names(self) -> List[str]:
        """
        Get list of sheet names in the workbook
        
        Returns:
            List of sheet names
        """
        try:
            # Use pandas to get sheet names (more robust)
            xls = pd.ExcelFile(self.file_path, engine='openpyxl' if self.file_type == 'xlsx' else 'xlrd')
            return xls.sheet_names
        except Exception as e:
            logger.error(f"Error getting sheet names: {e}")
            raise
    
    def extract_sheet_as_dataframe(self, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Extract a specific sheet as pandas DataFrame
        
        Args:
            sheet_name: Name of sheet to extract (None for first sheet)
            
        Returns:
            DataFrame with sheet data
        """
        try:
            # Try different engines for better compatibility
            engines = ['openpyxl', 'pyxlsb'] if self.file_type == 'xlsx' else ['xlrd']
            
            last_error = None
            for engine in engines:
                try:
                    df = pd.read_excel(
                        self.file_path,
                        sheet_name=sheet_name or 0,
                        engine=engine
                    )
                    logger.info(f"Extracted sheet with shape: {df.shape} using engine: {engine}")
                    return df
                except Exception as e:
                    last_error = e
                    logger.debug(f"Engine {engine} failed: {e}")
                    continue
            
            # If all engines fail, raise the last error
            raise last_error if last_error else Exception("Failed to read Excel file")
            
        except Exception as e:
            logger.error(f"Error extracting sheet as DataFrame: {e}")
            raise
    
    def extract_all_sheets_as_dataframes(self) -> Dict[str, pd.DataFrame]:
        """
        Extract all sheets as DataFrames
        
        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        try:
            # Try different engines for better compatibility
            engines = ['openpyxl', 'pyxlsb'] if self.file_type == 'xlsx' else ['xlrd']
            
            last_error = None
            for engine in engines:
                try:
                    all_sheets = pd.read_excel(
                        self.file_path,
                        sheet_name=None,  # Load all sheets
                        engine=engine
                    )
                    logger.info(f"Extracted {len(all_sheets)} sheets using engine: {engine}")
                    return all_sheets
                except Exception as e:
                    last_error = e
                    logger.debug(f"Engine {engine} failed: {e}")
                    continue
            
            # If all engines fail, raise the last error
            raise last_error if last_error else Exception("Failed to read Excel file")
            
        except Exception as e:
            logger.error(f"Error extracting all sheets: {e}")
            raise
    
    def extract_as_text(self, sheet_name: Optional[str] = None) -> str:
        """
        Extract sheet data as formatted text
        
        Args:
            sheet_name: Name of sheet to extract (None for first sheet)
            
        Returns:
            Formatted text representation
        """
        try:
            df = self.extract_sheet_as_dataframe(sheet_name)
            
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
    
    def extract_as_records(self, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract sheet data as list of dictionaries
        
        Args:
            sheet_name: Name of sheet to extract (None for first sheet)
            
        Returns:
            List of dictionaries (one per row)
        """
        try:
            df = self.extract_sheet_as_dataframe(sheet_name)
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
        Extract Excel file metadata
        
        Returns:
            Dictionary with metadata
        """
        try:
            sheet_names = self.get_sheet_names()
            
            metadata = {
                'file_name': self.file_path.name,
                'file_size_bytes': self.file_path.stat().st_size,
                'file_type': self.file_type,
                'sheet_names': sheet_names,
                'sheet_count': len(sheet_names)
            }
            
            # Get first sheet dimensions
            df = self.extract_sheet_as_dataframe()
            metadata['first_sheet_rows'] = len(df)
            metadata['first_sheet_columns'] = len(df.columns)
            metadata['columns'] = df.columns.tolist()
            
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            raise
    
    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all data from Excel file
        
        Returns:
            Dictionary with all extracted data
        """
        logger.info(f"Starting full extraction of Excel: {self.file_path.name}")
        
        all_sheets = self.extract_all_sheets_as_dataframes()
        metadata = self.extract_metadata()
        
        # Convert DataFrames to records for each sheet
        sheets_data = {}
        for sheet_name, df in all_sheets.items():
            sheets_data[sheet_name] = {
                'data': df.where(pd.notna(df), None).to_dict('records'),
                'shape': df.shape,
                'columns': df.columns.tolist()
            }
        
        return {
            'sheets': sheets_data,
            'metadata': metadata
        }
    
    def extract_structured(self) -> Dict[str, Any]:
        """
        Extract data in a structured format optimized for AI processing
        
        Returns:
            Dictionary with structured data
        """
        # Get primary sheet (usually first one or largest one)
        all_sheets = self.extract_all_sheets_as_dataframes()
        
        # Find the sheet with most data (likely the transaction sheet)
        primary_sheet_name = max(all_sheets.keys(), key=lambda k: len(all_sheets[k]))
        primary_df = all_sheets[primary_sheet_name]
        
        # Format as text for AI
        text_representation = self.extract_as_text(primary_sheet_name)
        
        # Also get as records
        records = self.extract_as_records(primary_sheet_name)
        
        metadata = self.extract_metadata()
        
        return {
            'raw_text': text_representation,
            'records': records,
            'primary_sheet': primary_sheet_name,
            'columns': primary_df.columns.tolist(),
            'row_count': len(primary_df),
            'all_sheet_names': list(all_sheets.keys()),
            'metadata': metadata,
            'file_path': str(self.file_path),
            'file_type': 'excel'
        }
    
    @staticmethod
    def is_valid_excel(file_path: str | Path) -> bool:
        """
        Check if file is a valid Excel file
        
        Args:
            file_path: Path to file
            
        Returns:
            True if valid Excel file, False otherwise
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
            
            suffix = file_path.suffix.lower()
            if suffix not in ['.xlsx', '.xls']:
                return False
            
            # Try to open it
            pd.read_excel(
                file_path,
                nrows=1,
                engine='openpyxl' if suffix == '.xlsx' else 'xlrd'
            )
            return True
        except Exception:
            return False

