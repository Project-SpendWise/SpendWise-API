# Troubleshooting Guide

## Common Issues and Solutions

### 1. ✅ FIXED: "Client.__init__() got an unexpected keyword argument 'proxies'"

**Error:**
```
Client.__init__() got an unexpected keyword argument 'proxies'
```

**Solution:**
Upgrade the OpenAI package:
```bash
source venv/bin/activate
pip install --upgrade openai
```

**Status:** ✅ Fixed in latest version

---

### 2. Excel File with Styling Corruption

**Error:**
```
TypeError: expected <class 'openpyxl.styles.fills.Fill'>
```

**Cause:** Some Excel files (especially from certain banks or software) have corrupted styling metadata that causes openpyxl to fail.

**Solutions:**

#### Option A: Export to CSV (Recommended ⭐)
1. Open the Excel file in Microsoft Excel or LibreOffice
2. Click **File → Save As**
3. Choose **CSV (UTF-8)** or **CSV (Comma delimited)**
4. Save the file
5. Run extraction on the CSV:
   ```bash
   python main.py --file yourfile.csv
   ```

#### Option B: Use Google Sheets
1. Upload the Excel file to Google Sheets
2. Download as CSV
3. Use the CSV for extraction

#### Option C: Use LibreOffice Command Line
```bash
libreoffice --headless --convert-to csv:"Text - txt - csv (StarCalc)":44,34,76 \
  --outdir . Hesap_Hareketleri_08112025.xlsx
```

#### Option D: Request Clean Export from Bank
Ask your bank for:
- CSV export
- Plain Excel without formatting
- Text-based PDF (not image/scanned)

---

### 3. PDF Returns 0 Transactions

**Issue:** PDF extraction shows "0 characters extracted" and "0 transactions"

**Cause:** The PDF is image-based (scanned document) rather than text-based.

**Solutions:**

#### Option A: Get Text-Based PDF
- Request a digital/text-based PDF from your bank
- Many banks offer both formats

#### Option B: Use Excel/CSV Instead
- Download transactions as Excel or CSV
- These are easier to process

#### Option C: Add OCR Support (Future)
OCR (Optical Character Recognition) will be added in a future version. For now:
1. Use online OCR tools to convert PDF to text
2. Or use Excel/CSV exports

---

### 4. "GROQ_API_KEY is required"

**Error:**
```
ValueError: GROQ_API_KEY is required when using Groq provider
```

**Solution:**
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```bash
   nano .env
   ```

3. Add your key:
   ```env
   GROQ_API_KEY=gsk_your_actual_key_here
   ```

4. Get a free key at: https://console.groq.com/

---

### 5. Rate Limit Errors (429)

**Error:**
```
429 Too Many Requests
```

**Solutions:**

#### Immediate:
- Wait 60 seconds and try again
- Check rate limit headers in debug mode

#### Short-term:
- Switch to faster model with higher limits:
  ```env
  GROQ_MODEL=llama-3.1-8b-instant
  ```

#### Long-term:
- Request higher limits at https://console.groq.com/
- Spread requests over time
- Batch process during off-peak hours

---

### 6. Module Not Found Errors

**Error:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

### 7. Incorrect Bank Detection

**Issue:** System detects wrong bank or shows "Could not detect bank"

**Impact:** ⚠️ Warning only - extraction will still work

**Solutions:**

#### Normal Operation:
The AI will still attempt to extract transactions even without bank detection.

#### To Improve Detection:
1. Add more patterns to `detectors/bank_detector.py`:
   ```python
   BankDetector.add_bank_pattern(
       bank_name="Your Bank",
       patterns=[r"Your\s+Bank", r"YOURBANK"]
   )
   ```

2. Or manually specify the bank in your code

---

### 8. Slow Processing

**Issue:** Extraction takes too long

**Solutions:**

#### Switch to Faster Model:
```env
# In .env file
GROQ_MODEL=llama-3.1-8b-instant  # Much faster
```

#### Or Use Groq Instead of OpenAI/Anthropic:
Groq is 10-100x faster than other providers.

---

### 9. Empty or Incomplete Extractions

**Issue:** Some transactions are missing or fields are empty

**Causes:**
- PDF is image-based (see #3)
- Excel file is corrupted (see #2)
- File format is unusual
- AI model hallucination

**Solutions:**

1. **Check the source file quality**
   - Is text selectable in PDF?
   - Does Excel open properly?

2. **Try different AI model**
   ```bash
   # Try the larger, more accurate model
   python main.py --file yourfile.pdf --provider groq
   # with GROQ_MODEL=llama-3.3-70b-versatile
   ```

3. **Enable debug mode**
   ```bash
   python main.py --file yourfile.pdf --debug
   ```

4. **Check the raw extracted text**
   Look in the debug output for what text was actually extracted

---

### 10. Turkish Character Encoding Issues

**Issue:** Turkish characters (ı, ş, ğ, ü, ö, ç) appear as gibberish

**For CSV Files:**
The CSV extractor automatically detects Turkish encoding (iso-8859-9, windows-1254).

**For Manual Conversion:**
Make sure to save as UTF-8 when exporting from Excel.

---

## Getting Help

### Debug Mode
Always use debug mode when troubleshooting:
```bash
python main.py --file yourfile.pdf --debug
```

This shows detailed logs including:
- File reading process
- Bank detection attempts
- AI API calls
- Data transformations

### Check Logs
Review the output for specific error messages and stack traces.

### Test Extractors
Run the test suite to verify components:
```bash
python test_extractors.py
```

### Common Solutions Summary

| Problem | Quick Fix |
|---------|-----------|
| Excel won't open | Export to CSV |
| PDF has 0 text | Use Excel/CSV instead |
| API key error | Add key to `.env` file |
| Rate limits | Switch to `llama-3.1-8b-instant` |
| Slow processing | Use Groq provider |
| Module errors | `pip install -r requirements.txt` |

---

## Still Having Issues?

1. **Check Documentation:**
   - `README.md` - Full documentation
   - `QUICKSTART.md` - Quick start guide
   - `GROQ_SETUP.md` - Groq-specific setup

2. **Verify Setup:**
   ```bash
   # Check Python version
   python3 --version  # Should be 3.8+
   
   # Check dependencies
   pip list | grep -E "openai|pdfplumber|pandas|openpyxl"
   
   # Check API key
   grep GROQ_API_KEY .env
   ```

3. **Test Components:**
   ```bash
   # Test file extractors (no API needed)
   python test_extractors.py
   
   # Test bank detector
   python main.py --list-banks
   ```

---

## Reporting Issues

When reporting issues, please include:
1. Error message (full traceback)
2. File type you're processing
3. Command you ran
4. Debug output (`--debug` flag)
5. Python version
6. OS information

---

**Last Updated:** 2025-11-10  
**Version:** 1.1.0

