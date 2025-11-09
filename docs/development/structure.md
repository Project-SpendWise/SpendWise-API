# Project Structure

This document describes the structure of the SpendWise API project.

## Directory Layout

```
SpendWise-API/
├── app.py                 # Application factory and main entry point
├── config.py              # Configuration classes
├── requirements.txt       # Python dependencies
├── mkdocs.yml            # MkDocs configuration
├── docs/                 # Documentation source files
│   ├── index.md
│   ├── getting-started/
│   ├── api/
│   ├── models/
│   ├── development/
│   └── utilities/
├── models/               # Database models
│   ├── __init__.py
│   ├── user.py
│   └── file.py
├── routes/               # API route blueprints
│   ├── __init__.py
│   ├── auth.py
│   └── files.py
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── responses.py
│   ├── validators.py
│   └── file_utils.py
├── instance/             # Instance-specific files
│   └── spendwise.db     # SQLite database (development)
├── uploads/              # User uploaded files
│   └── YYYY-MM-DD/       # Date-based folders
│       └── user_id/      # User-specific folders
└── venv/                 # Virtual environment (not in git)
```

## Core Files

### `app.py`

Main application file using the Flask application factory pattern.

**Key Components:**
- Application factory function `create_app()`
- Extension initialization (SQLAlchemy, JWT, CORS, Migrate)
- Blueprint registration
- Error handlers
- Health check endpoint

**Example Usage:**

```python
from app import create_app

app = create_app('production')
```

### `config.py`

Configuration management with environment-specific settings.

**Configuration Classes:**
- `Config`: Base configuration
- `DevelopmentConfig`: Development settings
- `ProductionConfig`: Production settings
- `TestingConfig`: Testing settings

### `requirements.txt`

Python package dependencies. Install with:

```bash
pip install -r requirements.txt
```

## Models (`models/`)

Database models using SQLAlchemy ORM.

### `models/user.py`

User model with authentication and profile management.

**See:** [User Model Documentation](../models/user.md)

### `models/file.py`

File model for storing user uploaded files with strong user relationship.

**See:** [File Model Documentation](../models/file.md)

## Routes (`routes/`)

API route blueprints organized by feature.

### `routes/auth.py`

Authentication endpoints:
- Registration
- Login
- User profile management
- Password changes
- Token refresh
- Logout

**Blueprint:** `auth_bp`  
**URL Prefix:** `/api/auth`

**Database Access Pattern:**
Routes use the `get_db()` helper function to access the database instance from the current app context. This ensures proper Flask-SQLAlchemy 3.x compatibility with the application factory pattern.

**See:** [Database Patterns](database-patterns.md) for detailed information on database access patterns.

### `routes/files.py`

File management endpoints:
- File upload
- List user's files
- Get file details
- Download files
- Delete files

**Blueprint:** `files_bp`  
**URL Prefix:** `/api/files`

**Features:**
- User ownership verification on all operations
- Date-based and user-based file organization
- Duplicate file detection via hash
- Pagination and filtering support

**See:** [File Endpoints Documentation](../api/endpoints/files.md)

## Utilities (`utils/`)

Shared utility functions.

### `utils/responses.py`

Standardized API response helpers:
- `success_response()`: Create success responses
- `error_response()`: Create error responses

### `utils/validators.py`

Input validation functions:
- `validate_email()`: Email format validation
- `validate_password()`: Password strength validation
- `validate_username()`: Username format validation
- `sanitize_string()`: String sanitization

### `utils/file_utils.py`

File handling utilities:
- `validate_file_type()`: File extension validation
- `validate_file_size()`: File size validation
- `generate_file_hash()`: SHA-256 hash generation
- `generate_stored_filename()`: Unique filename generation
- `get_file_storage_path()`: Date-based + user-based path generation
- `save_file()`: Save file to disk
- `delete_file_from_disk()`: Remove file from filesystem
- `get_file_mime_type()`: MIME type detection

## Database

### Development

SQLite database stored in `instance/spendwise.db`

### Migrations

Database migrations managed with Flask-Migrate:

```bash
flask db init          # Initialize migrations
flask db migrate       # Create migration
flask db upgrade      # Apply migration
```

Migration files are stored in `migrations/` (created after initialization).

## Documentation (`docs/`)

MkDocs documentation source files.

**Build Documentation:**

```bash
mkdocs build
```

**Serve Documentation Locally:**

```bash
mkdocs serve
```

## Environment Variables

Create a `.env` file in the project root for local configuration:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///spendwise.db
CORS_ORIGINS=*
```

## Application Factory Pattern

The application uses the factory pattern for flexibility:

```python
def create_app(config_name=None):
    app = Flask(__name__)
    # Configuration
    # Extensions
    # Blueprints
    # Error handlers
    return app
```

**Benefits:**
- Multiple app instances
- Testing support
- Environment-specific configuration
- Delayed initialization

## Extension Initialization

Extensions are initialized in the application factory:

```python
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
cors = CORS()

def create_app():
    app = Flask(__name__)
    db.init_app(app)
    jwt.init_app(app)
    # ...
```

## Blueprint Registration

Routes are organized in blueprints and registered in the factory:

```python
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
```

## Error Handling

Global error handlers are registered in the application factory:

- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error
- JWT-specific errors (expired, invalid, missing tokens)

## Testing Structure

For testing, create a `tests/` directory:

```
tests/
├── __init__.py
├── conftest.py        # Pytest configuration
├── test_auth.py      # Auth endpoint tests
└── test_models.py    # Model tests
```

## Database Access

The API uses Flask-SQLAlchemy 3.x with SQLAlchemy 2.0. Route handlers access the database using a helper function that retrieves the db instance from the current app context.

**See:** [Database Patterns](database-patterns.md) for complete documentation on database access patterns and query syntax.

## Future Structure

As the project grows, consider adding:

```
SpendWise-API/
├── migrations/        # Database migrations
├── tests/            # Test files
├── scripts/          # Utility scripts
├── .env.example      # Example environment file
└── .gitignore        # Git ignore rules
```

