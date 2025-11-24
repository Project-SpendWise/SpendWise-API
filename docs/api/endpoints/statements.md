# Statement Endpoints

Complete reference for all statement management endpoints. Statements represent uploaded bank statement files that are processed to extract transactions.

## Upload Statement

Upload a bank statement file for processing.

**Endpoint:** `POST /api/statements/upload`

**Authentication:** Required (Access Token)

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file` (required): The statement file to upload (PDF, CSV, Excel, etc.)

**Allowed File Types:**
- PDF (`.pdf`)
- Excel 2007+ (`.xlsx`)
- Excel 97-2003 (`.xls`)
- CSV (`.csv`)
- Word 2007+ (`.docx`)

**File Size Limit:** 10MB

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "stmt_123456",
    "fileName": "bank_statement_nov_2024.pdf",
    "uploadDate": "2024-11-02T15:30:00Z",
    "status": "processing",
    "transactionCount": null,
    "statementPeriodStart": null,
    "statementPeriodEnd": null,
    "isProcessed": false
  },
  "message": "Statement uploaded successfully",
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**After Processing (status: processed):**

```json
{
  "success": true,
  "data": {
    "id": "stmt_123456",
    "fileName": "bank_statement_nov_2024.pdf",
    "uploadDate": "2024-11-02T15:30:00Z",
    "status": "processed",
    "transactionCount": 45,
    "statementPeriodStart": "2024-11-01T00:00:00Z",
    "statementPeriodEnd": "2024-11-30T23:59:59Z",
    "isProcessed": true
  }
}
```

**Error Responses:**

- `400`: No file provided, invalid file type, file too large
- `401`: Missing or invalid token
- `413`: File size exceeds maximum allowed size
- `500`: Server error during processing

**Example:**

```bash
curl -X POST http://localhost:5000/api/statements/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/bank_statement.pdf"
```

**Processing Flow:**

1. File is uploaded and stored securely
2. Statement record is created with status "processing"
3. Response is returned immediately
4. Background job processes the file using fake analyzer
5. Mock transactions are generated and stored
6. Statement status is updated to "processed"

**Note:** Processing happens asynchronously. Poll `GET /api/statements/{id}` to check status.

---

## List Statements

Get all statements uploaded by the authenticated user.

**Endpoint:** `GET /api/statements`

**Authentication:** Required (Access Token)

**Success Response (200):**

```json
{
  "success": true,
  "data": {
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
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Missing or invalid token

**Example:**

```bash
curl -X GET http://localhost:5000/api/statements \
  -H "Authorization: Bearer <access_token>"
```

**Note:** Statements are ordered by upload date (newest first).

---

## Get Statement Details

Get details of a specific statement, including current processing status.

**Endpoint:** `GET /api/statements/{statementId}`

**Authentication:** Required (Access Token)

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "stmt_123456",
    "fileName": "bank_statement_nov_2024.pdf",
    "uploadDate": "2024-11-02T15:30:00Z",
    "status": "processed",
    "transactionCount": 45,
    "statementPeriodStart": "2024-11-01T00:00:00Z",
    "statementPeriodEnd": "2024-11-30T23:59:59Z",
    "isProcessed": true
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Missing or invalid token
- `403`: Statement belongs to another user
- `404`: Statement not found

**Example:**

```bash
curl -X GET http://localhost:5000/api/statements/stmt_123456 \
  -H "Authorization: Bearer <access_token>"
```

**Use Case:** Poll this endpoint to check if statement processing is complete.

---

## Delete Statement

Delete a statement and all its associated transactions.

**Endpoint:** `POST /api/statements/{statementId}/delete`

**Authentication:** Required (Access Token)

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "success": true,
    "message": "Statement deleted successfully"
  },
  "metadata": {
    "timestamp": "2024-11-02T15:30:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Missing or invalid token
- `403`: Statement belongs to another user
- `404`: Statement not found

**Example:**

```bash
curl -X POST http://localhost:5000/api/statements/stmt_123456/delete \
  -H "Authorization: Bearer <access_token>"
```

**Note:** This deletes the statement record, all associated transactions, and the physical file from disk.

---

## Statement Status

Statements have a `status` field that indicates processing state:

- `processing`: Statement is being analyzed (fake analyzer is running)
- `processed`: Statement has been successfully processed and transactions are available
- `failed`: Processing failed (check `error_message` field if available)

**Status Progression:**

```
upload → processing → processed (or failed)
```

---

## Statement Ownership

All statement operations verify ownership:
- Users can only access statements they uploaded
- `statement.user_id` must match the authenticated user's ID
- Attempts to access other users' statements return `403 Forbidden`

---

## File Selection Feature

Statements enable the file selection/profile feature:

1. User uploads multiple statement files
2. Each statement becomes a "profile" that can be selected
3. When a statement is selected, all analytics and transaction endpoints can filter by `statementId`
4. This allows users to view data specific to each uploaded file

**Example Flow:**

```bash
# 1. Upload statement
POST /api/statements/upload → returns stmt_123456

# 2. Get transactions for this statement only
GET /api/transactions?statementId=stmt_123456

# 3. Get analytics for this statement only
GET /api/analytics/categories?statementId=stmt_123456
```

