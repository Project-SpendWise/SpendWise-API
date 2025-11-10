# Usage Examples

## Basic Usage

### 1. First Time Setup

```bash
cd transaction-extractor

# Install dependencies
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Create .env file
cp .env.example .env

# Edit with your favorite editor
nano .env
```

Add your API key:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

### 3. Extract Your First File

```bash
# Activate virtual environment
source venv/bin/activate

# Extract from PDF
python main.py --file samples/Hesap_Hareketleri_08112025.pdf
```

## Command Line Options

### List Supported Banks
```bash
python main.py --list-banks
```

Output:
```
Supported Turkish Banks:
==================================================
 1. Garanti BBVA
 2. İş Bankası
 3. Yapı Kredi
 4. Akbank
 5. Ziraat Bankası
 ... (14 banks total)
```

### Extract with Custom Output Directory
```bash
python main.py --file statement.pdf --output ./my_results/
```

### Use Different AI Provider
```bash
# Use Anthropic Claude instead of OpenAI
python main.py --file statement.pdf --provider anthropic
```

### Enable Debug Logging
```bash
python main.py --file statement.pdf --debug
```

## Testing Without API Keys

Run the test suite to verify extractors work:

```bash
python test_extractors.py
```

This tests:
- PDF extraction
- Excel extraction
- CSV extraction
- Bank detection

No API credits are consumed.

## Python API Usage

### Example 1: Extract from a File

```python
from extractors import PDFExtractor
from detectors import BankDetector
from ai import AIExtractionEngine
from config import Config

# Initialize
config = Config.get_ai_config()
ai_engine = AIExtractionEngine(
    provider=config['provider'],
    api_key=config['api_key'],
    model=config['model']
)

# Extract raw data
pdf_extractor = PDFExtractor('statement.pdf')
raw_data = pdf_extractor.extract_structured()

# Detect bank
bank = BankDetector.detect_from_text(raw_data['raw_text'])
print(f"Detected bank: {bank}")

# Extract transactions with AI
result = ai_engine.extract_transactions(
    raw_data=raw_data['raw_text'],
    bank_name=bank
)

print(f"Extracted {len(result['transactions'])} transactions")
```

### Example 2: Process All Files in a Directory

```python
from pathlib import Path
from main import TransactionExtractor

# Initialize extractor
extractor = TransactionExtractor()

# Process all PDF files
pdf_dir = Path('statements')
for pdf_file in pdf_dir.glob('*.pdf'):
    print(f"Processing: {pdf_file.name}")
    try:
        output_path = extractor.extract_and_save(pdf_file)
        print(f"✓ Saved to: {output_path}")
    except Exception as e:
        print(f"✗ Failed: {e}")
```

### Example 3: Validate Extracted Data

```python
import json
from models import BankStatement, Transaction

# Load extracted JSON
with open('output/statement_extracted.json', 'r') as f:
    data = json.load(f)

# Validate with Pydantic
try:
    statement = BankStatement(**data)
    print(f"✓ Valid statement with {len(statement.transactions)} transactions")
    
    # Calculate totals
    total_credits = statement.get_total_credits()
    total_debits = statement.get_total_debits()
    
    print(f"Total Credits: {total_credits:.2f} {statement.currency}")
    print(f"Total Debits: {total_debits:.2f} {statement.currency}")
    
except Exception as e:
    print(f"✗ Validation failed: {e}")
```

### Example 4: Custom Bank Detection

```python
from detectors import BankDetector

# Add custom bank patterns
BankDetector.add_bank_pattern(
    bank_name="Custom Bank",
    patterns=[
        r"Custom\s+Bank",
        r"CUSTOMBANK"
    ]
)

# Detect with confidence scoring
text = "Statement from Custom Bank for account 1234"
result = BankDetector.detect_with_confidence(text)

print(f"Bank: {result['bank']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Matches: {result['matches']}")
```

### Example 5: Extract Only Specific Data

