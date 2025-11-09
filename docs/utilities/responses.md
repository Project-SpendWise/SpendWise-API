# Response Utilities

The `utils/responses.py` module provides standardized response helpers for consistent API responses.

## Functions

### `success_response(data=None, message=None, status_code=200)`

Create a standardized success response.

**Parameters:**
- `data` (dict, optional): Response data payload
- `message` (str, optional): Success message
- `status_code` (int, optional): HTTP status code (default: 200)

**Returns:**
- `tuple`: (JSON response, status code)

**Response Format:**

```json
{
  "success": true,
  "data": {
    // Your data here
  },
  "message": "Optional success message",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

**Example Usage:**

```python
from utils.responses import success_response

# Simple success response
return success_response()

# With data
return success_response(
    data={'user_id': '123', 'email': 'user@example.com'}
)

# With message and custom status code
return success_response(
    data={'user': user.to_dict()},
    message='User created successfully',
    status_code=201
)
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com"
    }
  },
  "message": "User created successfully",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

---

### `error_response(message, error_code='ERROR', status_code=400, details=None)`

Create a standardized error response.

**Parameters:**
- `message` (str): Error message description
- `error_code` (str, optional): Error code identifier (default: 'ERROR')
- `status_code` (int, optional): HTTP status code (default: 400)
- `details` (dict, optional): Additional error details

**Returns:**
- `tuple`: (JSON response, status code)

**Response Format:**

```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE",
    "statusCode": 400,
    "details": {
      // Optional additional details
    }
  }
}
```

**Example Usage:**

```python
from utils.responses import error_response

# Simple error response
return error_response('Invalid request', 'INVALID_REQUEST', 400)

# With details
return error_response(
    message='Validation failed',
    error_code='VALIDATION_ERROR',
    status_code=400,
    details={
        'fields': ['email', 'password'],
        'errors': ['Email is required', 'Password is too short']
    }
)

# Authentication error
return error_response(
    message='Invalid credentials',
    error_code='INVALID_CREDENTIALS',
    status_code=401
)
```

**Example Responses:**

```json
{
  "success": false,
  "error": {
    "message": "Invalid email format",
    "code": "INVALID_EMAIL",
    "statusCode": 400
  }
}
```

```json
{
  "success": false,
  "error": {
    "message": "Validation failed",
    "code": "VALIDATION_ERROR",
    "statusCode": 400,
    "details": {
      "fields": ["email"],
      "errors": ["Email is required"]
    }
  }
}
```

## Response Metadata

All success responses include metadata:

- `timestamp`: UTC timestamp in ISO 8601 format
- `version`: API version (currently "1.0.0")

## Common Error Codes

| Code | Description | Status Code |
|------|-------------|-------------|
| `INVALID_REQUEST` | Request body is missing or invalid | 400 |
| `INVALID_EMAIL` | Email format is invalid | 400 |
| `INVALID_PASSWORD` | Password doesn't meet requirements | 400 |
| `INVALID_USERNAME` | Username format is invalid | 400 |
| `INVALID_CREDENTIALS` | Email or password is incorrect | 401 |
| `EMAIL_EXISTS` | Email is already registered | 409 |
| `USERNAME_EXISTS` | Username is already taken | 409 |
| `UNAUTHORIZED` | Authentication required | 401 |
| `TOKEN_EXPIRED` | JWT token has expired | 401 |
| `INVALID_TOKEN` | JWT token is invalid | 401 |
| `MISSING_TOKEN` | Authorization token is missing | 401 |
| `USER_NOT_FOUND` | User doesn't exist | 404 |
| `ACCOUNT_DEACTIVATED` | User account is deactivated | 403 |

## Best Practices

1. **Always use these helpers** instead of manually creating JSON responses
2. **Use appropriate error codes** for different error types
3. **Include helpful error messages** that guide users
4. **Add details** for validation errors to help clients fix issues
5. **Use consistent status codes** following HTTP standards

## Integration with Flask

These functions return Flask `jsonify` responses, so they can be used directly in route handlers:

```python
from flask import Blueprint
from utils.responses import success_response, error_response

bp = Blueprint('example', __name__)

@bp.route('/example')
def example():
    try:
        # Your logic here
        return success_response(data={'result': 'success'})
    except Exception as e:
        return error_response(str(e), 'SERVER_ERROR', 500)
```

## Extending Responses

To add custom metadata or modify response format, you can extend these functions:

```python
def custom_success_response(data=None, message=None, status_code=200, custom_field=None):
    response_data = {
        'success': True,
        'data': data,
        'metadata': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'custom_field': custom_field
        }
    }
    if message:
        response_data['message'] = message
    return jsonify(response_data), status_code
```

