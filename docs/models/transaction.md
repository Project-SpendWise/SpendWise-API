# Transaction Model

The Transaction model represents individual financial transactions extracted from bank statements.

## Schema

### Table: `transactions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | Primary Key | UUID v4 identifier |
| `user_id` | String(36) | Foreign Key, Not Null, Indexed | Reference to users table |
| `statement_id` | String(36) | Foreign Key, Not Null, Indexed | Reference to statements table |
| `date` | DateTime | Not Null, Indexed | Transaction date and time |
| `description` | Text | Not Null | Transaction description or memo |
| `amount` | Numeric(10,2) | Not Null | Transaction amount |
| `type` | String(20) | Not Null | Transaction type: 'income' or 'expense' |
| `category` | String(100) | Nullable, Indexed | Transaction category |
| `merchant` | String(255) | Nullable | Merchant or vendor name |
| `account` | String(100) | Nullable | Account name |
| `reference_number` | String(100) | Nullable | Bank reference or transaction number |
| `created_at` | DateTime | Not Null, Default: NOW() | Record creation timestamp |
| `updated_at` | DateTime | Not Null, Default: NOW() | Last update timestamp |

## Transaction Types

- `income`: Money received (salary, bonuses, investment returns, etc.)
- `expense`: Money spent (purchases, bills, services, etc.)

## Categories (Turkish)

- **Gıda** (Food): Groceries, restaurants, food delivery
- **Ulaşım** (Transport): Public transport, fuel, ride-sharing
- **Alışveriş** (Shopping): Retail purchases, online shopping
- **Faturalar** (Bills): Utilities, phone, internet, rent
- **Eğlence** (Entertainment): Movies, subscriptions, cafes
- **Sağlık** (Health): Medical expenses, pharmacy
- **Eğitim** (Education): Courses, books, educational materials
- **Diğer** (Other): Miscellaneous expenses

## Model Definition

```python
from app import db
from datetime import datetime
import uuid

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    statement_id = db.Column(db.String(36), db.ForeignKey('statements.id', ondelete='CASCADE'), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(100), nullable=True, index=True)
    merchant = db.Column(db.String(255), nullable=True)
    account = db.Column(db.String(100), nullable=True)
    reference_number = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

## Methods

### `__init__(user_id, statement_id, date, description, amount, type, category=None, merchant=None, account=None, reference_number=None)`

Constructor for creating a new Transaction instance.

**Parameters:**
- `user_id` (str): ID of the user who owns this transaction
- `statement_id` (str): ID of the statement this transaction belongs to
- `date` (datetime): Transaction date and time
- `description` (str): Transaction description
- `amount` (float): Transaction amount
- `type` (str): Transaction type ('income' or 'expense')
- `category` (str, optional): Transaction category
- `merchant` (str, optional): Merchant or vendor name
- `account` (str, optional): Account name
- `reference_number` (str, optional): Bank reference number

**Example:**

```python
transaction = Transaction(
    user_id="user_123",
    statement_id="stmt_123456",
    date=datetime(2024, 11, 1, 10, 30),
    description="Migros Market Alışverişi",
    amount=245.50,
    type='expense',
    category='Gıda',
    merchant='Migros',
    account='Ana Hesap',
    reference_number='REF123456'
)
```

### `to_dict()`

Convert the transaction object to a dictionary matching API response format.

**Returns:**
- `dict`: Transaction data as dictionary

**Example:**

```python
transaction_dict = transaction.to_dict()
# {
#     'id': 'txn_123456',
#     'date': '2024-11-01T10:30:00Z',
#     'description': 'Migros Market Alışverişi',
#     'amount': 245.50,
#     'type': 'expense',
#     'category': 'Gıda',
#     'merchant': 'Migros',
#     'account': 'Ana Hesap',
#     'referenceNumber': 'REF123456',
#     'statementId': 'stmt_123456'
# }
```

## Usage Examples

### Creating a Transaction

```python
from models.transaction import Transaction
from app import db
from datetime import datetime

transaction = Transaction(
    user_id="user_123",
    statement_id="stmt_123456",
    date=datetime(2024, 11, 1, 10, 30),
    description="Migros Market Alışverişi",
    amount=245.50,
    type='expense',
    category='Gıda',
    merchant='Migros'
)

db.session.add(transaction)
db.session.commit()
```

### Querying Transactions

```python
from models.transaction import Transaction
from datetime import datetime

# Find transaction by ID
transaction = Transaction.query.get("txn_123456")

# Find all transactions for a user
user_transactions = Transaction.query.filter_by(user_id="user_123").all()

# Find transactions for a specific statement
statement_transactions = Transaction.query.filter_by(statement_id="stmt_123456").all()

# Find transactions by category
food_transactions = Transaction.query.filter_by(category='Gıda').all()

# Find transactions by date range
from datetime import timedelta
recent = Transaction.query.filter(
    Transaction.date >= datetime.utcnow() - timedelta(days=30)
).all()

# Find income transactions
income = Transaction.query.filter_by(type='income').all()

# Find expense transactions
expenses = Transaction.query.filter_by(type='expense').all()
```

### Aggregating Transactions

```python
from sqlalchemy import func

# Sum expenses for a user
total_expenses = db.session.query(
    func.sum(Transaction.amount)
).filter_by(
    user_id="user_123",
    type='expense'
).scalar()

# Count transactions by category
category_counts = db.session.query(
    Transaction.category,
    func.count(Transaction.id)
).filter_by(
    user_id="user_123"
).group_by(Transaction.category).all()

# Average transaction amount
avg_amount = db.session.query(
    func.avg(Transaction.amount)
).filter_by(
    user_id="user_123",
    type='expense'
).scalar()
```

## Relationships

### Statement (Many-to-One)

A transaction belongs to one statement:

```python
# Get the statement for a transaction
statement = transaction.statement

# Access statement properties
statement_id = transaction.statement_id
file_name = transaction.statement.file_name
```

### User (Many-to-One)

A transaction belongs to one user:

```python
# Get the user for a transaction
user = transaction.user
```

## Indexes

The following columns and combinations are indexed for performance:
- `user_id`: For fast user-based queries
- `statement_id`: For fast statement-based queries (file selection)
- `date`: For date-based filtering and sorting
- `category`: For category-based filtering
- `(user_id, date)`: Composite index for user + date queries
- `(user_id, category)`: Composite index for user + category queries

## Foreign Key Constraints

- `user_id` references `users.id` with `ON DELETE CASCADE`
  - Deleting a user automatically deletes all their transactions
- `statement_id` references `statements.id` with `ON DELETE CASCADE`
  - Deleting a statement automatically deletes all associated transactions

## Timestamps

- `created_at`: Automatically set when the transaction is created
- `updated_at`: Automatically updated whenever the transaction record is modified
- `date`: Transaction date (set explicitly, represents when the transaction occurred)

All timestamps use UTC timezone.

## File Selection Feature

Transactions support the file selection feature through `statement_id`:

- All transaction queries can filter by `statement_id`
- This enables viewing transactions for a specific uploaded file
- Analytics endpoints use this to provide file-specific insights

## Amount Handling

- Amounts are stored as `Numeric(10, 2)` for precise decimal handling
- Amounts are always positive values
- The `type` field indicates whether it's income or expense
- For expenses, the amount represents money spent
- For income, the amount represents money received

