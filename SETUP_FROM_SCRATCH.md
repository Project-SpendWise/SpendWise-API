# SpendWise API - Complete Setup Guide from Scratch

This guide will help you set up the SpendWise API from scratch and make it ready for frontend integration.

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.8 or higher** (check with `python --version`)
- **pip** (Python package manager)
- **Virtual environment** (recommended)
- **Text editor** or IDE (VS Code, PyCharm, etc.)

---

## 🚀 Step-by-Step Setup

### Step 1: Navigate to Project Directory

```bash
cd C:\Users\sinas\Desktop\project-spendwise\SpendWise-API
```

### Step 2: Create/Activate Virtual Environment

**Windows:**
```bash
# If venv doesn't exist, create it
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**Linux/Mac:**
```bash
# If venv doesn't exist, create it
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Verify activation:** You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-JWT-Extended 4.6.0
- Flask-CORS 6.0.1
- Flask-Migrate 4.0.5
- bcrypt 4.1.2
- python-dotenv 1.0.0
- SQLAlchemy 2.0.44

**Expected output:** All packages installed successfully.

### Step 4: Create Environment Configuration File

Create a `.env` file in the root directory:

**Windows (PowerShell):**
```powershell
New-Item -Path .env -ItemType File
```

**Windows (CMD):**
```cmd
type nul > .env
```

**Linux/Mac:**
```bash
touch .env
```

**Add this content to `.env`:**
```env
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production-12345
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production-12345
DATABASE_URL=sqlite:///spendwise.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
UPLOAD_FOLDER=uploads
```

**Important Notes:**
- `SECRET_KEY` and `JWT_SECRET_KEY`: Use strong random strings in production
- `CORS_ORIGINS`: Add your frontend URLs (React, Vue, etc.)
- `DATABASE_URL`: SQLite for development (change to PostgreSQL for production)

### Step 5: Initialize Database

**Option A: Automatic (Recommended)**

The database tables are created automatically when you first run the app. Just start the server:

```bash
python app.py
```

**Option B: Manual Setup**

If you want to create tables manually first:

```bash
python setup_database.py
```

**Expected output:**
```
Initializing database...
Creating tables...

✓ Database tables created successfully!

Created tables:
  - users
  - files
  - statements
  - transactions
  - budgets

You can now start the Flask server and test the endpoints.
```

### Step 6: Run Profile Migration (If Needed)

If you're upgrading from an older version, run the profile migration:

```bash
python migrate_add_profile_fields.py
```

**Note:** This is only needed if the `statements` table already exists without profile fields. For fresh installs, skip this step.

### Step 7: Start the Flask Server

```bash
python app.py
```

**Expected output:**
```
2024-11-23 10:00:00 [INFO] __main__: Application initialized in development mode
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

**Server is now running at:** `http://localhost:5000`

### Step 8: Verify Installation

**Test Health Check Endpoint:**

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/api/health | Select-Object -ExpandProperty Content
```

**Windows (CMD) or Linux/Mac:**
```bash
curl http://localhost:5000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "SpendWise API"
}
```

**Or open in browser:** `http://localhost:5000/api/health`

---

## 🎯 Frontend Configuration

### CORS Setup

The API is already configured for CORS. Make sure your frontend URLs are in the `.env` file:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

**Common Frontend Ports:**
- React (Create React App): `http://localhost:3000`
- Vite: `http://localhost:5173`
- Vue CLI: `http://localhost:8080`
- Next.js: `http://localhost:3000`

**To add more origins:** Add them to the comma-separated list in `.env`.

### API Base URL

In your frontend code, use:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

**For production:** Update this to your production server URL.

### Authentication Headers

All protected endpoints require JWT token:

```javascript
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
}
```

---

## 📝 Quick Test: Register and Login

Test the API with a simple registration:

**Using PowerShell (Windows):**
```powershell
$body = @{
    email = "test@example.com"
    password = "Test123!@#"
    username = "testuser"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/api/auth/register `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Using curl:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Expected response (201):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "...",
      "email": "test@example.com",
      "username": "testuser",
      ...
    }
  },
  "message": "User registered successfully"
}
```

**Then login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": { ... }
  }
}
```

---

## 🔧 Configuration for Frontend Integration

### 1. Update CORS Origins

Edit `.env` and add your frontend URL:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Restart the server** after changing `.env`.

### 2. Frontend API Client Setup

