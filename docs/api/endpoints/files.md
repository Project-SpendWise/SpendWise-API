# File Endpoints

Complete reference for all file management endpoints.

## Upload File

Upload a new file to the system.

**Endpoint:** `POST /api/files/upload`

**Authentication:** Required (Access Token)

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file` (required): The file to upload
- `description` (optional): Description of the file

**Allowed File Types:**
- PDF (`.pdf`)
- Excel 2007+ (`.xlsx`)
- Excel 97-2003 (`.xls`)
- CSV (`.csv`)
- Word 2007+ (`.docx`)

**File Size Limit:** 10MB

**Success Response (201):**

```json
{
  "success": true,
  "data": {
    "file": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-uuid-here",
      "original_filename": "document.pdf",
      "stored_filename": "abc123_document.pdf",
      "file_path": "/path/to/uploads/2025-11-09/user-id/",
      "file_type": "pdf",
      "mime_type": "application/pdf",
      "file_size": 1024000,
      "file_hash": "sha256-hash-here",
      "processing_status": "pending",
      "description": "Monthly expenses",
      "created_at": "2025-11-09T14:00:00Z",
      "updated_at": "2025-11-09T14:00:00Z"
    }
  },
  "message": "File uploaded successfully",
  "metadata": {
    "timestamp": "2025-11-09T14:00:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `400`: No file provided, invalid file type, file too large
- `401`: Missing or invalid token
- `409`: File with same content already exists (duplicate hash)
- `413`: File size exceeds maximum allowed size

**Example:**

```bash
curl -X POST http://localhost:5000/api/files/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/document.pdf" \
  -F "description=Monthly expenses report"
```

**File Storage:**
Files are stored in: `uploads/YYYY-MM-DD/user_id/stored_filename.ext`

---

## List Files

Get a paginated list of the authenticated user's files.

**Endpoint:** `GET /api/files`

**Authentication:** Required (Access Token)

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `file_type` | string | Filter by file type (pdf, xlsx, xls, csv, docx) | None (all types) |
| `page` | integer | Page number | 1 |
| `per_page` | integer | Items per page (max 100) | 20 |

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "files": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "user-uuid-here",
        "original_filename": "document.pdf",
        "stored_filename": "abc123_document.pdf",
        "file_path": "/path/to/uploads/2025-11-09/user-id/",
        "file_type": "pdf",
        "mime_type": "application/pdf",
        "file_size": 1024000,
        "file_hash": "sha256-hash-here",
        "processing_status": "pending",
        "description": "Monthly expenses",
        "created_at": "2025-11-09T14:00:00Z",
        "updated_at": "2025-11-09T14:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  },
  "metadata": {
    "timestamp": "2025-11-09T14:00:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Missing or invalid token

**Examples:**

```bash
# Get all files
curl -X GET http://localhost:5000/api/files \
  -H "Authorization: Bearer <access_token>"

# Get PDF files only
curl -X GET "http://localhost:5000/api/files?file_type=pdf" \
  -H "Authorization: Bearer <access_token>"

# Get second page
curl -X GET "http://localhost:5000/api/files?page=2&per_page=10" \
  -H "Authorization: Bearer <access_token>"
```

---

## Get File Details

Get detailed information about a specific file.

**Endpoint:** `GET /api/files/<file_id>`

**Authentication:** Required (Access Token)

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "file": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-uuid-here",
      "original_filename": "document.pdf",
      "stored_filename": "abc123_document.pdf",
      "file_path": "/path/to/uploads/2025-11-09/user-id/",
      "file_type": "pdf",
      "mime_type": "application/pdf",
      "file_size": 1024000,
      "file_hash": "sha256-hash-here",
      "processing_status": "pending",
      "description": "Monthly expenses",
      "created_at": "2025-11-09T14:00:00Z",
      "updated_at": "2025-11-09T14:00:00Z"
    }
  },
  "metadata": {
    "timestamp": "2025-11-09T14:00:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Missing or invalid token
- `403`: File belongs to another user
- `404`: File not found

**Example:**

```bash
curl -X GET http://localhost:5000/api/files/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <access_token>"
```

---

## Download File

Download a file.

**Endpoint:** `GET /api/files/<file_id>/download`

**Authentication:** Required (Access Token)

**Success Response (200):**

Returns the file as a download with appropriate headers:
- `Content-Type`: File's MIME type
- `Content-Disposition`: `attachment; filename="original_filename.ext"`

**Error Responses:**

- `401`: Missing or invalid token
- `403`: File belongs to another user
- `404`: File not found or file missing on disk

**Example:**

```bash
curl -X GET http://localhost:5000/api/files/550e8400-e29b-41d4-a716-446655440000/download \
  -H "Authorization: Bearer <access_token>" \
  -o downloaded_file.pdf
```

---

## Delete File

Delete a file from the system.

**Endpoint:** `DELETE /api/files/<file_id>`

**Authentication:** Required (Access Token)

**Success Response (200):**

```json
{
  "success": true,
  "message": "File deleted successfully",
  "metadata": {
    "timestamp": "2025-11-09T14:00:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Missing or invalid token
- `403`: File belongs to another user
- `404`: File not found

**Example:**

```bash
curl -X DELETE http://localhost:5000/api/files/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <access_token>"
```

**Note:** This deletes both the database record and the physical file from disk.

---

## File Ownership

All file operations verify ownership:
- Users can only access files they uploaded
- `file.user_id` must match the authenticated user's ID
- Attempts to access other users' files return `403 Forbidden`

## File Storage Structure

Files are organized by date and user:
```
uploads/
  └── 2025-11-09/
      └── user-id-1/
          ├── abc123_document.pdf
          └── def456_spreadsheet.xlsx
      └── user-id-2/
          └── ghi789_report.pdf
```

## Processing Status

Files have a `processing_status` field that can be:
- `pending`: File uploaded, not yet processed
- `processing`: File is being processed
- `completed`: File processing completed successfully
- `failed`: File processing failed

This field is reserved for future file processing/extraction features.

