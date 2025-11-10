# Transaction Extraction System

AI-powered system to extract transaction data from Turkish bank statements in various formats (PDF, Excel, CSV).

## Features

- **Multi-format Support**: PDF, XLSX, XLS, CSV
- **AI-Powered**: Uses Groq (Llama 3), OpenAI GPT-4, or Anthropic Claude for intelligent extraction
- **Automatic Bank Detection**: Identifies Turkish bank from file content
- **Standardized Output**: Converts all transactions to a unified JSON schema
- **Turkish Language Support**: Handles Turkish bank-specific terminology
- **Lightning Fast**: Groq provides 10-100x faster inference than traditional APIs

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq, OpenAI, or Anthropic API key:

```env
AI_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key-here
```

**Get a free Groq API key**: [https://console.groq.com/](https://console.groq.com/)

### 3. Add Sample Files

Place your bank statement files in the `samples/` directory.

## Usage

### Basic Usage

```bash
python main.py --file samples/statement.pdf
```

### Specify Output Directory

```bash
python main.py --file samples/statement.xlsx --output output/
```

### Use Specific AI Provider

```bash
# Use Groq (default - fastest and free)
python main.py --file samples/statement.pdf --provider groq

# Use Anthropic Claude
python main.py --file samples/statement.pdf --provider anthropic

# Use OpenAI GPT-4
python main.py --file samples/statement.pdf --provider openai
```

## Output Format

The system outputs a JSON file with the following structure:

```json
{
  "bank_name": "Garanti BBVA",
  "account_number": "****1234",
  "statement_period_start": "2025-10-01T00:00:00",
  "statement_period_end": "2025-11-01T00:00:00",
  "opening_balance": 5000.00,
  "closing_balance": 4500.00,
  "currency": "TRY",
  "transactions": [
    {
      "transaction_id": "TXN001",
      "date": "2025-10-15T14:30:00",
      "description": "Market alışverişi",
      "amount": -150.50,
      "currency": "TRY",
      "transaction_type": "debit",
      "balance_after": 4849.50,
      "reference_number": "REF123456",
      "channel": "POS",
      "bank_name": "Garanti BBVA"
    }
  ]
}
```

## Supported Turkish Banks

- Garanti BBVA
- İş Bankası
- Yapı Kredi
- Akbank
- Ziraat Bankası
- Halkbank
- Vakıfbank
- Denizbank
- QNB Finansbank
- And more...

## Directory Structure

```
transaction-extractor/
├── ai/                 # AI extraction engine
├── detectors/          # Bank detection logic
├── extractors/         # File format handlers
├── models/             # Data schemas
├── samples/            # Sample bank statements
├── output/             # Extracted JSON files
├── config.py           # Configuration
├── main.py             # Main script
└── requirements.txt    # Dependencies
```

## How It Works

1. **File Loading**: Reads PDF, Excel, or CSV file
2. **Bank Detection**: Identifies the Turkish bank from content
3. **Raw Extraction**: Extracts text/tables from the file
4. **AI Processing**: Sends data to AI model with structured prompts
5. **Validation**: Validates extracted data against schema
6. **Output**: Saves standardized JSON file

## License

See main project LICENSE file.

