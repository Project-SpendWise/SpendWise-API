# Backend MVP Implementation Requirements

## Overview

This document specifies the backend requirements for the SpendWise MVP. The goal is to create a backend that:
1. Accepts file uploads and simulates processing (without real AI/ML)
2. Returns prepared mock data that matches the frontend's expected structure
3. Allows users to select uploaded files and view their associated data (like a profile selection)
4. Provides all analytics endpoints that return data for each tab/component in the frontend

**Important**: This is an MVP implementation. The file analyzer is **modular and fake** - it should be designed so it can be replaced with real AI/ML processing later without changing the rest of the system.

---

## What is Already Implemented (DO NOT RE-IMPLEMENT)

### 1. Authentication System ✅
The frontend already has a working authentication system connected to these endpoints:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns access_token, refresh_token, user data)
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update user profile
- `POST /auth/change-password` - Change password
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout user

**Response Format:**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "username": "username",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
}
```

**Error Format:**
```json
{
  "error": {
    "message": "Error description",
    "statusCode": 400,
    "errorCode": "INVALID_REQUEST"
  }
}
```

### 2. File Management System ✅
The frontend already has file upload/download functionality:

- `POST /files/upload` - Upload any file (multipart/form-data)
- `GET /files` - List files with pagination
- `GET /files/{fileId}` - Get file details
- `GET /files/{fileId}/download` - Download file
- `DELETE /files/{fileId}` - Delete file

**File Upload Response:**
```json
{
  "data": {
    "file": {
      "id": "file_123",
      "user_id": "user_123",
      "original_filename": "document.pdf",
      "stored_filename": "stored_abc123.pdf",
      "file_path": "/uploads/user_123/stored_abc123.pdf",
      "file_type": "pdf",
      "mime_type": "application/pdf",
      "file_size": 1024000,
      "file_hash": "abc123...",
      "processing_status": "pending",
      "description": null,
      "created_at": "2024-11-02T15:30:00Z",
      "updated_at": "2024-11-02T15:30:00Z"
    }
  }
}
```

**Note**: The file management system is separate from statement processing. Files are stored, but statements are the processed financial documents.

---

## What Needs to be Implemented

### Core Concept: File Selection & Profile System

The main idea is that users can:
1. Upload a file (bank statement, PDF, etc.)
2. The backend simulates analyzing it
3. Each uploaded file becomes a "profile" that can be selected
4. When a file is selected, all tabs (Home, Analytics) show data **specific to that file**
5. Users can switch between different uploaded files to see different data sets

**Flow:**
```
File Upload → Fake Analyzer → Store Transactions → Return Statement with Status
     ↓
User Selects File → Frontend Requests Data → Backend Returns File-Specific Data
```

---

## 1. Statement Upload & Processing System

### 1.1 Upload Statement Endpoint

**Endpoint:** `POST /statements/upload`

**Description:** Upload a bank statement file. The backend should:
1. Accept the file (any format - PDF, CSV, Excel, etc.)
2. Store it securely
3. Immediately return a response with status "processing"
4. Start async processing (fake analyzer)
5. Update status to "processed" when done

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Headers: `Authorization: Bearer <token>`
- Body:
  - `file`: File binary data

**Response (Immediate - Status: processing):**
```json
{
  "id": "stmt_123456",
  "fileName": "bank_statement_nov_2024.pdf",
  "uploadDate": "2024-11-02T15:30:00Z",
  "status": "processing",
  "transactionCount": null,
  "statementPeriodStart": null,
  "statementPeriodEnd": null
}
```

**Response (After Processing - Status: processed):**
```json
{
  "id": "stmt_123456",
  "fileName": "bank_statement_nov_2024.pdf",
  "uploadDate": "2024-11-02T15:30:00Z",
  "status": "processed",
  "transactionCount": 45,
  "statementPeriodStart": "2024-11-01T00:00:00Z",
  "statementPeriodEnd": "2024-11-30T23:59:59Z"
}
```

**Status Codes:**
- `200 OK`: Upload successful
- `400 Bad Request`: Invalid file format or missing file
- `401 Unauthorized`: Invalid or missing authentication token
- `413 Payload Too Large`: File size exceeds limit (max 10MB)
- `500 Internal Server Error`: Server error during processing

### 1.2 Fake Analyzer Module (Modular Design)

**IMPORTANT**: Design this as a **modular, replaceable component**. It should be easy to swap out the fake analyzer with a real AI/ML analyzer later.

**Interface/Contract:**
```python
class StatementAnalyzer:
    def analyze(self, file_path: str, user_id: str, statement_id: str) -> AnalysisResult:
        """
        Analyzes a statement file and extracts transactions.
        
        Returns:
            AnalysisResult with:
            - transactions: List[Transaction]
            - statement_period_start: DateTime
            - statement_period_end: DateTime
            - metadata: Dict
        """
        pass
