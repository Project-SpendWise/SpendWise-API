# SpendWise API - Frontend Integration Guide

Complete guide for integrating the SpendWise API with your frontend application.

## Base Configuration

**Base URL:** `http://localhost:5000/api` (development)  
**Production URL:** Update when deploying

**Authentication:** All endpoints (except auth) require JWT token in header:
```
Authorization: Bearer <access_token>
```

---

## 1. Authentication Endpoints

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": "2024-11-22T14:00:00Z",
      "is_active": true
    }
  },
  "message": "User registered successfully"
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe"
    }
  },
  "message": "Login successful"
}
```

**Store tokens:** Save `access_token` and `refresh_token` (e.g., localStorage)

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
}
```

### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token...",
    "refresh_token": "new_refresh_token..."
  }
}
```

---

## 2. Statement Endpoints (File Upload & Management)

### Upload Statement
```http
POST /api/statements/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Form Data:
  file: <binary file data>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "stmt_123456",
    "fileName": "bank_statement_nov_2024.pdf",
    "uploadDate": "2024-11-22T14:00:00Z",
    "status": "processing",
    "transactionCount": null,
    "statementPeriodStart": null,
    "statementPeriodEnd": null,
    "isProcessed": false
  },
  "message": "Statement uploaded successfully"
}
```

**Important:** Status will be `"processing"` initially. Poll the statement details endpoint to check when it becomes `"processed"`.

### List All Statements
```http
GET /api/statements
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "statements": [
      {
        "id": "stmt_123456",
        "fileName": "bank_statement_nov_2024.pdf",
        "uploadDate": "2024-11-22T14:00:00Z",
        "status": "processed",
        "transactionCount": 45,
        "statementPeriodStart": "2024-11-01T00:00:00Z",
        "statementPeriodEnd": "2024-11-30T23:59:59Z",
        "isProcessed": true
      }
    ]
  }
}
```

### Get Statement Details
```http
GET /api/statements/{statementId}
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "stmt_123456",
    "fileName": "bank_statement_nov_2024.pdf",
    "uploadDate": "2024-11-22T14:00:00Z",
    "status": "processed",
    "transactionCount": 45,
    "statementPeriodStart": "2024-11-01T00:00:00Z",
    "statementPeriodEnd": "2024-11-30T23:59:59Z",
    "isProcessed": true
  }
}
```

**Use Case:** Poll this endpoint every 2-3 seconds after upload to check if `status` changed from `"processing"` to `"processed"`.

### Delete Statement
```http
POST /api/statements/{statementId}/delete
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "success": true,
    "message": "Statement deleted successfully"
  }
}
```

---

## 3. Transaction Endpoints

### Get Transactions
```http
GET /api/transactions?statementId={id}&startDate={date}&endDate={date}&category={cat}&limit={n}&offset={n}
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `statementId` (optional): Filter by specific statement (for file selection)
- `startDate` (optional): ISO 8601 date - Filter from this date
- `endDate` (optional): ISO 8601 date - Filter until this date
- `category` (optional): Filter by category name
- `account` (optional): Filter by account name
- `limit` (optional): Max results (default: 50, max: 100)
- `offset` (optional): Skip results (default: 0)

**Examples:**
```http
# Get all transactions
GET /api/transactions

# Get transactions for specific statement (FILE SELECTION)
GET /api/transactions?statementId=stmt_123456

# Get transactions with filters
GET /api/transactions?statementId=stmt_123456&category=Gıda&limit=20&offset=0

# Get transactions by date range
GET /api/transactions?startDate=2024-11-01T00:00:00Z&endDate=2024-11-30T23:59:59Z
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "txn_123456",
        "date": "2024-11-01T10:30:00Z",
        "description": "Migros Market Alışverişi",
        "amount": 245.50,
        "type": "expense",
        "category": "Gıda",
        "merchant": "Migros",
        "account": "Ana Hesap",
        "referenceNumber": "REF123456",
        "statementId": "stmt_123456"
      }
    ],
    "total": 45,
    "limit": 20,
    "offset": 0
  }
}
```

