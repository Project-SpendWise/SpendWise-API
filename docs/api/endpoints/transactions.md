# Transaction Endpoints

Complete reference for all transaction query endpoints. Transactions represent individual financial transactions extracted from bank statements.

## Get Transactions

Get transactions with filtering and pagination.

**Endpoint:** `GET /api/transactions`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | **CRITICAL**: Filter by specific statement ID (for file selection) | None (all transactions) |
| `startDate` | string (ISO 8601) | Filter transactions from this date | None |
| `endDate` | string (ISO 8601) | Filter transactions until this date | None |
| `category` | string | Filter by category name | None |
| `account` | string | Filter by account name | None |
| `limit` | integer | Maximum number of results (max 100) | 50 |
| `offset` | integer | Number of results to skip | 0 |

**Success Response (200):**

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
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `400`: Invalid date format
- `401`: Missing or invalid token
- `403`: Statement belongs to another user (if statementId provided)
- `404`: Statement not found (if statementId provided)

**Examples:**

```bash
# Get all transactions
curl -X GET http://localhost:5000/api/transactions \
  -H "Authorization: Bearer <access_token>"

# Get transactions for a specific statement (file selection)
curl -X GET "http://localhost:5000/api/transactions?statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"

# Get transactions with date range
curl -X GET "http://localhost:5000/api/transactions?startDate=2024-11-01T00:00:00Z&endDate=2024-11-30T23:59:59Z" \
  -H "Authorization: Bearer <access_token>"

# Get transactions by category
curl -X GET "http://localhost:5000/api/transactions?category=Gıda" \
  -H "Authorization: Bearer <access_token>"

# Get transactions with pagination
curl -X GET "http://localhost:5000/api/transactions?limit=20&offset=0" \
  -H "Authorization: Bearer <access_token>"

# Combined filters
curl -X GET "http://localhost:5000/api/transactions?statementId=stmt_123456&startDate=2024-11-01T00:00:00Z&limit=20&offset=0" \
  -H "Authorization: Bearer <access_token>"
```

**CRITICAL: Statement ID Filtering**

The `statementId` parameter is essential for the file selection feature:
- When provided, returns only transactions from that specific statement
- Enables users to view data for a selected file/profile
- All other filters (date, category, etc.) work in combination with statementId

**Transaction Types:**

- `income`: Money received (salary, bonuses, etc.)
- `expense`: Money spent (purchases, bills, etc.)

**Categories (Turkish):**

- Gıda (Food)
- Ulaşım (Transport)
- Alışveriş (Shopping)
- Faturalar (Bills)
- Eğlence (Entertainment)
- Sağlık (Health)
- Eğitim (Education)
- Diğer (Other)

---

## Get Transaction Summary

Get aggregated summary of transactions.

**Endpoint:** `GET /api/transactions/summary`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | **CRITICAL**: Filter by specific statement ID | None (all transactions) |
| `startDate` | string (ISO 8601) | Filter transactions from this date | None |
| `endDate` | string (ISO 8601) | Filter transactions until this date | None |

**Success Response (200):**

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
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `400`: Invalid date format
- `401`: Missing or invalid token
- `403`: Statement belongs to another user (if statementId provided)
- `404`: Statement not found (if statementId provided)

**Examples:**

```bash
# Get summary for all transactions
curl -X GET http://localhost:5000/api/transactions/summary \
  -H "Authorization: Bearer <access_token>"

# Get summary for a specific statement
curl -X GET "http://localhost:5000/api/transactions/summary?statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"

# Get summary with date range
curl -X GET "http://localhost:5000/api/transactions/summary?startDate=2024-11-01T00:00:00Z&endDate=2024-11-30T23:59:59Z" \
  -H "Authorization: Bearer <access_token>"
```

**CRITICAL: Statement ID Filtering**

When `statementId` is provided:
- Calculates summary only for that statement's transactions
- Uses statement's period dates if no date range is provided
- Enables file-specific financial summaries

**Summary Fields:**

- `totalIncome`: Sum of all income transactions
- `totalExpenses`: Sum of all expense transactions
- `savings`: Calculated as `totalIncome - totalExpenses`
- `transactionCount`: Total number of transactions
- `period`: Date range used for calculation (if provided)

---

## Transaction Ownership

All transaction operations verify ownership:
- Users can only access transactions from their own statements
- Transactions are automatically filtered by `user_id`
- Attempts to access other users' transactions return `403 Forbidden`

---

## Date Format

All date parameters use ISO 8601 format:
- Format: `YYYY-MM-DDTHH:MM:SSZ` or `YYYY-MM-DDTHH:MM:SS+00:00`
- Examples:
  - `2024-11-01T00:00:00Z`
  - `2024-11-30T23:59:59Z`
  - `2024-11-01T00:00:00+00:00`

---

## Pagination

Transactions endpoint supports pagination:
- `limit`: Maximum number of results per page (default: 50, max: 100)
- `offset`: Number of results to skip (default: 0)
- Response includes `total` count for calculating total pages

**Example Pagination:**

```bash
# Page 1 (first 20 results)
GET /api/transactions?limit=20&offset=0

# Page 2 (next 20 results)
GET /api/transactions?limit=20&offset=20

# Page 3 (next 20 results)
GET /api/transactions?limit=20&offset=40
```