```

**Fake Analyzer Implementation:**
1. Accept any file (don't actually parse it)
2. Simulate processing delay (2-5 seconds)
3. Generate mock transactions based on:
   - Statement ID (for consistency - same statement = same transactions)
   - User ID (optional - for user-specific patterns)
   - Current date (for realistic date ranges)
4. Return mock transaction data

**Mock Transaction Generation Rules:**
- Generate 30-60 transactions per statement
- Date range: Last 30 days from upload date
- Categories: Gıda, Ulaşım, Alışveriş, Faturalar, Eğlence, Sağlık, Eğitim, Diğer
- Include both income and expense transactions
- Use realistic Turkish merchant names and descriptions
- Amounts should be realistic (e.g., Gıda: 50-300 TL, Alışveriş: 200-2000 TL)

**Processing Flow:**
```
1. File uploaded → Store file → Create statement record (status: "processing")
2. Queue fake analyzer job (async)
3. Fake analyzer generates mock transactions
4. Store transactions linked to statement_id
5. Update statement status to "processed"
6. (Optional) Notify frontend via webhook or polling
```

### 1.3 Get Statements List

**Endpoint:** `GET /statements`

**Description:** Get all statements uploaded by the authenticated user.

**Response:**
```json
{
  "statements": [
    {
      "id": "stmt_123456",
      "fileName": "bank_statement_nov_2024.pdf",
      "uploadDate": "2024-11-02T15:30:00Z",
      "statementPeriodStart": "2024-11-01T00:00:00Z",
      "statementPeriodEnd": "2024-11-30T23:59:59Z",
      "transactionCount": 45,
      "status": "processed",
      "isProcessed": true
    },
    {
      "id": "stmt_123457",
      "fileName": "bank_statement_oct_2024.pdf",
      "uploadDate": "2024-10-02T10:15:00Z",
      "statementPeriodStart": "2024-10-01T00:00:00Z",
      "statementPeriodEnd": "2024-10-31T23:59:59Z",
      "transactionCount": 38,
      "status": "processed",
      "isProcessed": true
    }
  ]
}
```

### 1.4 Get Statement Details

**Endpoint:** `GET /statements/{statementId}`

**Description:** Get details of a specific statement, including current processing status.

**Response:**
```json
{
  "id": "stmt_123456",
  "fileName": "bank_statement_nov_2024.pdf",
  "uploadDate": "2024-11-02T15:30:00Z",
  "status": "processed",
  "transactionCount": 45,
  "statementPeriodStart": "2024-11-01T00:00:00Z",
  "statementPeriodEnd": "2024-11-30T23:59:59Z",
  "isProcessed": true
}
```

### 1.5 Delete Statement

**Endpoint:** `POST /statements/{statementId}/delete`

**Description:** Delete a statement and all its associated transactions.

**Response:**
```json
{
  "success": true,
  "message": "Statement deleted successfully"
}
```

---

## 2. Transaction Endpoints (File-Specific Data)

### 2.1 Get Transactions

**Endpoint:** `GET /transactions`

**Description:** Get transactions. **CRITICAL**: If `statementId` query parameter is provided, return only transactions for that statement. Otherwise, return all transactions for the user.

**Query Parameters:**
- `statementId` (optional): Filter by specific statement ID (for file selection)
- `startDate` (optional): ISO 8601 date string - Filter transactions from this date
- `endDate` (optional): ISO 8601 date string - Filter transactions until this date
- `category` (optional): Category name - Filter by category
- `account` (optional): Account name - Filter by account
- `limit` (optional): Integer - Maximum number of results (default: 50)
- `offset` (optional): Integer - Number of results to skip (default: 0)

**Example Request:**
```
GET /transactions?statementId=stmt_123456&startDate=2024-11-01T00:00:00Z&limit=20&offset=0
```

**Response:**
```json
{
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
    },
    {
      "id": "txn_123457",
      "date": "2024-11-01T14:20:00Z",
      "description": "IstanbulKart Yükleme",
      "amount": 200.00,
      "type": "expense",
      "category": "Ulaşım",
      "account": "Ana Hesap",
      "referenceNumber": "REF123457",
      "statementId": "stmt_123456"
    }
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

