# SpendWise-API

The official API and data management layer for the SpendWise personal finance tracking application. This service handles user authentication, secure data storage for all income and expense records, and provides the necessary analytical endpoints for the mobile app's budgeting and reporting features.

## Technology Stack

- **Framework**: Flask 3.0.0
- **Database**: SQLite (with Flask-SQLAlchemy)
- **Authentication**: Flask-JWT-Extended
- **Password Hashing**: bcrypt
- **CORS**: Flask-CORS
- **Migrations**: Flask-Migrate

## Setup Instructions

### 1. Install Dependencies

```bash
# Activate virtual environment (if using venv)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory (use `.env.example` as a template):

```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///spendwise.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Initialize Database

```bash
# Run the application (this will create the database)
python app.py

# Or use Flask CLI
flask db init  # First time only
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT tokens
- `GET /api/auth/me` - Get current user (requires authentication)
- `PUT /api/auth/me` - Update user profile (requires authentication)
- `POST /api/auth/change-password` - Change password (requires authentication)
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout (requires authentication)

### Health Check

- `GET /api/health` - Health check endpoint

## Project Structure

```
SpendWise-API/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models/
│   ├── __init__.py
│   └── user.py           # User model
├── routes/
│   ├── __init__.py
│   └── auth.py           # Authentication routes
├── utils/
│   ├── __init__.py
│   ├── validators.py     # Input validation helpers
│   └── responses.py      # Standardized response helpers
├── requirements.txt      # Python dependencies
└── .env.example         # Environment variables template
```

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade
```

## API Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "metadata": {
    "timestamp": "2024-11-02T10:00:00Z",
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
    "statusCode": 400
  }
}
```

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- CORS configuration
- Input validation and sanitization
- SQL injection protection (via SQLAlchemy ORM)

## License

See LICENSE file for details.