```python
from extractors import ExcelExtractor

# Extract from Excel
extractor = ExcelExtractor('statement.xlsx')

# Get metadata only
metadata = extractor.extract_metadata()
print(f"Sheets: {metadata['sheet_names']}")
print(f"Rows: {metadata['first_sheet_rows']}")

# Get only first 10 records
records = extractor.extract_as_records()[:10]
for i, record in enumerate(records, 1):
    print(f"{i}. {record}")
```

## Output Format

### JSON Structure

```json
{
  "bank_name": "Garanti BBVA",
  "account_number": "****1234",
  "statement_period_start": "2025-10-01",
  "statement_period_end": "2025-11-01",
  "opening_balance": 5000.00,
  "closing_balance": 4500.00,
  "currency": "TRY",
  "transactions": [
    {
      "transaction_id": "TXN001",
      "date": "2025-10-15",
      "description": "MARKET ALIŞVERİŞİ",
      "amount": -150.50,
      "currency": "TRY",
      "transaction_type": "debit",
      "balance_after": 4849.50,
      "reference_number": "REF123456",
      "channel": "POS",
      "bank_name": "Garanti BBVA",
      "account_number": "****1234"
    }
  ],
  "extraction_metadata": {
    "extracted_at": "2025-11-10T14:30:00",
    "ai_provider": "openai",
    "ai_model": "gpt-4-turbo-preview",
    "transaction_count": 45
  },
  "source_file": {
    "filename": "statement.pdf",
    "file_type": "pdf",
    "file_size_bytes": 524288,
    "processed_at": "2025-11-10T14:30:00"
  }
}
```

## Advanced Usage

### Custom AI Prompts

Modify `ai/extraction_engine.py` to customize prompts:

```python
def _create_extraction_prompt(self, raw_data: str, bank_name: Optional[str] = None) -> str:
    # Add custom instructions
    custom_instructions = """
    Additional extraction rules:
    - Categorize groceries as "Food"
    - Categorize transport as "Transport"
    """
    
    # Modify the prompt...
```

### Batch Processing Script

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
from main import TransactionExtractor

def batch_process(directory: str):
    extractor = TransactionExtractor()
    files = list(Path(directory).glob('*.*'))
    
    results = {'success': 0, 'failed': 0}
    
    for file in files:
        if file.suffix not in ['.pdf', '.xlsx', '.xls', '.csv']:
            continue
        
        try:
            print(f"Processing: {file.name}...")
            output = extractor.extract_and_save(file)
            print(f"✓ Success: {output}")
            results['success'] += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            results['failed'] += 1
    
    print(f"\nResults: {results['success']} success, {results['failed']} failed")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py <directory>")
        sys.exit(1)
    
    batch_process(sys.argv[1])
```

## Troubleshooting

### Issue: "API key is required"

**Solution:**
```bash
# Make sure .env file exists
cp .env.example .env

# Edit and add your key
nano .env
```

### Issue: "Module not found"

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Could not detect bank"

**Solution:**
This is just a warning. The extraction will still work. The AI will try to determine the bank from the content.

### Issue: Excel file won't open

**Solution:**
```bash
# Try converting to CSV first
# Or resave in Excel with "Save As"
```

### Issue: PDF returns 0 characters

**Solution:**
The PDF might be image-based (scanned). Consider:
- Using OCR preprocessing
- Asking the bank for a text-based PDF
- Using the Excel/CSV export instead

## Tips & Best Practices

1. **Start Small**: Test with one file first
2. **Check Output**: Always verify the first extraction
3. **Use Debug Mode**: When troubleshooting issues
4. **Batch at Night**: Process large batches when API costs are lower
5. **Keep Originals**: Don't delete source files
6. **Version Control**: Track changes to extraction logic
7. **Monitor Costs**: Track AI API usage
8. **Validate Results**: Use the Pydantic models

## Next Steps

After successful extraction:

1. **Review the JSON**: Check for accuracy
2. **Import to Database**: Load transactions into your system
3. **Categorize**: Add transaction categories
4. **Analyze**: Build reports and insights
5. **Automate**: Set up scheduled processing

## Support

- **Documentation**: See README.md
- **Quick Start**: See QUICKSTART.md
- **Implementation**: See IMPLEMENTATION_SUMMARY.md
- **Tests**: Run `python test_extractors.py`

