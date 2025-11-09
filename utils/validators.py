import re
from email.utils import parseaddr

def validate_email(email):
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, 'Email is required'
    
    email = email.strip().lower()
    
    # Basic email format validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, 'Invalid email format'
    
    # Check for valid email structure
    name, addr = parseaddr(email)
    if '@' not in addr or '.' not in addr.split('@')[1]:
        return False, 'Invalid email format'
    
    return True, None

def validate_password(password):
    """
    Validate password strength
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, 'Password is required'
    
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'
    
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'
    
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number'
    
    return True, None

def validate_username(username):
    """
    Validate username format
    Requirements:
    - 3-30 characters
    - Alphanumeric and underscores only
    - Must start with a letter
    
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, 'Username is required'
    
    username = username.strip()
    
    if len(username) < 3:
        return False, 'Username must be at least 3 characters long'
    
    if len(username) > 30:
        return False, 'Username must be no more than 30 characters long'
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, 'Username must start with a letter and contain only letters, numbers, and underscores'
    
    return True, None

def sanitize_string(value, max_length=None):
    """
    Sanitize string input by trimming whitespace
    """
    if not value:
        return None
    
    sanitized = value.strip()
    
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized if sanitized else None

