# API Overview

The SpendWise API is a RESTful API that follows standard HTTP methods and status codes. All endpoints return JSON responses.

## Base URL

```
http://localhost:5000/api
```

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Optional success message",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE",
    "statusCode": 400,
    "details": {} // Optional additional details
  }
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required or invalid |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error - Server error |

## Authentication

Most endpoints require authentication using JWT (JSON Web Tokens). Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

See the [Authentication Guide](authentication.md) for detailed information.

## Rate Limiting

Rate limiting is configurable but not enabled by default. When enabled, rate limit information is included in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1609459200
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register a new user | No |
| POST | `/api/auth/login` | Login and get tokens | No |
| GET | `/api/auth/me` | Get current user | Yes |
| PUT | `/api/auth/me` | Update user profile | Yes |
| POST | `/api/auth/change-password` | Change password | Yes |
| POST | `/api/auth/refresh` | Refresh access token | Yes (Refresh) |
| POST | `/api/auth/logout` | Logout user | Yes |

### File Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/files/upload` | Upload a file | Yes |
| GET | `/api/files` | List user's files | Yes |
| GET | `/api/files/<file_id>` | Get file details | Yes |
| GET | `/api/files/<file_id>/download` | Download file | Yes |
| DELETE | `/api/files/<file_id>` | Delete file | Yes |

### Health Check

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/health` | Health check endpoint | No |

## Request Headers

### Required Headers

For JSON endpoints:
```
Content-Type: application/json
```

For file upload:
```
Content-Type: multipart/form-data
```

### Optional Headers

```
Authorization: Bearer <token>
Accept: application/json
```

## Pagination

Pagination is implemented for file listing endpoints:

```
GET /api/files?page=1&per_page=20
```

**Pagination Response:**
```json
{
  "data": {
    "files": [...],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 50,
      "pages": 3
    }
  }
}
```

## Filtering and Sorting

Filtering is implemented for file endpoints:

```
GET /api/files?file_type=pdf
```

Files are automatically sorted by creation date (newest first).

Future filtering and sorting can be added to other endpoints using query parameters.

## Error Codes

Common error codes you may encounter:

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Request body is missing or invalid |
| `INVALID_EMAIL` | Email format is invalid |
| `INVALID_PASSWORD` | Password doesn't meet requirements |
| `INVALID_USERNAME` | Username format is invalid |
| `INVALID_CREDENTIALS` | Email or password is incorrect |
| `EMAIL_EXISTS` | Email is already registered |
| `USERNAME_EXISTS` | Username is already taken |
| `UNAUTHORIZED` | Authentication required |
| `TOKEN_EXPIRED` | JWT token has expired |
| `INVALID_TOKEN` | JWT token is invalid |
| `MISSING_TOKEN` | Authorization token is missing |
| `USER_NOT_FOUND` | User doesn't exist | 
| `ACCOUNT_DEACTIVATED` | User account is deactivated |
| `NO_FILE` | No file provided in upload request |
| `NO_FILE_SELECTED` | Empty filename in upload |
| `INVALID_FILE_TYPE` | File type not allowed |
| `FILE_TOO_LARGE` | File size exceeds maximum allowed |
| `DUPLICATE_FILE` | File with same content already exists |
| `FILE_NOT_FOUND` | File doesn't exist |
| `FORBIDDEN` | Access denied (file belongs to another user) |
| `SAVE_ERROR` | Failed to save file to disk |
| `DOWNLOAD_ERROR` | Error during file download |
| `DELETE_ERROR` | Error during file deletion |

## Versioning

The API is currently at version 1.0.0. Version information is included in response metadata. Future versions may be accessed via URL path or header:

```
/api/v1/auth/login
```

or

```
Accept: application/vnd.spendwise.v1+json
```

## CORS

CORS is enabled for configured origins. Preflight requests are automatically handled for all endpoints under `/api/*`.

## Examples

### cURL

```bash
# Register a user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Python

```python
import requests

url = "http://localhost:5000/api/auth/login"
data = {
    "email": "user@example.com",
    "password": "SecurePass123"
}

response = requests.post(url, json=data)
tokens = response.json()
```

### JavaScript (Fetch)

```javascript
fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