### Get Transaction Summary
```http
GET /api/transactions/summary?statementId={id}&startDate={date}&endDate={date}
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `statementId` (optional): Filter by specific statement (for file selection)
- `startDate` (optional): ISO 8601 date
- `endDate` (optional): ISO 8601 date

**Response (200):**
```json
{
  "success": true,
  "data": {
    "totalIncome": 15000.00,
    "totalExpenses": 8500.50,
    "savings": 6499.50,
    "transactionCount": 45,
    "period": {
      "start": "2024-11-01T00:00:00Z",
      "end": "2024-11-30T23:59:59Z"
    }
  }
}
```

---

## 4. Budget Endpoints

### Create/Update Budget
```http
POST /api/budgets
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "categoryId": "food",
  "categoryName": "Gıda",
  "amount": 2500.00,
  "period": "monthly",
  "startDate": "2024-11-01T00:00:00Z"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "budget_food_monthly",
    "categoryId": "food",
    "categoryName": "Gıda",
    "amount": 2500.00,
    "period": "monthly",
    "startDate": "2024-11-01T00:00:00Z",
    "endDate": "2024-11-30T23:59:59Z"
  },
  "message": "Budget saved successfully"
}
```

### List Budgets
```http
GET /api/budgets?period={period}&categoryId={id}
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `period` (optional): `"monthly"` or `"yearly"`
- `categoryId` (optional): Filter by category ID

**Response (200):**
```json
{
  "success": true,
  "data": {
    "budgets": [
      {
        "id": "budget_food_monthly",
        "categoryId": "food",
        "categoryName": "Gıda",
        "amount": 2500.00,
        "period": "monthly",
        "startDate": "2024-11-01T00:00:00Z",
        "endDate": "2024-11-30T23:59:59Z"
      }
    ]
  }
}
```

### Get Budget Comparison
```http
GET /api/budgets/compare?statementId={id}&period={period}&startDate={date}&endDate={date}
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `statementId` (optional): **CRITICAL** - Filter by specific statement (for file selection)
- `period` (optional): `"monthly"` or `"yearly"` (default: `"monthly"`)
- `startDate` (optional): ISO 8601 date
- `endDate` (optional): ISO 8601 date

**Response (200):**
```json
{
  "success": true,
  "data": {
    "comparisons": [
      {
        "budget": {
          "id": "budget_food_monthly",
          "categoryId": "food",
          "categoryName": "Gıda",
          "amount": 2500.00
        },
        "actualSpending": 2450.50,
        "remaining": 49.50,
        "percentageUsed": 98.02,
        "isOverBudget": false,
        "status": "on_track"
      }
    ],
    "period": {
      "start": "2024-11-01T00:00:00Z",
      "end": "2024-11-30T23:59:59Z"
    }
  }
}
```

**Status Values:**
- `"on_track"`: Spending < 80% of budget
- `"approaching_budget"`: Spending 80-100% of budget
- `"over_budget"`: Spending > 100% of budget

### Delete Budget
```http
DELETE /api/budgets/{budgetId}
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "success": true,
    "message": "Budget deleted successfully"
  }
}
```

---

## 5. Analytics Endpoints

**IMPORTANT:** All analytics endpoints support `statementId` query parameter for file selection.

### Get Category Breakdown
```http
GET /api/analytics/categories?statementId={id}&startDate={date}&endDate={date}
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "category": "Gıda",
        "totalAmount": 2450.50,
        "percentage": 28.8,
        "transactionCount": 15
      },
      {
        "category": "Ulaşım",
        "totalAmount": 1150.50,
        "percentage": 13.5,
        "transactionCount": 8
      }
    ],
    "totalExpenses": 8500.50
  }
}
```

### Get Spending Trends
```http
GET /api/analytics/trends?statementId={id}&period={period}&startDate={date}&endDate={date}
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `statementId` (optional): Filter by statement
- `period` (optional): `"day"`, `"week"`, or `"month"` (default: `"day"`)
- `startDate` (optional): ISO 8601 date
- `endDate` (optional): ISO 8601 date

