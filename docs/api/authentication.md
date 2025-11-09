# Authentication

The SpendWise API uses JWT (JSON Web Tokens) for authentication. This guide explains how to authenticate and use protected endpoints.

## Overview

The authentication system uses two types of tokens:

- **Access Token**: Short-lived token (15 minutes) for API requests
- **Refresh Token**: Long-lived token (30 days) for obtaining new access tokens

## Authentication Flow

### 1. Register a New User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-here",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": "2024-01-01T00:00:00Z",
      "is_active": true
    },
    "message": "User registered successfully"
  },
  "message": "Registration successful",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

### 2. Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": "uuid-here",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": "2024-01-01T00:00:00Z",
      "is_active": true
    }
  },
  "message": "Login successful",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

### 3. Using Access Tokens

Include the access token in the Authorization header for protected endpoints:

```http
GET /api/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 4. Refreshing Tokens

When the access token expires, use the refresh token to get a new access token:

```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "Token refreshed successfully"
}
```

## Password Requirements

Passwords must meet the following requirements:

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

## Email Validation

Emails must be in a valid format (e.g., `user@example.com`).

## Username Validation

Usernames must meet the following requirements:

- 3-30 characters
- Alphanumeric and underscores only
- Must start with a letter

## Protected Endpoints

The following endpoints require authentication:

- `GET /api/auth/me` - Get current user
- `PUT /api/auth/me` - Update user profile
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/logout` - Logout

## Token Expiration

### Access Token

- **Lifetime**: 15 minutes
- **Error**: Returns `401` with error code `TOKEN_EXPIRED`

### Refresh Token

- **Lifetime**: 30 days
- **Error**: Returns `401` with error code `INVALID_TOKEN`

## Error Responses

### Invalid Credentials

```json
{
  "success": false,
  "error": {
    "message": "Invalid email or password",
    "code": "INVALID_CREDENTIALS",
    "statusCode": 401
  }
}
```

### Expired Token

```json
{
  "success": false,
  "error": {
    "message": "Token has expired",
    "code": "TOKEN_EXPIRED",
    "statusCode": 401
  }
}
```

### Missing Token

```json
{
  "success": false,
  "error": {
    "message": "Authorization token is missing",
    "code": "MISSING_TOKEN",
    "statusCode": 401
  }
}
```

### Invalid Token

```json
{
  "success": false,
  "error": {
    "message": "Invalid token",
    "code": "INVALID_TOKEN",
    "statusCode": 401
  }
}
```

## Security Best Practices

1. **Store tokens securely**: Never store tokens in localStorage for web apps. Use httpOnly cookies when possible.

2. **Use HTTPS**: Always use HTTPS in production to protect tokens in transit.

3. **Refresh tokens regularly**: Implement automatic token refresh before expiration.

4. **Handle token expiration**: Implement proper error handling for expired tokens.

5. **Logout properly**: Call the logout endpoint when users log out (future: token blacklisting).

## Example Implementation

### JavaScript/TypeScript

```typescript
class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  async login(email: string, password: string) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    if (data.success) {
      this.accessToken = data.data.access_token;
      this.refreshToken = data.data.refresh_token;
      // Store tokens securely
      localStorage.setItem('refresh_token', this.refreshToken);
    }
    return data;
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.refreshToken}`
      }
    });

    const data = await response.json();
    if (data.success) {
      this.accessToken = data.data.access_token;
      this.refreshToken = data.data.refresh_token;
    }
    return data;
  }

  async authenticatedFetch(url: string, options: RequestInit = {}) {
    if (!this.accessToken) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.accessToken}`
      }
    });

    // Handle token expiration
    if (response.status === 401) {
      await this.refreshAccessToken();
      // Retry request
      return fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${this.accessToken}`
        }
      });
    }

    return response;
  }
}
```

### Python

```python
import requests
from typing import Optional

class AuthClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def login(self, email: str, password: str) -> dict:
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        if data.get("success"):
            self.access_token = data["data"]["access_token"]
            self.refresh_token = data["data"]["refresh_token"]
        return data

    def refresh(self) -> dict:
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        response = requests.post(
            f"{self.base_url}/api/auth/refresh",
            headers={"Authorization": f"Bearer {self.refresh_token}"}
        )
        data = response.json()
        if data.get("success"):
            self.access_token = data["data"]["access_token"]
            self.refresh_token = data["data"]["refresh_token"]
        return data

    def get_headers(self) -> dict:
        if not self.access_token:
            raise ValueError("Not authenticated")
        return {"Authorization": f"Bearer {self.access_token}"}
```