### 2.2 Get Transaction Summary

**Endpoint:** `GET /transactions/summary`

**Description:** Get aggregated summary. **CRITICAL**: If `statementId` is provided, calculate summary only for that statement's transactions.

**Query Parameters:**
- `statementId` (optional): Filter by specific statement ID
- `startDate` (optional): ISO 8601 date string
- `endDate` (optional): ISO 8601 date string

**Response:**
```json
{
  "totalIncome": 15000.00,
  "totalExpenses": 8500.50,
  "savings": 6499.50,
  "transactionCount": 45,
  "period": {
    "start": "2024-11-01T00:00:00Z",
    "end": "2024-11-30T23:59:59Z"
  }
}
```

---

## 3. Analytics Endpoints (File-Specific Data)

**IMPORTANT**: All analytics endpoints should accept an optional `statementId` query parameter. When provided, return analytics data **only for that statement's transactions**. This enables the file selection/profile feature.

### 3.1 Get Category Breakdown

**Endpoint:** `GET /analytics/categories`

**Query Parameters:**
- `statementId` (optional): Filter by statement ID
- `startDate` (optional): ISO 8601 date string
- `endDate` (optional): ISO 8601 date string

**Response:**
```json
{
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
    },
    {
      "category": "Alışveriş",
      "totalAmount": 4299.99,
      "percentage": 50.6,
      "transactionCount": 5
    }
  ],
  "totalExpenses": 8500.50
}
```

### 3.2 Get Spending Trends

**Endpoint:** `GET /analytics/trends`

**Query Parameters:**
- `statementId` (optional): Filter by statement ID
- `startDate` (optional): ISO 8601 date string
- `endDate` (optional): ISO 8601 date string
- `period` (optional): Aggregation period (`day`, `week`, `month`) - Default: `day`

**Response:**
```json
{
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
```

### 3.3 Get Financial Insights

**Endpoint:** `GET /analytics/insights`

**Query Parameters:**
- `statementId` (optional): Filter by statement ID
- `startDate` (optional): ISO 8601 date string
- `endDate` (optional): ISO 8601 date string

**Response:**
```json
{
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
      "message": "You spend the most in Alışveriş category. You can review your expenses in this category.",
      "severity": "info"
    }
  ]
}
```

**Insight Types:**
- `low_savings_rate`: Savings percentage below recommended threshold
- `excessive_spending`: Expenses exceed income
- `highest_spending_category`: Category with highest spending
- `great_savings`: Savings rate is optimal

**Severity Levels:**
- `info`: Informational insight
- `warning`: Cautionary insight
- `error`: Critical issue
- `success`: Positive feedback

### 3.4 Get Monthly Trends

**Endpoint:** `GET /analytics/monthly-trends`

**Query Parameters:**
- `statementId` (optional): Filter by statement ID
- `months` (optional): Integer - Number of months to retrieve (default: 12, max: 24)

**Response:**
```json
{
  "monthlyData": [
    {
      "month": "2024-11-01T00:00:00Z",
      "income": 15000.00,
      "expenses": 8500.50,
      "savings": 6499.50
    },
    {
      "month": "2024-10-01T00:00:00Z",
      "income": 14500.00,
      "expenses": 9200.25,
      "savings": 5299.75
    }
  ]
}
```

