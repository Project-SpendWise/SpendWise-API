# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Run the setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit and add your API key
nano .env
```

Add one of these:
```env
# For Groq (Recommended - Free & Fast!)
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your-key-here

# OR for OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# OR for Anthropic
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
```

**Get a free Groq API key**: Visit [console.groq.com](https://console.groq.com/)

### Step 3: Test the Extractors (No API Key Needed)

```bash
# Test that file extractors work
python test_extractors.py
```

This will test PDF, Excel, and CSV extraction without using any API credits.

### Step 4: Extract Your First Transaction File

```bash
# Extract from a PDF
python main.py --file samples/Hesap_Hareketleri_08112025.pdf

# Extract from an Excel file
python main.py --file samples/Hesap_Hareketleri_08112025.xlsx

# Specify output directory
python main.py --file samples/statement.pdf --output ./my_output/
```

### Step 5: Check the Results

Look in the `output/` directory for JSON files with extracted transactions:

```bash
cat output/Hesap_Hareketleri_08112025_extracted_*.json
```

## 📋 Common Commands

```bash
# List supported Turkish banks
python main.py --list-banks

# Use specific AI provider
python main.py --file statement.pdf --provider groq     # Default - Fast & Free
python main.py --file statement.pdf --provider anthropic
python main.py --file statement.pdf --provider openai

# Enable debug logging
python main.py --file statement.pdf --debug

# Get help
python main.py --help
```

## 📊 Understanding the Output

The extracted JSON contains:

```json
{
  "bank_name": "Garanti BBVA",
  "account_number": "****1234",
  "currency": "TRY",
  "transactions": [
    {
      "transaction_id": "TXN001",
      "date": "2025-11-08",
      "description": "Market alışverişi",
      "amount": -150.50,
      "transaction_type": "debit",
      "channel": "POS",
      "balance_after": 4849.50
    }
  ],
  "extraction_metadata": {
    "extracted_at": "2025-11-10T14:30:00",
    "ai_provider": "openai",
    "transaction_count": 45
  }
}
```

## 🔧 Troubleshooting

### "API key is required" error
- Make sure you've copied `.env.example` to `.env`
- Add your API key to the `.env` file
- Check that the key starts with `sk-` for OpenAI

### "Module not found" error
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Could not detect bank" warning
- This is normal for some files
- The extraction will still work
- You can manually specify bank name in the future

### File encoding issues (Turkish characters)
- The CSV extractor automatically detects Turkish encoding
- If issues persist, files might need manual encoding specification

## 🎯 Next Steps

1. **Test with your own bank statements**
2. **Integrate into your SpendWise API** (coming soon)
3. **Add custom categorization** for transactions
4. **Build a web interface** for easier uploads

## 💡 Tips

- Start with small files to test
- Check the JSON output for accuracy
- Each bank may have slightly different formats
- The AI learns and adapts to different formats
- Keep your API keys secure and never commit them

## 📚 More Information

See `README.md` for full documentation.

