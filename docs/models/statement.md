# Statement Model

The Statement model represents a bank statement file that has been uploaded and processed to extract transactions.

## Schema

### Table: `statements`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | Primary Key | UUID v4 identifier |
| `user_id` | String(36) | Foreign Key, Not Null, Indexed | Reference to users table |
| `file_name` | String(255) | Not Null | Original filename of uploaded statement |
| `file_path` | String(500) | Not Null | Full filesystem path to stored file |
| `upload_date` | DateTime | Not Null, Default: NOW() | When the statement was uploaded |
| `statement_period_start` | DateTime | Nullable | Start date of statement period |
| `statement_period_end` | DateTime | Nullable | End date of statement period |
| `transaction_count` | Integer | Not Null, Default: 0 | Number of transactions extracted |
| `status` | String(20) | Not Null, Default: 'processing' | Processing status |
| `error_message` | Text | Nullable | Error message if processing failed |
| `created_at` | DateTime | Not Null, Default: NOW() | Record creation timestamp |
| `updated_at` | DateTime | Not Null, Default: NOW() | Last update timestamp |

## Status Values

- `processing`: Statement is being analyzed (fake analyzer is running)
- `processed`: Statement has been successfully processed and transactions are available
- `failed`: Processing failed (check `error_message` field)

## Model Definition

```python
from app import db
from datetime import datetime
import uuid

class Statement(db.Model):
    __tablename__ = 'statements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    statement_period_start = db.Column(db.DateTime, nullable=True)
    statement_period_end = db.Column(db.DateTime, nullable=True)
    transaction_count = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(20), default='processing', nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

## Methods

### `__init__(user_id, file_name, file_path, status='processing')`

Constructor for creating a new Statement instance.

**Parameters:**
- `user_id` (str): ID of the user who uploaded the statement
- `file_name` (str): Original filename of the statement
- `file_path` (str): Full filesystem path where the file is stored
- `status` (str, optional): Initial status (default: 'processing')

**Example:**

```python
statement = Statement(
    user_id="user_123",
    file_name="bank_statement_nov_2024.pdf",
    file_path="/uploads/2024-11-02/user_123/abc123_statement.pdf",
    status='processing'
)
```

### `to_dict()`

Convert the statement object to a dictionary matching API response format.

**Returns:**
- `dict`: Statement data as dictionary

**Example:**

```python
statement_dict = statement.to_dict()
# {
#     'id': 'stmt_123456',
#     'fileName': 'bank_statement_nov_2024.pdf',
#     'uploadDate': '2024-11-02T15:30:00Z',
#     'status': 'processed',
#     'transactionCount': 45,
#     'statementPeriodStart': '2024-11-01T00:00:00Z',
#     'statementPeriodEnd': '2024-11-30T23:59:59Z',
#     'isProcessed': True
# }
```

### `update_status(status, error_message=None)`

Update the statement's processing status.

**Parameters:**
- `status` (str): New status ('processing', 'processed', or 'failed')
- `error_message` (str, optional): Error message if status is 'failed'

**Raises:**
- `ValueError`: If status is not one of the valid values

**Example:**

```python
statement.update_status('processed')
# or
statement.update_status('failed', error_message='Processing timeout')
```

## Usage Examples

### Creating a Statement

```python
from models.statement import Statement
from app import db

statement = Statement(
    user_id="user_123",
    file_name="bank_statement_nov_2024.pdf",
    file_path="/uploads/2024-11-02/user_123/abc123_statement.pdf"
)

db.session.add(statement)
db.session.commit()
```

### Querying Statements

```python
from models.statement import Statement

# Find statement by ID
statement = Statement.query.get("stmt_123456")

# Find all statements for a user
user_statements = Statement.query.filter_by(user_id="user_123").all()

# Find processed statements
processed = Statement.query.filter_by(status='processed').all()

# Find statements by upload date
from datetime import datetime, timedelta
recent = Statement.query.filter(
    Statement.upload_date >= datetime.utcnow() - timedelta(days=7)
).all()
```

### Updating Statement Status

```python
statement = Statement.query.get("stmt_123456")
statement.update_status('processed')
statement.transaction_count = 45
statement.statement_period_start = datetime(2024, 11, 1)
statement.statement_period_end = datetime(2024, 11, 30)
db.session.commit()
```

## Relationships

### Transactions (One-to-Many)

A statement can have many transactions:

```python
# Get all transactions for a statement
transactions = statement.transactions.all()

# Count transactions
count = statement.transactions.count()
```

Transactions are automatically deleted when a statement is deleted (CASCADE).

## Indexes

The following columns are indexed for performance:
- `user_id`: For fast user-based queries
- `status`: For filtering by processing status
- `upload_date`: For date-based sorting and filtering

## Foreign Key Constraints

- `user_id` references `users.id` with `ON DELETE CASCADE`
  - Deleting a user automatically deletes all their statements
  - Deleting a statement automatically deletes all associated transactions

## Timestamps

- `created_at`: Automatically set when the statement is created
- `updated_at`: Automatically updated whenever the statement record is modified
- `upload_date`: Set when the statement is uploaded (can be different from `created_at`)

All timestamps use UTC timezone.

## File Selection Feature

Statements enable the file selection/profile feature:

- Each statement represents a "profile" that users can select
- When a statement is selected, all transaction and analytics endpoints can filter by `statementId`
- This allows users to view data specific to each uploaded file

## Processing Flow

1. **Upload**: Statement is uploaded, record created with status 'processing'
2. **Processing**: Background job runs fake analyzer
3. **Completion**: Status updated to 'processed', transactions stored
4. **Failure**: If processing fails, status updated to 'failed' with error message

