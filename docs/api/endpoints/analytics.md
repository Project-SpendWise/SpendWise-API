# Analytics Endpoints

Complete reference for all analytics endpoints. Analytics provide insights into spending patterns, trends, and financial health.

**IMPORTANT**: All analytics endpoints support the `statementId` query parameter for file selection. When provided, analytics are calculated only for that statement's transactions.

## Get Category Breakdown

Get spending breakdown by category with percentages.

**Endpoint:** `GET /api/analytics/categories`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | Filter by specific statement ID | None (all transactions) |
| `startDate` | string (ISO 8601) | Filter from this date | None |
| `endDate` | string (ISO 8601) | Filter until this date | None |

**Success Response (200):**

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
      },
      {
        "category": "Alışveriş",
        "totalAmount": 4299.99,
        "percentage": 50.6,
        "transactionCount": 5
      }
    ],
    "totalExpenses": 8500.50
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:5000/api/analytics/categories?statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"
```

---

## Get Spending Trends

Get spending trends aggregated by day, week, or month.

**Endpoint:** `GET /api/analytics/trends`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | Filter by specific statement ID | None |
| `startDate` | string (ISO 8601) | Filter from this date | None |
| `endDate` | string (ISO 8601) | Filter until this date | None |
| `period` | string | Aggregation period: `day`, `week`, or `month` | `day` |

**Success Response (200):**

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
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:5000/api/analytics/trends?period=week&statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"
```

---

## Get Financial Insights

Get automated financial insights and recommendations.

**Endpoint:** `GET /api/analytics/insights`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | Filter by specific statement ID | None |
| `startDate` | string (ISO 8601) | Filter from this date | None |
| `endDate` | string (ISO 8601) | Filter until this date | None |

**Success Response (200):**

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
        "message": "You spend the most in Alışveriş category. You can review your expenses in this category.",
        "severity": "info"
      }
    ]
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Insight Types:**

- `low_savings_rate`: Savings percentage below recommended threshold (< 20%)
- `excessive_spending`: Expenses exceed income
- `highest_spending_category`: Category with highest spending
- `great_savings`: Savings rate is optimal (≥ 20%)

**Severity Levels:**

- `info`: Informational insight
- `warning`: Cautionary insight
- `error`: Critical issue
- `success`: Positive feedback

**Example:**

```bash
curl -X GET "http://localhost:5000/api/analytics/insights?statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"
```

---

## Get Monthly Trends

Get monthly income, expenses, and savings trends.

**Endpoint:** `GET /api/analytics/monthly-trends`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | Filter by specific statement ID | None |
| `months` | integer | Number of months to retrieve (max 24) | 12 |

**Success Response (200):**

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
      },
      {
        "month": "2024-10-01T00:00:00Z",
        "income": 14500.00,
        "expenses": 9200.25,
        "savings": 5299.75
      }
    ]
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:5000/api/analytics/monthly-trends?months=6&statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"
```

---

## Get Category Trends Over Time

Get spending trends for top categories over multiple months.

**Endpoint:** `GET /api/analytics/category-trends`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | Filter by specific statement ID | None |
| `topCategories` | integer | Number of top categories (max 10) | 5 |
| `months` | integer | Number of months to analyze | 12 |

**Success Response (200):**

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
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:5000/api/analytics/category-trends?topCategories=5&months=12&statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"
```

---

## Get Weekly Patterns

Get day-of-week spending patterns.

**Endpoint:** `GET /api/analytics/weekly-patterns`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | Filter by specific statement ID | None |
| `weeks` | integer | Number of weeks to analyze | 4 |

**Success Response (200):**

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
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Note:** `dayOfWeek` uses ISO 8601 standard: 1 = Monday, 7 = Sunday

**Example:**

```bash
curl -X GET "http://localhost:5000/api/analytics/weekly-patterns?weeks=8&statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"
```

---

## Get Year-over-Year Comparison

Compare spending year-over-year by month.

**Endpoint:** `GET /api/analytics/year-over-year`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | Filter by specific statement ID | None |
| `year` | integer | Year to compare | Current year |

**Success Response (200):**

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
      },
      {
        "month": "2024-10-01T00:00:00Z",
        "currentYear": 9200.25,
        "previousYear": 8900.00,
        "changePercent": 3.37
      }
    ]
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:5000/api/analytics/year-over-year?year=2024&statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"
```

---

## Get Spending Forecast

Get predicted spending for the next month based on historical data.

**Endpoint:** `GET /api/analytics/forecast`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `statementId` | string | Filter by specific statement ID | None |

**Success Response (200):**

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
        "Alışveriş": 3000.00,
        "Faturalar": 1200.00,
        "Eğlence": 550.00
      },
      "method": "moving_average",
      "monthsAnalyzed": 3
    }
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:5000/api/analytics/forecast?statementId=stmt_123456" \
  -H "Authorization: Bearer <access_token>"
```

**Forecast Method:**

- Uses moving average of last 3 months
- Calculates average spending per category
- Confidence score indicates prediction reliability

---

## Common Query Parameters

All analytics endpoints support:

- `statementId`: Filter by specific statement (enables file selection)
- `startDate`: Filter transactions from this date (ISO 8601)
- `endDate`: Filter transactions until this date (ISO 8601)

When `statementId` is provided:
- Analytics are calculated only for that statement's transactions
- Statement's period dates are used if no date range is provided
- Enables file-specific analytics

---

## Error Responses

All analytics endpoints may return:

- `400`: Invalid date format or invalid parameter value
- `401`: Missing or invalid token
- `403`: Statement belongs to another user (if statementId provided)
- `404`: Statement not found (if statementId provided)
- `500`: Server error

---

## Analytics Ownership

All analytics operations verify ownership:
- Users can only view analytics for their own transactions
- Transactions are automatically filtered by `user_id`
- Attempts to access other users' data return `403 Forbidden`

