# Changelog

## [1.1.0] - 2025-11-10

### ✨ Added - Groq Integration

- **Groq AI Provider Support**: Added support for Groq's ultra-fast inference API
- **Default Provider Changed**: Groq is now the default AI provider (was OpenAI)
- **New Default Model**: `llama-3.3-70b-versatile` for best quality Turkish extraction
- **Groq Configuration**: Added `GROQ_API_KEY`, `GROQ_MODEL`, and `GROQ_BASE_URL` settings
- **Provider Flexibility**: Easy switching between Groq, OpenAI, and Anthropic
- **Documentation**: Added comprehensive Groq setup and integration guides

### 📝 Updated

- **AI Extraction Engine**: Enhanced to support Groq's OpenAI-compatible API
- **Configuration System**: Updated to handle multiple AI providers with different models
- **CLI Tool**: Added `--provider groq` option
- **Environment Template**: Updated `.env.example` with Groq configuration
- **Documentation**: Updated README.md, QUICKSTART.md with Groq information

### 🔧 Technical Changes

#### Files Modified:
1. `ai/extraction_engine.py`
   - Added `base_url` parameter to `__init__`
   - Added Groq client initialization using OpenAI-compatible API
   - Enhanced JSON parsing to handle markdown code blocks
   - Updated provider routing to include Groq

2. `config.py`
   - Added `GROQ_API_KEY` configuration
   - Added `GROQ_MODEL` configuration (default: `llama-3.3-70b-versatile`)
   - Added `GROQ_BASE_URL` configuration
   - Changed default `AI_PROVIDER` to `groq`
   - Enhanced `get_ai_config()` method
   - Updated validation to check Groq API key

3. `main.py`
   - Added `groq` to provider choices
   - Added Groq configuration handling
   - Added `base_url` parameter passing

4. `.env.example`
   - Added Groq API key field
   - Added Groq model configuration
   - Added Groq base URL
   - Updated default provider to `groq`

#### Files Created:
- `GROQ_SETUP.md` - Complete Groq setup guide
- `GROQ_INTEGRATION.md` - Technical integration details
- `CHANGELOG.md` - This file

#### Files Updated:
- `README.md` - Added Groq information and examples
- `QUICKSTART.md` - Updated with Groq quick start instructions

### 🎯 Benefits

- **⚡ 10-100x Faster**: Groq provides significantly faster inference
- **💰 Cost-Effective**: Generous free tier and low pricing
- **🔓 Open Source**: Uses Llama 3.3 70B open-source model
- **🌍 Turkish Support**: Excellent multilingual capabilities including Turkish
- **🎁 Free Tier**: No credit card required to get started

### 📊 Performance

Rate limits for default model (`llama-3.3-70b-versatile`):
- 30 RPM (Requests Per Minute)
- 1K RPD (Requests Per Day)
- 12K TPM (Tokens Per Minute)  
- 100K TPD (Tokens Per Day)

Sufficient for processing 50-100 bank statements per day.

### 🔄 Backward Compatibility

✅ **Fully backward compatible**
- All existing OpenAI functionality preserved
- All existing Anthropic functionality preserved
- No breaking changes to API or data formats
- Can switch providers with single config change

### 📚 Documentation

New documentation:
- `GROQ_SETUP.md` - Step-by-step Groq setup
- `GROQ_INTEGRATION.md` - Technical implementation details

Updated documentation:
- `README.md` - Added Groq to features and usage
- `QUICKSTART.md` - Added Groq quick start
- `USAGE_EXAMPLES.md` - Includes Groq examples

### 🚀 Migration Guide

For existing users:

1. **Get Groq API Key**: Visit [console.groq.com](https://console.groq.com/)
2. **Update .env file**:
   ```env
   AI_PROVIDER=groq
   GROQ_API_KEY=gsk_your_key_here
   ```
3. **Run extraction**: Works exactly as before, just faster!

To continue using OpenAI or Anthropic:
```env
AI_PROVIDER=openai  # or anthropic
# Keep your existing API key
```

---

## [1.0.0] - 2025-11-10

### 🎉 Initial Release

- Multi-format support (PDF, Excel, CSV)
- AI-powered extraction (OpenAI, Anthropic)
- Automatic Turkish bank detection (14 banks)
- Standard transaction schema
- CLI tool for extraction
- Comprehensive documentation
- Test suite

### Features

- **PDF Extractor**: Text and table extraction from PDF statements
- **Excel Extractor**: Multi-sheet support for .xlsx and .xls files  
- **CSV Extractor**: Auto-encoding detection for Turkish characters
- **Bank Detector**: Automatic detection of 14 Turkish banks
- **AI Engine**: OpenAI GPT-4 and Anthropic Claude support
- **Transaction Schema**: Pydantic models for data validation
- **CLI Tool**: Command-line interface for easy usage
- **Documentation**: README, QUICKSTART, USAGE_EXAMPLES, IMPLEMENTATION_SUMMARY

### Supported Banks

1. Garanti BBVA
2. İş Bankası
3. Yapı Kredi
4. Akbank
5. Ziraat Bankası
6. Halkbank
7. Vakıfbank
8. Denizbank
9. QNB Finansbank
10. TEB
11. ING Bank
12. HSBC
13. Kuveyt Türk
14. Albaraka Türk

---

## Version History

- **1.1.0** (2025-11-10): Added Groq support, now default provider
- **1.0.0** (2025-11-10): Initial release with OpenAI and Anthropic

---

## Upcoming Features

### Planned for 1.2.0
- [ ] OCR support for image-based PDFs
- [ ] Batch processing capability
- [ ] Transaction categorization
- [ ] Duplicate detection

### Planned for 2.0.0
- [ ] Integration with SpendWise API
- [ ] Web interface for uploads
- [ ] Background job processing
- [ ] Database storage
- [ ] User authentication

---

**Current Version**: 1.1.0  
**Latest Update**: 2025-11-10  
**Status**: ✅ Production Ready

