# SpendWise API - Quick Reference Card

## 🚀 Setup Commands

```bash
# 1. Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (see SETUP_FROM_SCRATCH.md for content)

# 4. Setup database
python setup_database.py

# 5. Start server
python app.py
```

## 📍 API Base URL

```
Development: http://localhost:5000/api
Health Check: http://localhost:5000/api/health
```

## 🔑 Authentication Flow

```javascript
// 1. Register
POST /api/auth/register
Body: { email, password, username, first_name, last_name }

// 2. Login
POST /api/auth/login
Body: { email, password }
Response: { access_token, refresh_token, user }

// 3. Use token in headers
Authorization: Bearer <access_token>

// 4. Refresh token (when expired)
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

## 📤 File Upload

```javascript
// Upload statement
POST /api/statements/upload
Content-Type: multipart/form-data
FormData: { file, profileName?, accountType?, color?, icon? }

// Poll for processing status
GET /api/statements/{id}
// Check: status === "processed"
```

## 📊 Key Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health` | GET | No | Health check |
| `/api/auth/register` | POST | No | Register user |
| `/api/auth/login` | POST | No | Login |
| `/api/auth/me` | GET | Yes | Get current user |
| `/api/statements/upload` | POST | Yes | Upload statement |
| `/api/statements` | GET | Yes | List statements |
| `/api/statements/profiles` | GET | Yes | List profiles |
| `/api/transactions` | GET | Yes | Get transactions |
| `/api/transactions/summary` | GET | Yes | Get summary |
| `/api/budgets` | POST/GET | Yes | Manage budgets |
| `/api/budgets/compare` | GET | Yes | Compare budgets |
| `/api/analytics/categories` | GET | Yes | Category breakdown |
| `/api/analytics/trends` | GET | Yes | Spending trends |
| `/api/analytics/insights` | GET | Yes | Financial insights |

## 🎯 Profile System (File Selection)

```javascript
// All endpoints support statementId parameter
GET /api/transactions?statementId={id}
GET /api/analytics/categories?statementId={id}
GET /api/budgets/compare?statementId={id}
// ... etc

// If no statementId: returns data for ALL statements
// If statementId provided: returns data for that profile only
```

## 🔧 Common Tasks

### Reset Database
```bash
python reset_database.py
```

### Run Tests
```bash
python test_all_endpoints.py
```

### Check Database
```bash
# SQLite database location
instance/spendwise.db
```

### View Logs
```bash
# Logs appear in terminal where Flask is running
# Look for: [INFO], [ERROR], [WARNING]
```

## ⚙️ Environment Variables (.env)

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///spendwise.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
UPLOAD_FOLDER=uploads
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | Activate venv, run `pip install -r requirements.txt` |
| Port 5000 in use | Kill process or change port in `app.py` |
| CORS errors | Add frontend URL to `CORS_ORIGINS` in `.env` |
| Database locked | Stop server, delete `instance/spendwise.db`, restart |
| Token expired | Use refresh token endpoint |
| Tables missing | Run `python setup_database.py` |

## 📚 Documentation Files

- **Setup Guide:** `SETUP_FROM_SCRATCH.md` - Complete setup instructions
- **Frontend Integration:** `FRONTEND_INTEGRATION_GUIDE.md` - API usage guide
- **Profile System:** `PROFILE_SYSTEM_FRONTEND_GUIDE.md` - Profile feature guide
- **Backend Docs:** `BACKEND_COMPREHENSIVE_DOCUMENTATION.md` - Technical details

## 💡 Frontend Integration Example

```javascript
// Axios setup
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: { 'Content-Type': 'application/json' }
});

// Add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Upload statement
const formData = new FormData();
formData.append('file', file);
formData.append('profileName', 'My Account');

const response = await api.post('/statements/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});

// Get transactions for profile
const transactions = await api.get('/transactions', {
  params: { statementId: selectedProfileId }
});
```

## 🎨 Transaction Categories

- `Gıda` - Food
- `Ulaşım` - Transport
- `Alışveriş` - Shopping
- `Faturalar` - Bills
- `Eğlence` - Entertainment
- `Sağlık` - Health
- `Eğitim` - Education
- `Diğer` - Other

## 📝 Response Format

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE",
    "statusCode": 400
  }
}
```

---

**For detailed information, see the full documentation files listed above.**
