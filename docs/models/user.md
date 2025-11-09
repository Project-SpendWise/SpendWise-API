# User Model

The User model represents a user account in the SpendWise system.

## Schema

### Table: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | Primary Key | UUID v4 identifier |
| `email` | String(255) | Unique, Not Null, Indexed | User's email address |
| `username` | String(50) | Unique, Nullable, Indexed | User's username |
| `password_hash` | String(255) | Not Null | Bcrypt hashed password |
| `first_name` | String(100) | Nullable | User's first name |
| `last_name` | String(100) | Nullable | User's last name |
| `created_at` | DateTime | Not Null | Account creation timestamp |
| `updated_at` | DateTime | Not Null | Last update timestamp |
| `is_active` | Boolean | Not Null, Default: True | Account active status |
| `last_login` | DateTime | Nullable | Last login timestamp |

## Model Definition

```python
from app import db
from datetime import datetime
import bcrypt
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
```

## Methods

### `__init__(email, password, username=None, first_name=None, last_name=None)`

Constructor for creating a new User instance.

**Parameters:**
- `email` (str): User's email address
- `password` (str): Plain text password (will be hashed)
- `username` (str, optional): User's username
- `first_name` (str, optional): User's first name
- `last_name` (str, optional): User's last name

**Example:**

```python
user = User(
    email="user@example.com",
    password="SecurePass123",
    username="johndoe",
    first_name="John",
    last_name="Doe"
)
```

### `set_password(password)`

Hash and set the user's password using bcrypt.

**Parameters:**
- `password` (str): Plain text password

**Example:**

```python
user.set_password("NewSecurePass456")
```

### `check_password(password)`

Verify if the provided password matches the stored hash.

**Parameters:**
- `password` (str): Plain text password to verify

**Returns:**
- `bool`: True if password matches, False otherwise

**Example:**

```python
if user.check_password("SecurePass123"):
    print("Password is correct")
```

### `update_last_login()`

Update the `last_login` timestamp to the current UTC time.

**Example:**

```python
user.update_last_login()
```

### `to_dict(include_sensitive=False)`

Convert the user object to a dictionary representation.

**Parameters:**
- `include_sensitive` (bool, optional): Include sensitive fields like `last_login`

**Returns:**
- `dict`: User data as dictionary

**Example:**

```python
# Basic user data
user_dict = user.to_dict()
# {
#     'id': '550e8400-e29b-41d4-a716-446655440000',
#     'email': 'user@example.com',
#     'username': 'johndoe',
#     'first_name': 'John',
#     'last_name': 'Doe',
#     'created_at': '2024-01-01T00:00:00Z',
#     'is_active': True
# }

# Include sensitive data
user_dict = user.to_dict(include_sensitive=True)
# Includes 'last_login' field
```

## Usage Examples

### Creating a User

```python
from models.user import User
from app import db

user = User(
    email="newuser@example.com",
    password="SecurePass123",
    username="newuser",
    first_name="New",
    last_name="User"
)

db.session.add(user)
db.session.commit()
```

### Querying Users

```python
from models.user import User

# Find user by email
user = User.query.filter_by(email="user@example.com").first()

# Find user by username
user = User.query.filter_by(username="johndoe").first()

# Find user by ID
user = User.query.get("550e8400-e29b-41d4-a716-446655440000")

# Get all active users
active_users = User.query.filter_by(is_active=True).all()
```

### Updating a User

```python
user = User.query.filter_by(email="user@example.com").first()
user.first_name = "Updated"
user.username = "updateduser"
user.updated_at = datetime.utcnow()
db.session.commit()
```

### Password Operations

```python
# Change password
user.set_password("NewSecurePass456")
db.session.commit()

# Verify password
if user.check_password("NewSecurePass456"):
    print("Password verified")
```

### Deactivating a User

```python
user = User.query.filter_by(email="user@example.com").first()
user.is_active = False
db.session.commit()
```

## Password Security

Passwords are hashed using bcrypt with automatic salt generation. The hash is stored in the `password_hash` column and never exposed in API responses.

**Security Features:**
- Bcrypt hashing with salt
- Passwords are never stored in plain text
- Password hashes are never returned in API responses

## Indexes

The following columns are indexed for performance:
- `email`: For fast email lookups
- `username`: For fast username lookups

## Relationships

Currently, the User model has no relationships defined. Future relationships may include:
- Transactions (one-to-many)
- Categories (one-to-many)
- Budgets (one-to-many)

## Validation

User data validation is handled at the API level using validators in `utils/validators.py`:

- Email format validation
- Password strength validation
- Username format validation
- String sanitization

## Timestamps

- `created_at`: Automatically set when the user is created
- `updated_at`: Automatically updated whenever the user record is modified
- `last_login`: Manually updated via `update_last_login()` method

All timestamps use UTC timezone.

