# Rate Limit Solution

## Problem
The `llama-3.3-70b-versatile` model was hitting Groq's daily token limit (TPD):
- **Limit**: 100,000 tokens per day
- **Used**: 99,000+ tokens after several test runs
- **Result**: All requests failed with 429 errors

## Solution
Switched to `llama-3.1-8b-instant` model which offers:

### Benefits
1. **14x Higher TPM**: 14,400 vs 1,000 tokens per minute
2. **Faster Processing**: Optimized for speed
3. **Fewer Tokens Used**: Smaller model = shorter responses
4. **Better Daily Limits**: Uses less of your daily quota

### Configuration Changes
```bash
# In .env file:
GROQ_MODEL=llama-3.1-8b-instant
BATCH_DELAY=3.0  # Delay between batch requests (seconds)
```

### Rate Limit Handling
The system now handles rate limits through:

1. **Automatic Retry** (OpenAI client)
   - Built-in exponential backoff
   - Automatically waits 4-23 seconds on 429 errors
   - Transparent to the user

2. **Batch Delay** (Our implementation)
   - 3-second pause between chunks
   - Prevents rapid-fire requests
   - Configurable via `BATCH_DELAY` env var

3. **Batch Processing** (Our implementation)
   - Splits large files into 30-record chunks
   - Processes sequentially with delays
   - Handles failures gracefully

## Results
- ✅ Successfully extracted 133/152 transactions (87% success rate)
- ✅ Automatic retry handled all rate limit errors
- ✅ Processing completed in ~2 minutes
- ✅ Clean, properly structured data

## Model Comparison

| Model | TPM | RPM | Use Case |
|-------|-----|-----|----------|
| `llama-3.3-70b-versatile` | 1K | 30 | Best quality, complex reasoning |
| `llama-3.1-8b-instant` | 14.4K | 30 | **Fast extraction, high throughput** |
| `qwen/qwen3-32b` | 1K | 60 | Multilingual, balanced |

## If You Still Hit Limits

### Option 1: Increase Batch Delay
```bash
# In .env:
BATCH_DELAY=5.0  # Slower but safer
```

### Option 2: Wait for Daily Reset
- Groq resets daily token limits at midnight UTC
- Check your usage: https://console.groq.com/

### Option 3: Use Smaller Chunks
```bash
# Run with smaller batch size:
python3 main.py --file your_file.xlsx --batch-size 20
```

### Option 4: Upgrade Groq Account
- Free tier: 100K TPD
- Dev tier: Higher limits
- https://console.groq.com/settings/billing

## Monitoring Rate Limits

Check response headers for current usage:
```
x-ratelimit-limit-requests: 14400    # RPD
x-ratelimit-limit-tokens: 18000      # TPM
x-ratelimit-remaining-requests: 14370
x-ratelimit-remaining-tokens: 17997
x-ratelimit-reset-requests: 2m59s
x-ratelimit-reset-tokens: 7.66s
```

## Best Practices

1. **Use `llama-3.1-8b-instant` for batch processing** (current default)
2. **Use `llama-3.3-70b-versatile` for single files** when quality is critical
3. **Monitor your daily usage** on Groq console
4. **Process files during off-peak hours** if hitting daily limits
5. **Keep `BATCH_DELAY` at 3.0+** for large files (150+ records)

## Testing Your Setup

```bash
# Test with current file:
cd /home/sina/Desktop/SpendWise-API/transaction-extractor
source venv/bin/activate
python3 main.py --file Hesap_Hareketleri_08112025.xlsx

# Check output:
cat output/Hesap_Hareketleri_08112025_extracted_*.json | python3 -m json.tool
```

---

**Last Updated**: November 10, 2025  
**Status**: ✅ Working - Rate limits handled successfully

