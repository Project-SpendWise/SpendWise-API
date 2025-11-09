# Validation Utilities

The `utils/validators.py` module provides input validation functions for user data.

## Functions

### `validate_email(email)`

Validate email format.

**Parameters:**
- `email` (str): Email address to validate

**Returns:**
- `tuple`: (is_valid: bool, error_message: str | None)

**Validation Rules:**
- Email is required (not None or empty)
- Must match standard email format pattern
- Must have valid structure (name@domain.tld)

**Example Usage:**

```python
from utils.validators import validate_email

is_valid, error_msg = validate_email("user@example.com")
if not is_valid:
    print(error_msg)  # None if valid

# Invalid examples
validate_email("")           # (False, "Email is required")
validate_email("invalid")    # (False, "Invalid email format")
validate_email("@example.com") # (False, "Invalid email format")
```

**Valid Email Formats:**
- `user@example.com`
- `user.name@example.co.uk`
- `user+tag@example.com`

**Invalid Email Formats:**
- Empty string
- Missing @ symbol
- Missing domain
- Invalid characters

---

### `validate_password(password)`

Validate password strength.

**Parameters:**
- `password` (str): Password to validate

**Returns:**
- `tuple`: (is_valid: bool, error_message: str | None)

**Validation Rules:**
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)

**Example Usage:**

```python
from utils.validators import validate_password

is_valid, error_msg = validate_password("SecurePass123")
if not is_valid:
    print(error_msg)  # None if valid

# Invalid examples
validate_password("short")        # (False, "Password must be at least 8 characters long")
validate_password("nouppercase1") # (False, "Password must contain at least one uppercase letter")
validate_password("NOLOWERCASE1") # (False, "Password must contain at least one lowercase letter")
validate_password("NoNumbers")   # (False, "Password must contain at least one number")
```

**Valid Password Examples:**
- `SecurePass123`
- `MyP@ssw0rd`
- `Test1234`

**Invalid Password Examples:**
- `short` (too short)
- `alllowercase123` (no uppercase)
- `ALLUPPERCASE123` (no lowercase)
- `NoNumbersHere` (no numbers)

---

### `validate_username(username)`

Validate username format.

**Parameters:**
- `username` (str): Username to validate

**Returns:**
- `tuple`: (is_valid: bool, error_message: str | None)

**Validation Rules:**
- 3-30 characters long
- Alphanumeric and underscores only
- Must start with a letter (a-z, A-Z)

**Example Usage:**

```python
from utils.validators import validate_username

is_valid, error_msg = validate_username("johndoe")
if not is_valid:
    print(error_msg)  # None if valid

# Invalid examples
validate_username("ab")           # (False, "Username must be at least 3 characters long")
validate_username("a" * 31)       # (False, "Username must be no more than 30 characters long")
validate_username("123username")  # (False, "Username must start with a letter...")
validate_username("user-name")    # (False, "Username must start with a letter...")
```

**Valid Username Examples:**
- `johndoe`
- `user_123`
- `TestUser`
- `a_b_c`

**Invalid Username Examples:**
- `ab` (too short)
- `123user` (starts with number)
- `user-name` (contains hyphen)
- `user.name` (contains period)
- `user name` (contains space)

---

### `sanitize_string(value, max_length=None)`

Sanitize string input by trimming whitespace and optionally limiting length.

**Parameters:**
- `value` (str, optional): String to sanitize
- `max_length` (int, optional): Maximum length (truncates if longer)

**Returns:**
- `str | None`: Sanitized string, or None if input is empty/None

**Example Usage:**

```python
from utils.validators import sanitize_string

# Basic sanitization
sanitize_string("  hello world  ")  # "hello world"
sanitize_string("")                 # None
sanitize_string(None)               # None

# With max length
sanitize_string("  very long string  ", max_length=10)  # "very long"
sanitize_string("short", max_length=10)                # "short"
```

**Behavior:**
- Trims leading and trailing whitespace
- Returns `None` if result is empty string
- Truncates to `max_length` if provided and string is longer
- Handles `None` input gracefully

## Usage in Routes

These validators are typically used in route handlers:

```python
from flask import request
from utils.validators import validate_email, validate_password
from utils.responses import error_response

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate email
    email = data.get('email')
    is_valid, error_msg = validate_email(email)
    if not is_valid:
        return error_response(error_msg, 'INVALID_EMAIL', 400)
    
    # Validate password
    password = data.get('password')
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return error_response(error_msg, 'INVALID_PASSWORD', 400)
    
    # Continue with registration...
```

## Validation Flow

1. **Extract** data from request
2. **Validate** using appropriate validator
3. **Check** validation result
4. **Return error** if validation fails
5. **Continue** if validation passes

## Best Practices

1. **Always validate** user input before processing
2. **Use specific error messages** to guide users
3. **Sanitize strings** before storing in database
4. **Validate early** in the request handling flow
5. **Combine validators** for complex validation

## Extending Validators

To add custom validation, create new functions following the same pattern:

```python
def validate_phone(phone):
    """
    Validate phone number format
    Returns: (is_valid, error_message)
    """
    if not phone:
        return False, 'Phone number is required'
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if all digits
    if not cleaned.isdigit():
        return False, 'Phone number must contain only digits'
    
    # Check length (example: 10 digits for US numbers)
    if len(cleaned) != 10:
        return False, 'Phone number must be 10 digits'
    
    return True, None
```

## Regular Expressions Used

The validators use the following regex patterns:

- **Email**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **Password uppercase**: `[A-Z]`
- **Password lowercase**: `[a-z]`
- **Password number**: `\d`
- **Username**: `^[a-zA-Z][a-zA-Z0-9_]*$`