### 3.5 Get Category Trends Over Time

**Endpoint:** `GET /analytics/category-trends`

**Query Parameters:**
- `statementId` (optional): Filter by statement ID
- `topCategories` (optional): Integer - Number of top categories (default: 5, max: 10)
- `months` (optional): Integer - Number of months (default: 12)

**Response:**
```json
{
  "categoryTrends": [
    {
      "categoryName": "Gıda",
      "monthlyData": [
        {
          "month": "2024-11-01T00:00:00Z",
          "amount": 2450.50
        },
        {
          "month": "2024-10-01T00:00:00Z",
          "amount": 2300.00
        }
      ]
    },
    {
      "categoryName": "Alışveriş",
      "monthlyData": [
        {
          "month": "2024-11-01T00:00:00Z",
          "amount": 4299.99
        }
      ]
    }
  ]
}
```

### 3.6 Get Weekly Patterns

**Endpoint:** `GET /analytics/weekly-patterns`

**Query Parameters:**
- `statementId` (optional): Filter by statement ID
- `weeks` (optional): Integer - Number of weeks to analyze (default: 4)

**Response:**
```json
{
  "patterns": [
    {
      "dayOfWeek": 1,
      "dayName": "Monday",
      "averageSpending": 320.50,
      "transactionCount": 45
    },
    {
      "dayOfWeek": 2,
      "dayName": "Tuesday",
      "averageSpending": 285.75,
      "transactionCount": 38
    },
    {
      "dayOfWeek": 6,
      "dayName": "Saturday",
      "averageSpending": 450.25,
      "transactionCount": 52
    }
  ]
}
```

**Note:** `dayOfWeek` uses ISO 8601 standard: 1 = Monday, 7 = Sunday

### 3.7 Get Year-over-Year Comparison

**Endpoint:** `GET /analytics/year-over-year`

**Query Parameters:**
- `statementId` (optional): Filter by statement ID
- `year` (optional): Integer - Year to compare (default: current year)

**Response:**
```json
{
  "comparisons": [
    {
      "month": "2024-11-01T00:00:00Z",
      "currentYear": 8500.50,
      "previousYear": 7800.25,
      "changePercent": 8.98
    },
    {
      "month": "2024-10-01T00:00:00Z",
      "currentYear": 9200.25,
      "previousYear": 8900.00,
      "changePercent": 3.37
    }
  ]
}
```

### 3.8 Get Spending Forecast

**Endpoint:** `GET /analytics/forecast`

**Query Parameters:**
- `statementId` (optional): Filter by statement ID

**Response:**
```json
{
  "forecast": {
    "nextMonth": "2024-12-01T00:00:00Z",
    "predictedSpending": 8750.00,
    "confidence": 0.85,
    "byCategory": {
      "Gıda": 2500.00,
      "Ulaşım": 1500.00,
      "Alışveriş": 3000.00,
      "Faturalar": 1200.00,
      "Eğlence": 550.00
    },
    "method": "moving_average",
    "monthsAnalyzed": 3
  }
}
```

---

## 4. Budget Management Endpoints

### 4.1 Create/Update Budget

**Endpoint:** `POST /budgets`

**Description:** Create or update a budget for a category.

**Request Body:**
```json
{
  "categoryId": "food",
  "categoryName": "Gıda",
  "amount": 2500.00,
  "period": "monthly",
  "startDate": "2024-11-01T00:00:00Z"
}
```

**Response:**
```json
{
  "id": "budget_food_monthly",
  "categoryId": "food",
  "categoryName": "Gıda",
  "amount": 2500.00,
  "period": "monthly",
  "startDate": "2024-11-01T00:00:00Z",
  "createdAt": "2024-11-01T10:00:00Z",
  "updatedAt": "2024-11-01T10:00:00Z"
}
```

### 4.2 Get Budgets

**Endpoint:** `GET /budgets`

**Query Parameters:**
- `period` (optional): Filter by period (`monthly`, `yearly`)
- `categoryId` (optional): Filter by category

