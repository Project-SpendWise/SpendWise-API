# Authentication Endpoints

Complete reference for all authentication-related endpoints.

## Register User

Register a new user account.

**Endpoint:** `POST /api/auth/register`

**Authentication:** Not required

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "username": "johndoe",        // Optional
  "first_name": "John",          // Optional
  "last_name": "Doe"             // Optional
}
```

**Validation Rules:**

- `email`: Required, valid email format, unique
- `password`: Required, min 8 chars, must contain uppercase, lowercase, and number
- `username`: Optional, 3-30 chars, alphanumeric and underscores, must start with letter, unique
- `first_name`: Optional, max 100 chars
- `last_name`: Optional, max 100 chars

**Success Response (201):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
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

**Error Responses:**

- `400`: Invalid email, password, or username format
- `409`: Email or username already exists

**Example:**

```bash
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

---

## Login

Authenticate and receive access/refresh tokens.

**Endpoint:** `POST /api/auth/login`

**Authentication:** Not required

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
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

**Error Responses:**

- `400`: Missing email or password
- `401`: Invalid credentials
- `403`: Account is deactivated

**Example:**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

---

## Get Current User

Get the authenticated user's profile information.

**Endpoint:** `GET /api/auth/me`

**Authentication:** Required (Access Token)

**Headers:**

```
Authorization: Bearer <access_token>
```

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": "2024-01-01T00:00:00Z",
      "is_active": true
    }
  },
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Missing or invalid token
- `404`: User not found

**Example:**

```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Update User Profile

Update the authenticated user's profile information.

**Endpoint:** `PUT /api/auth/me`

**Authentication:** Required (Access Token)

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "username": "newusername",     // Optional
  "first_name": "Jane",          // Optional
  "last_name": "Smith"           // Optional
}
```

**Note:** All fields are optional. Only include fields you want to update.

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "username": "newusername",
      "first_name": "Jane",
      "last_name": "Smith",
      "created_at": "2024-01-01T00:00:00Z",
      "is_active": true
    }
  },
  "message": "Profile updated successfully",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `400`: Invalid username format
- `401`: Missing or invalid token
- `404`: User not found
- `409`: Username already taken

**Example:**

```bash
curl -X PUT http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith"
  }'
```

---

## Change Password

Change the authenticated user's password.

**Endpoint:** `POST /api/auth/change-password`

**Authentication:** Required (Access Token)

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "current_password": "OldPass123",
  "new_password": "NewSecurePass456"
}
```

**Validation:**

- `new_password` must meet password requirements
- `new_password` must be different from `current_password`

**Success Response (200):**

```json
{
  "success": true,
  "message": "Password changed successfully",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `400`: Missing passwords or invalid new password format
- `401`: Incorrect current password or missing/invalid token
- `404`: User not found

**Example:**

```bash
curl -X POST http://localhost:5000/api/auth/change-password \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPass123",
    "new_password": "NewSecurePass456"
  }'
```

---

## Refresh Token

Get a new access token using a refresh token.

**Endpoint:** `POST /api/auth/refresh`

**Authentication:** Required (Refresh Token)

**Headers:**

```
Authorization: Bearer <refresh_token>
```

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "Token refreshed successfully",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

**Error Responses:**

- `401`: Invalid or expired refresh token
- `404`: User not found or inactive

**Example:**

```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

---

## Logout

Logout the authenticated user.

**Endpoint:** `POST /api/auth/logout`

**Authentication:** Required (Access Token)

**Headers:**

```
Authorization: Bearer <access_token>
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Logged out successfully",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

**Note:** Currently, this endpoint only returns success. Token blacklisting can be implemented for production use.

**Error Responses:**

- `401`: Missing or invalid token

**Example:**

```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