**Response (200):**
```json
{
  "success": true,
  "data": {
    "trends": [
      {
        "date": "2024-11-01T00:00:00Z",
        "totalAmount": 445.50,
        "transactionCount": 3
      },
      {
        "date": "2024-11-02T00:00:00Z",
        "totalAmount": 320.75,
        "transactionCount": 2
      }
    ],
    "period": "day"
  }
}
```

### Get Financial Insights
```http
GET /api/analytics/insights?statementId={id}&startDate={date}&endDate={date}
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "insights": [
      {
        "type": "low_savings_rate",
        "title": "Low Savings Rate",
        "message": "You are saving 8.5% of your income. You should aim for at least 20%.",
        "severity": "warning"
      },
      {
        "type": "highest_spending_category",
        "title": "Highest Spending Category",
        "message": "You spend the most in Alışveriş category.",
        "severity": "info"
      }
    ]
  }
}
```

**Severity Levels:** `"info"`, `"warning"`, `"error"`, `"success"`

### Get Monthly Trends
```http
GET /api/analytics/monthly-trends?statementId={id}&months={n}
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `statementId` (optional): Filter by statement
- `months` (optional): Number of months (default: 12, max: 24)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "monthlyData": [
      {
        "month": "2024-11-01T00:00:00Z",
        "income": 15000.00,
        "expenses": 8500.50,
        "savings": 6499.50
      }
    ]
  }
}
```

### Get Category Trends Over Time
```http
GET /api/analytics/category-trends?statementId={id}&topCategories={n}&months={n}
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `statementId` (optional): Filter by statement
- `topCategories` (optional): Number of top categories (default: 5, max: 10)
- `months` (optional): Number of months (default: 12)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "categoryTrends": [
      {
        "categoryName": "Gıda",
        "monthlyData": [
          {
            "month": "2024-11-01T00:00:00Z",
            "amount": 2450.50
          }
        ]
      }
    ]
  }
}
```

### Get Weekly Patterns
```http
GET /api/analytics/weekly-patterns?statementId={id}&weeks={n}
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `statementId` (optional): Filter by statement
- `weeks` (optional): Number of weeks (default: 4)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "dayOfWeek": 1,
        "dayName": "Monday",
        "averageSpending": 320.50,
        "transactionCount": 45
      }
    ]
  }
}
```

**Note:** `dayOfWeek` uses ISO 8601: 1=Monday, 7=Sunday

### Get Year-over-Year Comparison
```http
GET /api/analytics/year-over-year?statementId={id}&year={year}
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `statementId` (optional): Filter by statement
- `year` (optional): Year to compare (default: current year)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "comparisons": [
      {
        "month": "2024-11-01T00:00:00Z",
        "currentYear": 8500.50,
        "previousYear": 7800.25,
        "changePercent": 8.98
      }
    ]
  }
}
```

### Get Spending Forecast
```http
GET /api/analytics/forecast?statementId={id}
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "forecast": {
      "nextMonth": "2024-12-01T00:00:00Z",
      "predictedSpending": 8750.00,
      "confidence": 0.85,
      "byCategory": {
        "Gıda": 2500.00,
        "Ulaşım": 1500.00,
        "Alışveriş": 3000.00
      },
      "method": "moving_average",
      "monthsAnalyzed": 3
    }
  }
}
```

---

## 6. Error Handling

All endpoints return errors in this format:

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

**Common Error Codes:**
- `UNAUTHORIZED` (401): Missing or invalid token
- `FORBIDDEN` (403): Access denied
- `NOT_FOUND` (404): Resource not found
- `INVALID_REQUEST` (400): Invalid request data
- `FILE_TOO_LARGE` (413): File exceeds 10MB limit
- `STATEMENT_NOT_FOUND` (404): Statement doesn't exist

**HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict (duplicate)
- `413`: Payload Too Large
- `500`: Internal Server Error