**Response:**
```json
{
  "budgets": [
    {
      "id": "budget_food_monthly",
      "categoryId": "food",
      "categoryName": "Gıda",
      "amount": 2500.00,
      "period": "monthly",
      "startDate": "2024-11-01T00:00:00Z"
    }
  ]
}
```

### 4.3 Get Budget vs Actual

**Endpoint:** `GET /budgets/compare`

**Description:** Get budget comparison for current period. **CRITICAL**: If `statementId` is provided, compare against that statement's transactions only.

**Query Parameters:**
- `statementId` (optional): Filter by statement ID
- `period` (optional): Period type (`monthly`, `yearly`)
- `startDate` (optional): ISO 8601 date string
- `endDate` (optional): ISO 8601 date string

**Response:**
```json
{
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
    },
    {
      "budget": {
        "id": "budget_shopping_monthly",
        "categoryId": "shopping",
        "categoryName": "Alışveriş",
        "amount": 2000.00
      },
      "actualSpending": 2500.00,
      "remaining": -500.00,
      "percentageUsed": 125.00,
      "isOverBudget": true,
      "status": "over_budget"
    }
  ],
  "period": {
    "start": "2024-11-01T00:00:00Z",
    "end": "2024-11-30T23:59:59Z"
  }
}
```

**Status Values:**
- `on_track`: Spending is within budget
- `approaching_budget`: 80-100% of budget used
- `over_budget`: Spending exceeds budget

### 4.4 Delete Budget

**Endpoint:** `DELETE /budgets/{budgetId}`

**Response:**
```json
{
  "success": true,
  "message": "Budget deleted successfully"
}
```

---

## Database Schema Requirements

### Statements Table
```sql
CREATE TABLE statements (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    file_name VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    upload_date TIMESTAMP DEFAULT NOW(),
    statement_period_start TIMESTAMP,
    statement_period_end TIMESTAMP,
    transaction_count INT DEFAULT 0,
    status ENUM('processing', 'processed', 'failed') DEFAULT 'processing',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user (user_id),
    INDEX idx_status (status)
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    statement_id VARCHAR NOT NULL,  -- CRITICAL: Links transaction to statement
    date TIMESTAMP NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    category VARCHAR,
    merchant VARCHAR,
    account VARCHAR,
    reference_number VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_date (user_id, date),
    INDEX idx_user_category (user_id, category),
    INDEX idx_statement (statement_id),  -- CRITICAL: For file filtering
    FOREIGN KEY (statement_id) REFERENCES statements(id) ON DELETE CASCADE
);
```

### Budgets Table
```sql
CREATE TABLE budgets (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    category_id VARCHAR NOT NULL,
    category_name VARCHAR NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    period ENUM('monthly', 'yearly') NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_category (user_id, category_id),
    INDEX idx_user_period (user_id, period)
);
```

---

## Mock Data Generation Guidelines

When the fake analyzer generates transactions, follow these patterns:

### Categories (Turkish)
- **Gıda** (Food): 50-300 TL per transaction, 2-3 transactions per day
- **Ulaşım** (Transport): 30-200 TL per transaction, 1-2 transactions per day
- **Alışveriş** (Shopping): 200-2000 TL per transaction, 1-2 transactions per week
- **Faturalar** (Bills): 100-500 TL per transaction, 4-5 transactions per month (on 1st-5th of month)
- **Eğlence** (Entertainment): 100-500 TL per transaction, 2-3 transactions per week (more on weekends)
- **Sağlık** (Health): 150-600 TL per transaction, 1-2 transactions per month
- **Eğitim** (Education): 200-450 TL per transaction, 1-2 transactions per month
- **Diğer** (Other): 100-500 TL per transaction, occasional

### Income
- Monthly salary: 14000-15000 TL, on 1st of month
- Occasional bonuses or other income

### Date Patterns
- Generate transactions for last 30 days from upload date
- More transactions on weekends (Eğlence, Gıda)
- Bills on 1st-5th of month
- Income on 1st of month

