"""
Configuration for transaction extraction system
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the extraction system"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    SAMPLES_DIR = BASE_DIR / "samples"
    OUTPUT_DIR = BASE_DIR / "output"
    
    # Groq API Configuration (only provider supported)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Faster, uses fewer tokens
    GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    
    # Extraction settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8000"))  # Increased for large statements
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
    BATCH_DELAY = float(os.getenv("BATCH_DELAY", "2.5"))  # Delay between batch requests (seconds)
    
    # File processing settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    SUPPORTED_FORMATS = [".pdf", ".xlsx", ".xls", ".csv"]
    
    # Turkish bank names for detection
    TURKISH_BANKS = [
        "Garanti",
        "Garanti BBVA",
        "İş Bankası",
        "Türkiye İş Bankası",
        "Yapı Kredi",
        "Akbank",
        "Ziraat Bankası",
        "Halkbank",
        "Vakıfbank",
        "Denizbank",
        "QNB Finansbank",
        "TEB",
        "ING Bank",
        "HSBC",
        "Kuveyt Türk",
        "Albaraka Türk"
    ]
    
    # Date formats commonly used in Turkish banks
    DATE_FORMATS = [
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d.%m.%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%d/%m/%Y %H:%M"
    ]
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required. Get your free key at https://console.groq.com/")
        
        # Create directories if they don't exist
        cls.SAMPLES_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        
        return True
    
    @classmethod
    def get_ai_config(cls):
        """Get Groq AI configuration"""
        return {
            "api_key": cls.GROQ_API_KEY,
            "model": cls.GROQ_MODEL,
            "base_url": cls.GROQ_BASE_URL,
            "max_tokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE
        }

