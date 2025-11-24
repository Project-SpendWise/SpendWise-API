# Budget Endpoints

Complete reference for all budget management endpoints. Budgets allow users to set spending limits for categories and track actual spending against those limits.

## Create/Update Budget

Create or update a budget for a category.

**Endpoint:** `POST /api/budgets`

**Authentication:** Required (Access Token)

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

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `categoryId` | string | Yes | Unique identifier for the category |
| `categoryName` | string | Yes | Display name of the category |
| `amount` | number | Yes | Budget amount (must be > 0) |
| `period` | string | Yes | Budget period: `"monthly"` or `"yearly"` |
| `startDate` | string (ISO 8601) | Yes | Start date of the budget period |

**Success Response (200):**

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
    "endDate": "2024-11-30T23:59:59Z",
    "createdAt": "2024-11-01T10:00:00Z",
    "updatedAt": "2024-11-01T10:00:00Z"
  },
  "message": "Budget saved successfully",
  "metadata": {
    "timestamp": "2024-11-01T10:00:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `400`: Missing required fields, invalid amount, invalid period, invalid date format
- `401`: Missing or invalid token
- `500`: Database error

**Example:**

```bash
curl -X POST http://localhost:5000/api/budgets \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "categoryId": "food",
    "categoryName": "Gıda",
    "amount": 2500.00,
    "period": "monthly",
    "startDate": "2024-11-01T00:00:00Z"
  }'
```

**Note:** If a budget already exists for the same user, category, and period, it will be updated instead of creating a new one.

---

## List Budgets

Get all budgets for the authenticated user.

**Endpoint:** `GET /api/budgets`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `period` | string | Filter by period (`monthly` or `yearly`) | None (all periods) |
| `categoryId` | string | Filter by category ID | None (all categories) |

**Success Response (200):**

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
      },
      {
        "id": "budget_shopping_monthly",
        "categoryId": "shopping",
        "categoryName": "Alışveriş",
        "amount": 2000.00,
        "period": "monthly",
        "startDate": "2024-11-01T00:00:00Z",
        "endDate": "2024-11-30T23:59:59Z"
      }
    ]
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Missing or invalid token

**Examples:**

```bash
# Get all budgets
curl -X GET http://localhost:5000/api/budgets \
  -H "Authorization: Bearer <access_token>"

# Get monthly budgets only
curl -X GET "http://localhost:5000/api/budgets?period=monthly" \
  -H "Authorization: Bearer <access_token>"

# Get budget for specific category
curl -X GET "http://localhost:5000/api/budgets?categoryId=food" \
  -H "Authorization: Bearer <access_token>"
```

---

## Get Budget vs Actual

Get budget comparison for current period, showing actual spending vs budgeted amounts.

**Endpoint:** `GET /api/budgets/compare`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | **CRITICAL**: Filter by specific statement ID | None (all transactions) |
| `period` | string | Period type (`monthly` or `yearly`) | `monthly` |
| `startDate` | string (ISO 8601) | Start date for comparison | Current month start |
| `endDate` | string (ISO 8601) | End date for comparison | Current month end |

**Success Response (200):**

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
# Get budget comparison for all transactions
curl -X GET http://localhost:5000/api/budgets/compare \
  -H "Authorization: Bearer <access_token>"

# Get budget comparison for a specific statement
curl -X GET "http://localhost:5000/api/budgets/compare?statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"

# Get budget comparison with custom date range
curl -X GET "http://localhost:5000/api/budgets/compare?startDate=2024-11-01T00:00:00Z&endDate=2024-11-30T23:59:59Z" \
  -H "Authorization: Bearer <access_token>"
```

**CRITICAL: Statement ID Filtering**

When `statementId` is provided:
- Compares budgets against transactions from that specific statement only
- Uses statement's period dates if no date range is provided
- Enables file-specific budget tracking

**Status Values:**

- `on_track`: Spending is within budget (< 80% used)
- `approaching_budget`: 80-100% of budget used
- `over_budget`: Spending exceeds budget (> 100% used)

**Comparison Fields:**

- `actualSpending`: Sum of expense transactions for the category
- `remaining`: Budget amount minus actual spending (negative if over budget)
- `percentageUsed`: Percentage of budget used (can exceed 100%)
- `isOverBudget`: Boolean indicating if spending exceeds budget
- `status`: Current budget status

---

## Delete Budget

Delete a budget.

**Endpoint:** `DELETE /api/budgets/{budgetId}`

**Authentication:** Required (Access Token)

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "success": true,
    "message": "Budget deleted successfully"
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Missing or invalid token
- `403`: Budget belongs to another user
- `404`: Budget not found

**Example:**

```bash
curl -X DELETE http://localhost:5000/api/budgets/budget_food_monthly \
  -H "Authorization: Bearer <access_token>"
```

---

## Budget Ownership

All budget operations verify ownership:
- Users can only access budgets they created
- `budget.user_id` must match the authenticated user's ID
- Attempts to access other users' budgets return `403 Forbidden`

---

## Budget Periods

**Monthly Budget:**
- Covers one calendar month
- `endDate` is automatically calculated as the last day of the month
- Example: `startDate: 2024-11-01` → `endDate: 2024-11-30`

**Yearly Budget:**
- Covers one calendar year
- `endDate` is automatically calculated as December 31st
- Example: `startDate: 2024-01-01` → `endDate: 2024-12-31`

