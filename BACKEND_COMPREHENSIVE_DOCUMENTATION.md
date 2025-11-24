# SpendWise Backend - Comprehensive Documentation

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [System Architecture](#system-architecture)
4. [Design Patterns](#design-patterns)
5. [Database Schema](#database-schema)
6. [Business Logic](#business-logic)
7. [Code Walkthrough](#code-walkthrough)
8. [API Flow](#api-flow)
9. [Key Components](#key-components)
10. [Common Questions & Answers](#common-questions--answers)

---

## Overview

**SpendWise Backend** is a RESTful API built with Flask that provides:
- User authentication and authorization
- File upload and management
- Bank statement processing (with mock analyzer)
- Transaction management
- Budget tracking
- Financial analytics

**Technology Stack:**
- **Framework**: Flask 3.0.0
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **ORM**: SQLAlchemy (Flask-SQLAlchemy 3.x)
- **Authentication**: JWT (Flask-JWT-Extended)
- **Password Security**: bcrypt
- **CORS**: Flask-CORS
- **Migrations**: Flask-Migrate

---

## Project Structure

```
SpendWise-API/
├── app.py                      # Application factory (main entry point)
├── config.py                    # Configuration classes
├── requirements.txt             # Python dependencies
│
├── models/                      # Database models (SQLAlchemy ORM)
│   ├── __init__.py             # Model exports
│   ├── user.py                 # User model
│   ├── file.py                 # File model
│   ├── statement.py            # Statement model (with profile fields)
│   ├── transaction.py          # Transaction model
│   └── budget.py               # Budget model
│
├── routes/                      # API route blueprints
│   ├── __init__.py
│   ├── auth.py                 # Authentication endpoints
│   ├── files.py                # File management endpoints
│   ├── statements.py           # Statement processing endpoints
│   ├── transactions.py         # Transaction endpoints
│   ├── budgets.py              # Budget management endpoints
│   └── analytics.py            # Analytics endpoints
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   ├── responses.py            # Standardized API responses
│   ├── validators.py           # Input validation
│   └── file_utils.py           # File handling utilities
│
├── analyzers/                   # Statement analyzers
│   ├── __init__.py
│   └── fake_analyzer.py        # Mock analyzer (generates realistic data)
│
├── instance/                    # Instance-specific files
│   └── spendwise.db            # SQLite database file
│
├── uploads/                     # User uploaded files
│   └── YYYY-MM-DD/             # Date-based folders
│       └── user_id/            # User-specific folders
│
├── docs/                        # MkDocs documentation
├── scripts/                     # Utility scripts
│
└── Migration & Setup Scripts:
    ├── setup_database.py       # Initial database setup
    ├── migrate_add_profile_fields.py  # Profile system migration
    └── reset_database.py       # Database reset utility
```

---

## System Architecture

### High-Level Architecture

```
┌─────────────┐
│   Client    │ (Frontend/Mobile App)
│  (Browser)  │
└──────┬──────┘
       │ HTTP/REST API
       │ (JWT Authentication)
       ▼
┌─────────────────────────────────────┐
│         Flask Application           │
│  ┌───────────────────────────────┐  │
│  │   Application Factory (app.py) │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │      Blueprints (Routes)      │  │
│  │  - auth, files, statements    │  │
│  │  - transactions, budgets      │  │
│  │  - analytics                  │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │    Business Logic Layer       │  │
│  │  - Validation                 │  │
│  │  - Data processing            │  │
│  │  - File handling              │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │    Data Access Layer          │  │
│  │  - SQLAlchemy ORM             │  │
│  │  - Models (User, File, etc.)  │  │
│  └───────────┬───────────────────┘  │
└──────────────┼───────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         SQLite Database             │
│  - users                            │
│  - files                            │
│  - statements                       │
│  - transactions                     │
│  - budgets                          │
└─────────────────────────────────────┘
```

### Request Flow

```
1. Client Request
   ↓
2. Flask Application (app.py)
   ↓
3. CORS Middleware (if cross-origin)
   ↓
4. JWT Authentication Middleware (if protected route)
   ↓
5. Blueprint Route Handler
   ↓
6. Input Validation
   ↓
7. Business Logic Processing
   ↓
8. Database Operations (SQLAlchemy)
   ↓
9. Response Formatting
   ↓
10. Client Response
```

---

## Design Patterns

### 1. Application Factory Pattern

**Location**: `app.py`

**Purpose**: Allows creating multiple app instances with different configurations (development, production, testing).

**How it works:**
```python
def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Initialize extensions
    # Register blueprints
    return app
```

**Benefits:**
- Easy testing (can create test app instances)
- Multiple configurations (dev, prod, test)
- Extensions initialized per app instance

### 2. Blueprint Pattern

**Location**: `routes/*.py`

**Purpose**: Organizes routes into logical modules.

**Example:**
```python
# routes/auth.py
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # Registration logic
    pass

# app.py
app.register_blueprint(auth_bp, url_prefix='/api/auth')
```

**Benefits:**
- Modular code organization
- Reusable route groups
- Easy to maintain and test

### 3. Repository Pattern (via SQLAlchemy)

**Location**: `models/*.py`

**Purpose**: Abstracts database operations through ORM models.

**How it works:**
- Models define database structure
- SQLAlchemy handles SQL generation
- Business logic uses model methods

### 4. Dependency Injection

**Location**: Throughout the application

**Purpose**: Database instance is injected via `get_db()` helper.

**Example:**
```python
def get_db():
    return current_app.extensions['sqlalchemy']

@route('/endpoint')
def my_endpoint():
    db_instance = get_db()  # Get DB from app context
    # Use db_instance
```

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────┐         ┌──────────┐
│   User   │────────<│   File   │
│          │ 1    *  │          │
└────┬─────┘         └──────────┘
     │
     │ 1
     │
     │    *
┌────▼─────────────┐
│   Statement     │
│  (Profile)      │
└────┬────────────┘
     │
     │ 1
     │
     │    *
┌────▼─────────────┐
│  Transaction    │
└──────────────────┘

┌──────────┐         ┌──────────┐
│   User   │────────<│  Budget  │
│          │ 1    *  │          │
└──────────┘         └──────────┘
```

### Tables

#### 1. `users`
- `id` (String, PK) - UUID
- `email` (String, Unique) - User email
- `username` (String, Unique) - Username
- `password_hash` (String) - Bcrypt hashed password
- `first_name`, `last_name` (String)
- `created_at`, `updated_at` (DateTime)
- `is_active` (Boolean)

#### 2. `files`
- `id` (String, PK) - UUID
- `user_id` (String, FK → users.id)
- `original_filename`, `stored_filename` (String)
- `file_path` (String)
- `file_type`, `mime_type` (String)
- `file_size` (Integer)
- `file_hash` (String) - MD5 hash for duplicate detection
- `processing_status` (String)
- `created_at`, `updated_at` (DateTime)

#### 3. `statements`
- `id` (String, PK) - UUID
- `user_id` (String, FK → users.id)
- `file_name`, `file_path` (String)
- `upload_date` (DateTime)
- `statement_period_start`, `statement_period_end` (DateTime)
- `transaction_count` (Integer)
- `status` (String) - processing, processed, failed
- **Profile Fields:**
  - `profile_name` (String)
  - `profile_description` (Text)
  - `account_type` (String)
  - `bank_name` (String)
  - `color` (String) - Hex color code
  - `icon` (String)
  - `is_default` (Boolean)
- `created_at`, `updated_at` (DateTime)

#### 4. `transactions`
- `id` (String, PK) - UUID
- `user_id` (String, FK → users.id)
- `statement_id` (String, FK → statements.id)
- `date` (DateTime)
- `description` (Text)
- `amount` (Numeric)
- `type` (String) - income, expense
- `category` (String) - Gıda, Ulaşım, etc.
- `merchant` (String)
- `account` (String)
- `reference_number` (String)
- `created_at`, `updated_at` (DateTime)

#### 5. `budgets`
- `id` (String, PK) - UUID
- `user_id` (String, FK → users.id)
- `category` (String)
- `amount` (Numeric)
- `period_start`, `period_end` (DateTime)
- `created_at`, `updated_at` (DateTime)

### Relationships

- **User → Files**: One-to-Many (CASCADE delete)
- **User → Statements**: One-to-Many (CASCADE delete)
- **User → Transactions**: One-to-Many (CASCADE delete)
- **User → Budgets**: One-to-Many (CASCADE delete)
- **Statement → Transactions**: One-to-Many (CASCADE delete)

---

## Business Logic

### 1. Authentication Flow

```
User Registration:
1. Validate input (email, password, username)
2. Check if email/username already exists
3. Hash password with bcrypt
4. Create user record
5. Return user data (no password)

User Login:
1. Validate input (email/username, password)
2. Find user by email/username
3. Verify password hash
4. Generate JWT access token (15 min expiry)
5. Generate JWT refresh token (30 days expiry)
6. Return tokens + user data

Token Refresh:
1. Verify refresh token
2. Generate new access token
3. Return new access token

Protected Routes:
1. Extract JWT token from Authorization header
2. Verify token signature and expiry
3. Extract user_id from token payload
4. Allow request to proceed
```

### 2. File Upload Flow

```
File Upload:
1. Verify user is authenticated
2. Validate file type (PDF, XLSX, CSV, etc.)
3. Validate file size (max 10MB)
4. Generate unique filename
5. Create date-based folder structure: uploads/YYYY-MM-DD/user_id/
6. Save file to disk
7. Calculate MD5 hash
8. Check for duplicates (same hash + user)
9. Create File record in database
10. Return file metadata

File Download:
1. Verify user is authenticated
2. Verify file ownership
3. Check file exists on disk
4. Stream file to client
5. Set appropriate headers (Content-Type, Content-Disposition)
```

### 3. Statement Processing Flow

```
Statement Upload:
1. User uploads file via /api/statements/upload
2. Accept optional profile metadata (name, description, account type, etc.)
3. Save file to disk
4. Create Statement record with status='processing'
5. If first profile, set is_default=True
6. Queue async processing job
7. Return statement record immediately

Async Processing (Background Thread):
1. Get statement record from database
2. Load FakeStatementAnalyzer
3. Generate realistic transactions:
   - Calculate income (17,000-25,000 TRY/month)
   - Generate expenses (75-90% of income)
   - Allocate to categories (Gıda, Ulaşım, etc.)
   - Create fixed expenses (rent, utilities)
4. Save transactions to database
5. Update statement:
   - Set status='processed'
   - Set transaction_count
   - Set statement_period_start/end
6. Commit all changes

User Views Transactions:
1. User selects a profile (statement)
2. Frontend passes statementId to API
3. API filters transactions by statementId
4. Returns only transactions for that profile
```

### 4. Transaction Generation Logic

**Location**: `analyzers/fake_analyzer.py`

**Algorithm:**
```
1. Generate Income:
   - Primary salary: 17,000-25,000 TRY (always on 1st-5th of month)
   - Optional freelance: 2,000-5,000 TRY (20% chance)
   - Optional bonus: 1,000-3,000 TRY (10% chance)

2. Calculate Expense Budget:
   - Total income = sum of all income transactions
   - Expense ratio = 75-90% (randomized per statement)
   - Target expenses = total_income * expense_ratio

3. Allocate Category Budgets:
   - Gıda (Food): 25-30% of expenses
   - Ulaşım (Transport): 15-20%
   - Faturalar (Bills): 15-20%
   - Alışveriş (Shopping): 10-15%
   - Eğlence (Entertainment): 5-10%
   - Sağlık (Health): 5-8%
   - Eğitim (Education): 3-5%
   - Diğer (Other): 5-10%

4. Generate Fixed Expenses:
   - Rent: 2,000-5,000 TRY (always on 1st-5th)
   - Utilities: Electricity, Water, Gas, Internet, Phone

5. Generate Variable Expenses:
   - For each category, generate transactions until budget is met
   - Scale amounts based on income level
   - Distribute across time period (30 days)
```

### 5. Profile System Logic

```
Profile Creation:
- Each uploaded file becomes a profile
- Profile metadata: name, description, account type, bank, color, icon
- First profile automatically becomes default

Profile Selection:
- User selects a profile from dropdown
- Frontend stores selected profile ID
- All API requests include statementId={selectedProfileId}
- Transactions, budgets, analytics filter by profile

Default Profile:
- Only one profile can be default at a time
- Setting a profile as default unsets all others
- Default profile appears first in lists
```

### 6. Analytics Calculation Logic

**Category Breakdown:**
- Group transactions by category
- Sum amounts per category
- Calculate percentages
- Filter by statementId if provided

**Spending Trends:**
- Group transactions by date (daily/weekly/monthly)
- Calculate totals per period
- Compare periods
- Filter by statementId if provided

**Financial Insights:**
- Total income = sum of income transactions
- Total expenses = sum of expense transactions
- Net = income - expenses
- Savings rate = (income - expenses) / income
- Filter by statementId if provided

---

## Code Walkthrough

### 1. Application Initialization (`app.py`)

```python
# Step 1: Initialize extensions (outside create_app)
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
cors = CORS()

# Step 2: Application factory
def create_app(config_name=None):
    app = Flask(__name__)
    
    # Step 3: Load configuration
    app.config.from_object(config[config_name])
    
    # Step 4: Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    # ... etc
    
    # Step 5: Import models (register with SQLAlchemy)
    from models import User, File, Statement, Transaction, Budget
    
    # Step 6: Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # ... etc
    
    # Step 7: Create tables
    with app.app_context():
        db.create_all()
    
    # Step 8: Setup middleware (logging, error handlers)
    # ... etc
    
    return app
```

### 2. Database Access Pattern

**Problem**: Flask-SQLAlchemy 3.x with application factory requires special handling.

**Solution**: `get_db()` helper function.

```python
# In each route file
from flask import current_app

def get_db():
    """Get database instance from current app context"""
    return current_app.extensions['sqlalchemy']

# Usage in routes
@route('/endpoint')
def my_endpoint():
    db_instance = get_db()
    user = db_instance.session.get(User, user_id)
    # ... use db_instance
```

### 3. Authentication Route Example

```python
# routes/auth.py
@auth_bp.route('/register', methods=['POST'])
def register():
    # 1. Get request data
    data = request.get_json()
    
    # 2. Validate input
    if not validate_email(data['email']):
        return error_response('Invalid email', 'INVALID_EMAIL', 400)
    
    # 3. Check if user exists
    db_instance = get_db()
    existing_user = db_instance.session.query(User).filter_by(
        email=data['email']
    ).first()
    if existing_user:
        return error_response('Email already exists', 'EMAIL_EXISTS', 400)
    
    # 4. Hash password
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    # 5. Create user
    user = User(
        email=data['email'],
        username=data['username'],
        password_hash=password_hash,
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )
    db_instance.session.add(user)
    db_instance.session.commit()
    
    # 6. Return success response
    return success_response(
        data={'user': user.to_dict()},
        message='User registered successfully',
        status_code=201
    )
```

### 4. Statement Upload & Processing

```python
# routes/statements.py
@statements_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_statement():
    # 1. Get file and profile metadata
    file = request.files['file']
    profile_name = request.form.get('profileName', '').strip()
    
    # 2. Validate file
    is_valid, error_msg = validate_file_type(file.filename)
    if not is_valid:
        return error_response(error_msg, 'INVALID_FILE_TYPE', 400)
    
    # 3. Save file
    stored_filename = generate_stored_filename(file.filename, user_id)
    save_file(file_content, storage_path, stored_filename)
    
    # 4. Check if first profile (set as default)
    existing_statements = db_instance.session.query(Statement).filter_by(
        user_id=user_id
    ).count()
    is_default = existing_statements == 0
    
    # 5. Create statement record
    statement = Statement(
        user_id=user_id,
        file_name=file.filename,
        file_path=full_file_path,
        status='processing',
        profile_name=profile_name or auto_generated_name,
        is_default=is_default
    )
    db_instance.session.add(statement)
    db_instance.session.commit()
    
    # 6. Queue async processing
    executor.submit(process_statement_async, app_obj, statement.id, file_path, user_id)
    
    # 7. Return immediately (processing happens in background)
    return success_response(data=statement.to_dict())

# Async processing function
def process_statement_async(app_instance, statement_id, file_path, user_id):
    with app_instance.app_context():
        db_instance = get_db()
        statement = db_instance.session.get(Statement, statement_id)
        
        # Run fake analyzer
        analyzer = FakeStatementAnalyzer()
        result = analyzer.analyze(file_path, user_id, statement_id)
        
        # Save transactions
        for txn in result.transactions:
            db_instance.session.add(txn)
        
        # Update statement
        statement.status = 'processed'
        statement.transaction_count = len(result.transactions)
        db_instance.session.commit()
```

### 5. Transaction Filtering by Profile

```python
# routes/transactions.py
@transactions_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    db_instance = get_db()
    user_id = get_jwt_identity()
    
    # Build base query (always filter by user)
    query = select(Transaction).filter_by(user_id=user_id)
    
    # CRITICAL: Filter by statementId if provided (profile selection)
    statement_id = request.args.get('statementId', '').strip()
    if statement_id:
        # Verify statement belongs to user
        statement = db_instance.session.get(Statement, statement_id)
        if not statement or statement.user_id != user_id:
            return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
        
        query = query.filter_by(statement_id=statement_id)
    
    # Apply other filters (date, category, etc.)
    # ...
    
    transactions = db_instance.session.scalars(query).all()
    return success_response(data={'transactions': [t.to_dict() for t in transactions]})
```

---

## API Flow

### Complete User Journey

```
1. User Registration
   POST /api/auth/register
   → Creates user account
   → Returns user data

2. User Login
   POST /api/auth/login
   → Validates credentials
   → Returns JWT tokens (access + refresh)

3. Upload Statement (with Profile)
   POST /api/statements/upload
   Headers: Authorization: Bearer <access_token>
   Body: multipart/form-data
     - file: <PDF/XLSX>
     - profileName: "Personal Account"
     - accountType: "Checking"
     - color: "#3B82F6"
   → Saves file
   → Creates Statement record (status='processing')
   → Queues async processing
   → Returns statement data

4. Background Processing
   → Fake analyzer generates transactions
   → Saves transactions to database
   → Updates statement (status='processed')

5. List Profiles
   GET /api/statements/profiles
   → Returns all user's profiles
   → Sorted by isDefault DESC

6. Select Profile
   Frontend stores selected profile ID
   → All subsequent requests include statementId

7. Get Transactions (Filtered by Profile)
   GET /api/transactions?statementId={selectedProfileId}
   → Returns only transactions for selected profile

8. Get Analytics (Filtered by Profile)
   GET /api/analytics/category-breakdown?statementId={selectedProfileId}
   → Returns analytics for selected profile only

9. Update Profile
   PUT /api/statements/{id}/profile
   Body: { profileName, color, icon, ... }
   → Updates profile metadata

10. Set Default Profile
    POST /api/statements/{id}/set-default
    → Sets this profile as default
    → Unsets all other profiles
```

---

## Key Components

### 1. Models (`models/`)

**Purpose**: Define database structure and relationships.

**Key Features:**
- SQLAlchemy ORM models
- Relationships with CASCADE deletes
- `to_dict()` methods for API responses
- Indexes for performance

**Example Model:**
```python
class Statement(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    # ... fields
    
    # Relationship
    transactions = db.relationship('Transaction', backref='statement', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'profileName': self.profile_name,
            # ... etc
        }
```

### 2. Routes (`routes/`)

**Purpose**: Handle HTTP requests and responses.

**Structure:**
- Each file is a blueprint
- Routes are decorated with `@jwt_required()` for protection
- Use `get_db()` for database access
- Return standardized responses

### 3. Utilities (`utils/`)

**`responses.py`**: Standardized API responses
```python
def success_response(data, message=None, status_code=200):
    return {
        'data': data,
        'message': message,
        'statusCode': status_code
    }, status_code

def error_response(message, error_code, status_code):
    return {
        'error': {
            'message': message,
            'errorCode': error_code,
            'statusCode': status_code
        }
    }, status_code
```

**`file_utils.py`**: File handling
- File validation (type, size)
- Filename generation
- File storage (date-based folders)
- File deletion

**`validators.py`**: Input validation
- Email validation
- Password strength
- Username format

### 4. Analyzers (`analyzers/`)

**Purpose**: Process bank statements and extract transactions.

**Current Implementation**: `FakeStatementAnalyzer`
- Generates realistic mock data
- Income-based expense budgeting
- Category allocation
- Fixed and variable expenses

**Design**: Modular interface allows easy replacement with real AI/ML analyzer.

### 5. Configuration (`config.py`)

**Purpose**: Environment-specific settings.

**Configurations:**
- `DevelopmentConfig`: Debug mode, verbose logging
- `ProductionConfig`: Security checks, optimized logging
- `TestingConfig`: In-memory database

---

## Common Questions & Answers

### Q1: How does authentication work?

**A**: JWT-based authentication:
1. User logs in with email/username + password
2. Server validates credentials
3. Server generates JWT tokens (access + refresh)
4. Client stores tokens
5. Client sends access token in `Authorization: Bearer <token>` header
6. Server validates token on each request
7. Access token expires in 15 minutes
8. Client uses refresh token to get new access token

### Q2: How are files organized on disk?

**A**: Date-based + user-based structure:
```
uploads/
  └── 2024-01-15/          # Date folder
      └── user_123/         # User folder
          └── file_abc.pdf  # Actual file
```

**Benefits:**
- Easy to find files by date
- User isolation
- Prevents filename conflicts

### Q3: How does statement processing work?

**A**: Asynchronous background processing:
1. User uploads file → Statement created with `status='processing'`
2. File saved to disk
3. Background thread starts processing
4. Fake analyzer generates transactions
5. Transactions saved to database
6. Statement updated: `status='processed'`, `transaction_count` set

**Why async?**
- Large files might take time to process
- User gets immediate response
- Processing happens in background

### Q4: How does the profile system work?

**A**: Each uploaded file becomes a selectable profile:
1. Upload file with profile metadata (name, color, icon, etc.)
2. Statement record stores profile info
3. User selects a profile from dropdown
4. Frontend passes `statementId` to all API requests
5. Backend filters data by `statementId`
6. User sees only data for selected profile

**Benefits:**
- Separate accounts/profiles
- Easy switching between profiles
- Organized data

### Q5: How are transactions generated?

**A**: Realistic mock data generation:
1. Generate income (17,000-25,000 TRY/month)
2. Calculate expense budget (75-90% of income)
3. Allocate to categories (Gıda 25-30%, Ulaşım 15-20%, etc.)
4. Generate fixed expenses (rent, utilities)
5. Generate variable expenses per category
6. Distribute across 30-day period

**Consistency:**
- Same `statement_id` always generates same transactions (uses hash as seed)

### Q6: How does database access work?

**A**: Flask-SQLAlchemy 3.x with application factory:
- Use `get_db()` helper to get database instance
- Access via `db_instance.session`
- Always filter by `user_id` for security
- Use SQLAlchemy 2.0 query syntax (`select()`, `scalars()`)

### Q7: What happens when a user is deleted?

**A**: CASCADE deletes:
- User deleted → All their files deleted
- User deleted → All their statements deleted
- Statement deleted → All its transactions deleted
- User deleted → All their budgets deleted

**File cleanup:**
- Database records deleted automatically
- Physical files remain (can be cleaned up separately)

### Q8: How are errors handled?

**A**: Standardized error responses:
```json
{
  "error": {
    "message": "Error description",
    "errorCode": "ERROR_CODE",
    "statusCode": 400
  }
}
```

**Error types:**
- 400: Bad Request (validation errors)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (access denied)
- 404: Not Found (resource doesn't exist)
- 500: Internal Server Error (server issues)

### Q9: How is CORS configured?

**A**: Flask-CORS middleware:
- Allows cross-origin requests from configured origins
- Configured in `app.py` for `/api/*` routes
- Supports: GET, POST, PUT, DELETE, OPTIONS
- Exposes headers for file downloads

### Q10: How to add a new endpoint?

**A**: Steps:
1. Create route in appropriate blueprint file (or new file)
2. Add `@jwt_required()` if protected
3. Use `get_db()` for database access
4. Validate input
5. Process business logic
6. Return standardized response (`success_response()` or `error_response()`)
7. Register blueprint in `app.py` (if new)

---

## Summary

**SpendWise Backend** is a well-structured Flask application that:

1. **Uses modern patterns**: Application factory, blueprints, ORM
2. **Handles authentication**: JWT-based with refresh tokens
3. **Manages files**: Organized storage with validation
4. **Processes statements**: Async background processing with mock analyzer
5. **Supports profiles**: Each file is a selectable profile
6. **Provides analytics**: Filtered by profile/statement
7. **Ensures security**: User isolation, input validation, CASCADE deletes

**Key Design Decisions:**
- Application factory for flexibility
- Blueprints for modularity
- Async processing for better UX
- Profile system for data organization
- Realistic mock data for MVP testing

This architecture is scalable and can be extended with real AI/ML analyzers, additional features, and production-ready database (PostgreSQL).

