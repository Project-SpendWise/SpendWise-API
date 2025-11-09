# Database Patterns

This document describes the database access patterns used in the SpendWise API.

## Flask-SQLAlchemy 3.x Pattern

The API uses Flask-SQLAlchemy 3.x with SQLAlchemy 2.0. Due to the application factory pattern, database access requires getting the db instance from the current app context.

## Getting the Database Instance

In route handlers, use the `get_db()` helper function to access the database instance:

```python
from flask import current_app

def get_db():
    """Get db instance from current app"""
    return current_app.extensions['sqlalchemy']

@auth_bp.route('/example', methods=['GET'])
def example():
    db_instance = get_db()
    # Use db_instance.session for queries
```

## SQLAlchemy 2.0 Query Syntax

The API uses SQLAlchemy 2.0 style queries with `select()` and `scalar()`:

### Querying Records

```python
from sqlalchemy import select

# Get a single record
user = db_instance.session.scalar(select(User).filter_by(email=email))

# Get by primary key
user = db_instance.session.get(User, user_id)

# Check if record exists
existing_user = db_instance.session.scalar(
    select(User).filter_by(username=username)
)
```

### Creating Records

```python
# Create new record
user = User(
    email=email,
    password=password,
    username=username
)

db_instance.session.add(user)
db_instance.session.commit()
```

### Updating Records

```python
# Update record
user = db_instance.session.get(User, user_id)
user.first_name = "Updated"
user.updated_at = datetime.utcnow()
db_instance.session.commit()
```

### Deleting Records

```python
# Delete record
user = db_instance.session.get(User, user_id)
db_instance.session.delete(user)
db_instance.session.commit()
```

## Error Handling

Always use try-except blocks and rollback on errors:

```python
try:
    db_instance.session.add(user)
    db_instance.session.commit()
except IntegrityError as e:
    db_instance.session.rollback()
    return error_response('Duplicate entry', 'DUPLICATE_ERROR', 409)
except Exception as e:
    db_instance.session.rollback()
    return error_response('An error occurred', 'SERVER_ERROR', 500)
```

## Why This Pattern?

The application factory pattern creates the Flask app instance at runtime. When routes are imported at module level, the db instance from `app.py` isn't yet bound to an app context. Using `current_app.extensions['sqlalchemy']` ensures we get the db instance that's properly bound to the current request's app context.

## Migration from Older Patterns

If you're migrating from older Flask-SQLAlchemy patterns:

**Old (Flask-SQLAlchemy 2.x):**
```python
user = User.query.filter_by(email=email).first()
```

**New (Flask-SQLAlchemy 3.x with SQLAlchemy 2.0):**
```python
db_instance = get_db()
user = db_instance.session.scalar(select(User).filter_by(email=email))
```

## Best Practices

1. **Always use `get_db()`** in route handlers to get the db instance
2. **Use SQLAlchemy 2.0 syntax** with `select()` and `scalar()`
3. **Handle exceptions** and rollback on errors
4. **Commit explicitly** after making changes
5. **Use transactions** for multiple related operations

## Example: Complete Route Handler

```python
from flask import Blueprint, request, current_app
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app import db
from models.user import User
from utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__)

def get_db():
    """Get db instance from current app"""
    return current_app.extensions['sqlalchemy']

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        db_instance = get_db()
        data = request.get_json()
        
        # Validate input
        email = data.get('email')
        if not email:
            return error_response('Email required', 'INVALID_REQUEST', 400)
        
        # Check if user exists
        existing_user = db_instance.session.scalar(
            select(User).filter_by(email=email.lower().strip())
        )
        if existing_user:
            return error_response('Email exists', 'EMAIL_EXISTS', 409)
        
        # Create user
        user = User(email=email, password=data.get('password'))
        db_instance.session.add(user)
        db_instance.session.commit()
        
        return success_response(
            data={'user': user.to_dict()},
            message='User created',
            status_code=201
        )
        
    except IntegrityError as e:
        db_instance.session.rollback()
        return error_response('Duplicate entry', 'DUPLICATE_ERROR', 409)
    except Exception as e:
        db_instance.session.rollback()
        return error_response('Server error', 'SERVER_ERROR', 500)
```