---

## 7. File Selection Feature (CRITICAL)

The file selection feature allows users to view data for a specific uploaded statement file.

### How It Works:

1. **User uploads statement:**
   ```http
   POST /api/statements/upload
   → Returns: { "id": "stmt_123456", "status": "processing" }
   ```

2. **Wait for processing (poll status):**
   ```http
   GET /api/statements/stmt_123456
   → Check if status === "processed"
   ```

3. **User selects this statement/file:**
   - Store `statementId` in your app state: `selectedStatementId = "stmt_123456"`

4. **All subsequent API calls include statementId:**
   ```javascript
   // Get transactions for selected file
   GET /api/transactions?statementId=stmt_123456
   
   // Get summary for selected file
   GET /api/transactions/summary?statementId=stmt_123456
   
   // Get analytics for selected file
   GET /api/analytics/categories?statementId=stmt_123456
   GET /api/analytics/trends?statementId=stmt_123456
   // ... all analytics endpoints support statementId
   
   // Get budget comparison for selected file
   GET /api/budgets/compare?statementId=stmt_123456
   ```

5. **When no statementId is provided:**
   - Returns data for ALL user's transactions (across all statements)

### Implementation Example:

```javascript
// User selects a statement
const selectedStatementId = "stmt_123456";

// Fetch transactions for selected statement
const response = await fetch(
  `/api/transactions?statementId=${selectedStatementId}`,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  }
);

// Fetch analytics for selected statement
const analytics = await fetch(
  `/api/analytics/categories?statementId=${selectedStatementId}`,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  }
);
```

---

## 8. JavaScript/TypeScript Integration Examples

### Axios Example

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with auth
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

// Login
async function login(email, password) {
  const response = await api.post('/auth/login', { email, password });
  localStorage.setItem('access_token', response.data.data.access_token);
  localStorage.setItem('refresh_token', response.data.data.refresh_token);
  return response.data.data.user;
}

// Upload Statement
async function uploadStatement(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/statements/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  
  return response.data.data; // Returns statement with id and status
}

// Get Transactions (with file selection)
async function getTransactions(statementId = null) {
  const params = statementId ? { statementId } : {};
  const response = await api.get('/transactions', { params });
  return response.data.data.transactions;
}

// Get Analytics (with file selection)
async function getCategoryBreakdown(statementId = null) {
  const params = statementId ? { statementId } : {};
  const response = await api.get('/analytics/categories', { params });
  return response.data.data;
}
```

### Fetch API Example

```javascript
const API_BASE_URL = 'http://localhost:5000/api';

function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

// Upload Statement
async function uploadStatement(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/statements/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      // Don't set Content-Type for FormData - browser sets it automatically
    },
    body: formData
  });
  
  const data = await response.json();
  return data.data;
}

// Get Transactions with File Selection
async function getTransactions(statementId = null) {
  const url = new URL(`${API_BASE_URL}/transactions`);
  if (statementId) {
    url.searchParams.append('statementId', statementId);
  }
  
  const response = await fetch(url, {
    headers: getAuthHeaders()
  });
  
  const data = await response.json();
  return data.data.transactions;
}

// Poll Statement Status
async function waitForStatementProcessing(statementId, maxWait = 30000) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < maxWait) {
    const response = await fetch(`${API_BASE_URL}/statements/${statementId}`, {
      headers: getAuthHeaders()
    });
    
    const data = await response.json();
    const statement = data.data;
    
    if (statement.status === 'processed') {
      return statement;
    }
    
    if (statement.status === 'failed') {
      throw new Error('Statement processing failed');
    }
    
    // Wait 2 seconds before next poll
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  throw new Error('Statement processing timeout');
}
```

---

## 9. Date Format

All dates use **ISO 8601 format with 'Z' suffix** (UTC):
- Format: `YYYY-MM-DDTHH:MM:SSZ`
- Examples:
  - `"2024-11-01T00:00:00Z"`
  - `"2024-11-30T23:59:59Z"`

**JavaScript Date Conversion:**
```javascript
// Convert to Date object
const date = new Date("2024-11-01T00:00:00Z");

