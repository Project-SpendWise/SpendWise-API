"""
PDF Extractor for bank statements
Extracts text and tables from PDF files
"""
import pdfplumber
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract data from PDF bank statements"""
    
    def __init__(self, file_path: str | Path):
        """
        Initialize PDF extractor
        
        Args:
            file_path: Path to PDF file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        if not self.file_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF: {file_path}")
    
    def extract_text(self) -> str:
        """
        Extract all text from PDF
        
        Returns:
            Extracted text as string
        """
        try:
            text_content = []
            with pdfplumber.open(self.file_path) as pdf:
                logger.info(f"Opening PDF: {self.file_path.name}, Pages: {len(pdf.pages)}")
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"--- Page {i+1} ---\n{page_text}")
                        logger.debug(f"Extracted {len(page_text)} characters from page {i+1}")
            
            full_text = "\n\n".join(text_content)
            logger.info(f"Total text extracted: {len(full_text)} characters")
            return full_text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_tables(self) -> List[List[List[Any]]]:
        """
        Extract all tables from PDF
        
        Returns:
            List of tables (each table is a list of rows)
        """
        try:
            all_tables = []
            with pdfplumber.open(self.file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    if tables:
                        logger.debug(f"Found {len(tables)} table(s) on page {i+1}")
                        for table in tables:
                            if table and len(table) > 0:
                                all_tables.append(table)
                                logger.debug(f"Table with {len(table)} rows extracted")
            
            logger.info(f"Total tables extracted: {len(all_tables)}")
            return all_tables
        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {e}")
            raise
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract PDF metadata
        
        Returns:
            Dictionary with metadata
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                metadata = {
                    'page_count': len(pdf.pages),
                    'file_name': self.file_path.name,
                    'file_size_bytes': self.file_path.stat().st_size,
                    'pdf_metadata': pdf.metadata or {}
                }
                
                # Add first page dimensions if available
                if pdf.pages:
                    first_page = pdf.pages[0]
                    metadata['page_width'] = first_page.width
                    metadata['page_height'] = first_page.height
                
                return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from PDF: {e}")
            raise
    
    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all data from PDF (text, tables, and metadata)
        
        Returns:
            Dictionary with all extracted data
        """
        logger.info(f"Starting full extraction of PDF: {self.file_path.name}")
        
        return {
            'text': self.extract_text(),
            'tables': self.extract_tables(),
            'metadata': self.extract_metadata()
        }
    
    def extract_structured(self) -> Dict[str, Any]:
        """
        Extract data in a structured format optimized for AI processing
        
        Returns:
            Dictionary with structured data
        """
        text = self.extract_text()
        tables = self.extract_tables()
        metadata = self.extract_metadata()
        
        # Format tables as text for easier AI processing
        formatted_tables = []
        for i, table in enumerate(tables):
            table_text = f"\n=== Table {i+1} ===\n"
            for row in table:
                # Filter out None values and join
                row_text = " | ".join([str(cell) if cell else "" for cell in row])
                table_text += row_text + "\n"
            formatted_tables.append(table_text)
        
        return {
            'raw_text': text,
            'formatted_tables': "\n".join(formatted_tables) if formatted_tables else "",
            'tables_data': tables,
            'metadata': metadata,
            'file_path': str(self.file_path),
            'file_type': 'pdf'
        }
    
    @staticmethod
    def is_valid_pdf(file_path: str | Path) -> bool:
        """
        Check if file is a valid PDF
        
        Args:
            file_path: Path to file
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
            if not file_path.suffix.lower() == '.pdf':
                return False
            
            # Try to open it
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages) > 0
        except Exception:
            return False

