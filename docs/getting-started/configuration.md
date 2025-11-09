# Configuration

The SpendWise API uses a flexible configuration system that supports multiple environments: development, production, and testing.

## Configuration Classes

The application uses three configuration classes defined in `config.py`:

### DevelopmentConfig

Default configuration for local development:

```python
DEBUG = True
SQLALCHEMY_ECHO = True  # Logs all SQL queries
```

### ProductionConfig

Production configuration with strict security requirements:

```python
DEBUG = False
# Requires SECRET_KEY and JWT_SECRET_KEY environment variables
```

### TestingConfig

Configuration for running tests:

```python
TESTING = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database
```

## Environment Variables

### Required (Production)

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for session management | `your-secret-key-here` |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | `your-jwt-secret-key-here` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment name (development/production/testing) | `development` |
| `DATABASE_URL` | Database connection string | `sqlite:///spendwise.db` |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | `*` |
| `UPLOAD_FOLDER` | Directory for file uploads | `uploads` |
| `RATELIMIT_ENABLED` | Enable rate limiting | `False` |

## JWT Configuration

JWT tokens are configured with the following defaults:

```python
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)   # Access token lifetime
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)     # Refresh token lifetime
JWT_TOKEN_LOCATION = ['headers']                   # Token location
JWT_HEADER_NAME = 'Authorization'                  # Header name
JWT_HEADER_TYPE = 'Bearer'                         # Token type
```

## CORS Configuration

CORS is configured to allow requests from specified origins:

```python
CORS_ORIGINS = ['http://localhost:3000', 'https://app.spendwise.com']
```

For development, you can use `*` to allow all origins (not recommended for production).

## Database Configuration

### SQLite (Development)

```env
DATABASE_URL=sqlite:///spendwise.db
```

### PostgreSQL (Production)

```env
DATABASE_URL=postgresql://user:password@localhost/spendwise
```

### MySQL (Production)

```env
DATABASE_URL=mysql://user:password@localhost/spendwise
```

## File Upload Configuration

```python
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
UPLOAD_FOLDER = 'uploads'               # Upload directory
```

## Setting Environment Variables

### Windows (PowerShell)

```powershell
$env:SECRET_KEY="your-secret-key"
$env:FLASK_ENV="production"
```

### macOS/Linux

```bash
export SECRET_KEY="your-secret-key"
export FLASK_ENV="production"
```

### Using .env File

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///spendwise.db
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

The application automatically loads variables from `.env` using `python-dotenv`.

## Security Best Practices

1. **Never commit secrets**: Add `.env` to `.gitignore`
2. **Use strong keys**: Generate random, long strings for secret keys
3. **Limit CORS origins**: Specify exact origins in production
4. **Use HTTPS**: Always use HTTPS in production
5. **Rotate keys**: Regularly rotate secret keys

## Example Production Configuration

```env
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://user:pass@db.example.com/spendwise
CORS_ORIGINS=https://app.spendwise.com,https://www.spendwise.com
UPLOAD_FOLDER=/var/www/spendwise/uploads
RATELIMIT_ENABLED=true
```