// Convert Date to API format
const apiDate = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
```

---

## 10. Transaction Categories (Turkish)

- `"Gıda"` - Food
- `"Ulaşım"` - Transport
- `"Alışveriş"` - Shopping
- `"Faturalar"` - Bills
- `"Eğlence"` - Entertainment
- `"Sağlık"` - Health
- `"Eğitim"` - Education
- `"Diğer"` - Other

---

## 11. Transaction Types

- `"income"` - Money received
- `"expense"` - Money spent

---

## 12. Complete Integration Flow Example

```javascript
// 1. User logs in
const user = await login(email, password);
// Store: access_token, refresh_token, user data

// 2. User uploads statement
const statement = await uploadStatement(file);
const statementId = statement.id; // e.g., "stmt_123456"

// 3. Wait for processing (poll status)
const processedStatement = await waitForStatementProcessing(statementId);
// Now status === "processed" and transactionCount > 0

// 4. User selects this statement
const selectedStatementId = statementId;

// 5. Fetch data for selected statement
const transactions = await getTransactions(selectedStatementId);
const summary = await getTransactionSummary(selectedStatementId);
const categories = await getCategoryBreakdown(selectedStatementId);
const trends = await getSpendingTrends(selectedStatementId);
const insights = await getFinancialInsights(selectedStatementId);

// 6. Display data in UI
// All data is filtered to the selected statement
```

---

## 13. File Upload Requirements

**Allowed File Types:**
- PDF (`.pdf`)
- Excel 2007+ (`.xlsx`)
- Excel 97-2003 (`.xls`)
- CSV (`.csv`)
- Word 2007+ (`.docx`)

**File Size Limit:** 10MB

**Upload Example:**
```javascript
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];

if (file.size > 10 * 1024 * 1024) {
  alert('File size exceeds 10MB limit');
  return;
}

const statement = await uploadStatement(file);
```

---

## 14. Error Handling Best Practices

```javascript
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      // Handle error
      if (response.status === 401) {
        // Token expired - try refresh
        await refreshToken();
        // Retry request
        return apiCall(url, options);
      }
      
      throw new Error(data.error?.message || 'Request failed');
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
```

---

## 15. Quick Reference

### Endpoints Summary

| Endpoint | Method | Auth | File Selection |
|----------|--------|------|----------------|
| `/auth/register` | POST | No | - |
| `/auth/login` | POST | No | - |
| `/auth/me` | GET | Yes | - |
| `/statements/upload` | POST | Yes | - |
| `/statements` | GET | Yes | - |
| `/statements/{id}` | GET | Yes | - |
| `/statements/{id}/delete` | POST | Yes | - |
| `/transactions` | GET | Yes | ✅ statementId |
| `/transactions/summary` | GET | Yes | ✅ statementId |
| `/budgets` | POST/GET | Yes | - |
| `/budgets/compare` | GET | Yes | ✅ statementId |
| `/budgets/{id}` | DELETE | Yes | - |
| `/analytics/categories` | GET | Yes | ✅ statementId |
| `/analytics/trends` | GET | Yes | ✅ statementId |
| `/analytics/insights` | GET | Yes | ✅ statementId |
| `/analytics/monthly-trends` | GET | Yes | ✅ statementId |
| `/analytics/category-trends` | GET | Yes | ✅ statementId |
| `/analytics/weekly-patterns` | GET | Yes | ✅ statementId |
| `/analytics/year-over-year` | GET | Yes | ✅ statementId |
| `/analytics/forecast` | GET | Yes | ✅ statementId |

---

## 16. Testing

Test your integration using the provided test script:
```bash
python test_all_endpoints.py
```

Or use Postman/Insomnia with the examples above.

---

## Support

For detailed API documentation, see:
- `docs/api/endpoints/` - Detailed endpoint documentation
- `docs/models/` - Data model documentation

For questions or issues, check server logs or contact the backend team.


