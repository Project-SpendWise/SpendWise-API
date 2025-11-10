# Groq Setup Guide

## 🚀 Quick Setup with Groq

Groq provides extremely fast inference with open-source models at low cost.

### 1. Get Your Groq API Key

1. Go to [https://console.groq.com/](https://console.groq.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy your key (starts with `gsk_...`)

### 2. Configure the System

```bash
# Copy the example env file
cp .env.example .env

# Edit the .env file
nano .env
```

Set these values:
```env
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Run Your First Extraction

```bash
# Activate virtual environment
source venv/bin/activate

# Extract from a file
python main.py --file samples/Hesap_Hareketleri_08112025.pdf
```

## 📊 Available Groq Models

### Recommended for Turkish Bank Statements:

| Model | Speed | Quality | TPM | TPD | Best For |
|-------|-------|---------|-----|-----|----------|
| **llama-3.3-70b-versatile** | Medium | ⭐⭐⭐⭐⭐ | 12K | 100K | **Default - Best quality** |
| **llama-3.1-8b-instant** | Fast | ⭐⭐⭐⭐ | 6K | 500K | High volume, budget-friendly |
| **qwen/qwen3-32b** | Fast | ⭐⭐⭐⭐ | 6K | 500K | Multilingual excellence |

### Switch Models

In your `.env` file:
```env
# For best quality (default)
GROQ_MODEL=llama-3.3-70b-versatile

# For speed and volume
GROQ_MODEL=llama-3.1-8b-instant

# For multilingual support
GROQ_MODEL=qwen/qwen3-32b
```

Or via command line:
```bash
# Use specific model
export GROQ_MODEL=llama-3.1-8b-instant
python main.py --file statement.pdf
```

## 💰 Rate Limits

### llama-3.3-70b-versatile (Default)
- **30 RPM** (Requests Per Minute)
- **1K RPD** (Requests Per Day)
- **12K TPM** (Tokens Per Minute)
- **100K TPD** (Tokens Per Day)

This means:
- ✅ Can process ~50-100 bank statements per day
- ✅ Each statement typically uses 2K-8K tokens
- ✅ Perfect for individual/small business use

### llama-3.1-8b-instant (High Volume)
- **30 RPM**
- **14.4K RPD** 
- **6K TPM**
- **500K TPD**

This means:
- ✅ Can process 500+ bank statements per day
- ✅ Faster processing
- ✅ Great for batch processing

## 🎯 Why Groq?

### Advantages
1. **⚡ Lightning Fast**: 10-100x faster than traditional APIs
2. **💰 Cost-Effective**: Generous free tier + low prices
3. **🔓 Open Source**: Uses Llama, Mixtral, Qwen models
4. **🌍 Turkish Support**: Llama 3 handles Turkish very well
5. **🔄 OpenAI Compatible**: Easy to integrate

### Comparison

| Feature | Groq | OpenAI | Anthropic |
|---------|------|--------|-----------|
| Speed | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡ |
| Cost | 💰 | 💰💰💰 | 💰💰💰 |
| Turkish | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Free Tier | ✅ Yes | ❌ No | ❌ No |
| Open Source | ✅ Yes | ❌ No | ❌ No |

## 🔧 Advanced Configuration

### Custom Base URL
If you're using a different endpoint:
```env
GROQ_BASE_URL=https://your-custom-endpoint.com/v1
```

### Adjust Token Limits
For longer statements:
```env
MAX_TOKENS=8000
```

### Temperature Control
For more creative vs deterministic:
```env
TEMPERATURE=0.1  # More deterministic (recommended)
TEMPERATURE=0.5  # More creative
```

## 🚨 Troubleshooting

### "GROQ_API_KEY is required"
```bash
# Make sure .env file exists
ls -la .env

# Check the content
cat .env

# Verify the key is set
grep GROQ_API_KEY .env
```

### Rate Limit Errors (429)
If you hit rate limits:
1. Wait a minute and try again
2. Switch to `llama-3.1-8b-instant` for higher limits
3. Request higher limits at [Groq Console](https://console.groq.com/)

### Slow Processing
Try the faster model:
```env
GROQ_MODEL=llama-3.1-8b-instant
```

## 📈 Performance Tips

1. **Batch Processing**: Process multiple files during off-peak hours
2. **Model Selection**: Use 8B for volume, 70B for quality
3. **Token Management**: Keep prompts concise
4. **Caching**: Reuse extraction results when possible

## 🔄 Switching Providers

You can easily switch between providers:

```bash
# Use Groq (default)
python main.py --file statement.pdf --provider groq

# Use OpenAI
python main.py --file statement.pdf --provider openai

# Use Anthropic
python main.py --file statement.pdf --provider anthropic
```

Just make sure you have the corresponding API key in your `.env` file.

## 📚 Example Usage

### Basic Extraction
```bash
python main.py --file samples/Hesap_Hareketleri_08112025.pdf
```

### With Debug Output
```bash
python main.py --file samples/Hesap_Hareketleri_08112025.xlsx --debug
```

### Custom Output Directory
```bash
python main.py --file statement.pdf --output ./results/
```

### Batch Processing
```bash
for file in samples/*.pdf; do
    python main.py --file "$file"
done
```

## 🆘 Support

- **Groq Documentation**: [https://console.groq.com/docs](https://console.groq.com/docs)
- **Groq Discord**: Join for community support
- **Rate Limit Increases**: Request at [https://console.groq.com/](https://console.groq.com/)

## 🎉 Get Started Now!

```bash
# 1. Get API key from console.groq.com
# 2. Configure
cp .env.example .env
nano .env  # Add your GROQ_API_KEY

# 3. Extract!
source venv/bin/activate
python main.py --file samples/Hesap_Hareketleri_08112025.pdf
```

That's it! You're ready to extract Turkish bank transactions with Groq! 🚀