**Example with Axios (JavaScript/TypeScript):**

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            {},
            { headers: { Authorization: `Bearer ${refreshToken}` } }
          );
          localStorage.setItem('access_token', response.data.data.access_token);
          // Retry original request
          return api.request(error.config);
        } catch (refreshError) {
          // Refresh failed - redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 3. Environment Variables for Frontend

Create a `.env` file in your frontend project:

```env
REACT_APP_API_URL=http://localhost:5000/api
# or for Vite:
VITE_API_URL=http://localhost:5000/api
```

---

## 📚 API Endpoints Summary

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh access token

### Statements (File Upload)
- `POST /api/statements/upload` - Upload bank statement
- `GET /api/statements` - List all statements
- `GET /api/statements/{id}` - Get statement details
- `GET /api/statements/profiles` - List profiles
- `PUT /api/statements/{id}/profile` - Update profile metadata
- `POST /api/statements/{id}/set-default` - Set default profile

### Transactions
- `GET /api/transactions?statementId={id}` - Get transactions (filter by profile)
- `GET /api/transactions/summary?statementId={id}` - Get summary

### Budgets
- `POST /api/budgets` - Create/update budget
- `GET /api/budgets` - List budgets
- `GET /api/budgets/compare?statementId={id}` - Compare with actual spending
- `DELETE /api/budgets/{id}` - Delete budget

### Analytics
- `GET /api/analytics/categories?statementId={id}` - Category breakdown
- `GET /api/analytics/trends?statementId={id}` - Spending trends
- `GET /api/analytics/insights?statementId={id}` - Financial insights
- `GET /api/analytics/monthly-trends?statementId={id}` - Monthly trends
- `GET /api/analytics/forecast?statementId={id}` - Spending forecast
- ... and more (see FRONTEND_INTEGRATION_GUIDE.md)

**All analytics endpoints support `statementId` parameter for profile filtering.**

---

## 🐛 Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'bcrypt'"

**Solution:**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: "no such table: statements"

**Solution:**
```bash
# Run database setup
python setup_database.py

# Or restart the Flask server (tables are created automatically)
python app.py
```

### Issue 3: CORS Errors in Browser

**Solution:**
1. Check `.env` file has your frontend URL in `CORS_ORIGINS`
2. Restart Flask server after changing `.env`
3. Verify frontend is using correct API URL

### Issue 4: "Port 5000 already in use"

**Solution:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac: Find and kill process
lsof -ti:5000 | xargs kill -9

# Or change port in app.py (last line):
app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
```

### Issue 5: Database Locked Error

**Solution:**
```bash
# Stop the Flask server
# Delete the database file
rm instance/spendwise.db  # Linux/Mac
del instance\spendwise.db  # Windows

# Restart server (will create new database)
python app.py
```

### Issue 6: Token Expired (401 Unauthorized)

**Solution:**
- Access tokens expire in 15 minutes
- Use refresh token to get new access token:
  ```javascript
  POST /api/auth/refresh
  Authorization: Bearer <refresh_token>
  ```

---

## ✅ Verification Checklist

Before connecting your frontend, verify:

- [ ] Virtual environment is activated
- [ ] All dependencies installed (`pip list` shows Flask, etc.)
- [ ] `.env` file exists with correct CORS origins
- [ ] Database tables created (check `instance/spendwise.db` exists)
- [ ] Flask server running on `http://localhost:5000`
- [ ] Health check returns `{"status": "healthy"}`
- [ ] Can register a user successfully
- [ ] Can login and get tokens
- [ ] CORS allows your frontend origin

---

## 🚀 Production Deployment Notes

**For production, you should:**

1. **Change secret keys:**
   ```env
   SECRET_KEY=<strong-random-secret-key>
   JWT_SECRET_KEY=<strong-random-jwt-secret>
   ```

2. **Use PostgreSQL instead of SQLite:**
   ```env
   DATABASE_URL=postgresql://user:password@localhost/spendwise
   ```

3. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Set proper CORS origins:**
   ```env
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

5. **Enable HTTPS** (use reverse proxy like Nginx)

6. **Set `FLASK_ENV=production`** in `.env`

---

## 📖 Additional Documentation

- **Frontend Integration Guide:** `FRONTEND_INTEGRATION_GUIDE.md`
- **Profile System Guide:** `PROFILE_SYSTEM_FRONTEND_GUIDE.md`
- **Backend Documentation:** `BACKEND_COMPREHENSIVE_DOCUMENTATION.md`
- **API Testing:** `test_all_endpoints.py`

---

## 🎉 You're Ready!

Your SpendWise API is now set up and ready for frontend integration!

**Next Steps:**
1. Keep the Flask server running
2. Start your frontend application
3. Connect to `http://localhost:5000/api`
4. Test authentication flow
5. Upload a statement file
6. View transactions and analytics

**Need Help?**
- Check server logs for errors
- Review `FRONTEND_INTEGRATION_GUIDE.md` for API usage
- Test endpoints with `test_all_endpoints.py`

---

## Quick Reference Commands

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup database
python setup_database.py

# Start server
python app.py

# Test endpoints
python test_all_endpoints.py

# Reset database (if needed)
python reset_database.py
```

---

**Happy Coding! 🚀**