### Merchant Names (Turkish Examples)
- Gıda: "Migros Market Alışverişi", "Getir Yemek", "CarrefourSA", "Bim Market"
- Ulaşım: "IstanbulKart Yükleme", "Uber Yolculuk", "Benzin İstasyonu"
- Alışveriş: "Amazon.com.tr", "H&M Mağaza", "Teknosa", "MediaMarkt"
- Eğlence: "Sinema Bileti", "Netflix Abonelik", "Spotify Premium", "Kafe"

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Set up database with required tables
- [ ] Implement statement upload endpoint
- [ ] Create fake analyzer module (modular design)
- [ ] Implement async processing queue/job system
- [ ] Implement statement status updates

### Phase 2: Transaction System
- [ ] Implement transaction storage (linked to statements)
- [ ] Implement GET /transactions with statementId filtering
- [ ] Implement GET /transactions/summary with statementId filtering
- [ ] Test file selection feature

### Phase 3: Analytics Endpoints
- [ ] Implement GET /analytics/categories (with statementId support)
- [ ] Implement GET /analytics/trends (with statementId support)
- [ ] Implement GET /analytics/insights (with statementId support)
- [ ] Implement GET /analytics/monthly-trends (with statementId support)
- [ ] Implement GET /analytics/category-trends (with statementId support)
- [ ] Implement GET /analytics/weekly-patterns (with statementId support)
- [ ] Implement GET /analytics/year-over-year (with statementId support)
- [ ] Implement GET /analytics/forecast (with statementId support)

### Phase 4: Budget System
- [ ] Implement POST /budgets
- [ ] Implement GET /budgets
- [ ] Implement GET /budgets/compare (with statementId support)
- [ ] Implement DELETE /budgets/{id}

### Phase 5: Statement Management
- [ ] Implement GET /statements
- [ ] Implement GET /statements/{id}
- [ ] Implement POST /statements/{id}/delete

### Phase 6: Testing
- [ ] Test file upload and processing flow
- [ ] Test file selection and data filtering
- [ ] Test all analytics endpoints with statementId
- [ ] Test error handling
- [ ] Test authentication on all endpoints

---

## Important Notes

1. **Modular Analyzer**: Design the fake analyzer as a separate module/service that can be easily replaced. Use dependency injection or a plugin architecture.

2. **Statement ID Filtering**: **CRITICAL** - All transaction and analytics endpoints must support `statementId` query parameter for the file selection feature to work.

3. **Status Progression**: Statement status should progress: `processing` → `processed` (or `failed`). Frontend may poll `GET /statements/{id}` to check status.

4. **Data Consistency**: When generating mock transactions for a statement, ensure:
   - Same statement ID always generates the same transactions (use statement ID as seed)
   - Transactions are realistic and consistent
   - Date ranges match the statement period

5. **Error Handling**: All endpoints should return proper error responses in the format specified in the Authentication section.

6. **Authentication**: All endpoints (except auth endpoints) require `Authorization: Bearer <token>` header.

7. **File Storage**: Store uploaded files securely. Consider using cloud storage (S3, etc.) or local secure storage.

8. **Performance**: Analytics calculations should be efficient. Consider caching or pre-calculating aggregations for better performance.

---

## Example Implementation Flow

```
1. User uploads file via POST /statements/upload
   → Backend stores file
   → Creates statement record (status: "processing")
   → Returns statement ID immediately

2. Backend queues fake analyzer job
   → Analyzer generates mock transactions
   → Stores transactions with statement_id
   → Updates statement status to "processed"

3. User selects file in frontend
   → Frontend calls GET /transactions?statementId=stmt_123
   → Backend returns only transactions for that statement

4. Frontend displays data in tabs
   → Home tab: GET /transactions/summary?statementId=stmt_123
   → Analytics tab: GET /analytics/categories?statementId=stmt_123
   → All data is filtered to that specific file
```

---

## Questions or Clarifications?

If you need clarification on any part of this specification, please refer to:
- `docs/BACKEND_API.md` - Full API documentation
- Frontend code in `lib/data/services/` - See expected request/response formats
- Frontend models in `lib/data/models/` - See data structures

