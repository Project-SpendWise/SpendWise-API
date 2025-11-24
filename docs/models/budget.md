# Budget Model

The Budget model represents user-defined spending limits for categories over specific time periods.

## Schema

### Table: `budgets`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | Primary Key | UUID v4 identifier |
| `user_id` | String(36) | Foreign Key, Not Null, Indexed | Reference to users table |
| `category_id` | String(100) | Not Null | Unique identifier for the category |
| `category_name` | String(100) | Not Null | Display name of the category |
| `amount` | Numeric(10,2) | Not Null | Budget amount |
| `period` | String(20) | Not Null | Budget period: 'monthly' or 'yearly' |
| `start_date` | DateTime | Not Null, Indexed | Start date of budget period |
| `end_date` | DateTime | Nullable | End date of budget period |
| `created_at` | DateTime | Not Null, Default: NOW() | Record creation timestamp |
| `updated_at` | DateTime | Not Null, Default: NOW() | Last update timestamp |

## Budget Periods

- `monthly`: Budget covers one calendar month
- `yearly`: Budget covers one calendar year

## Model Definition

```python
from app import db
from datetime import datetime
import uuid

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.String(100), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    period = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

## Methods

### `__init__(user_id, category_id, category_name, amount, period, start_date, end_date=None)`

Constructor for creating a new Budget instance.

**Parameters:**
- `user_id` (str): ID of the user who owns this budget
- `category_id` (str): Unique identifier for the category
- `category_name` (str): Display name of the category
- `amount` (float): Budget amount (must be > 0)
- `period` (str): Budget period ('monthly' or 'yearly')
- `start_date` (datetime): Start date of the budget period
- `end_date` (datetime, optional): End date of the budget period

**Example:**

```python
from datetime import datetime

budget = Budget(
    user_id="user_123",
    category_id="food",
    category_name="Gıda",
    amount=2500.00,
    period='monthly',
    start_date=datetime(2024, 11, 1),
    end_date=datetime(2024, 11, 30)
)
```

### `to_dict()`

Convert the budget object to a dictionary matching API response format.

**Returns:**
- `dict`: Budget data as dictionary

**Example:**

```python
budget_dict = budget.to_dict()
# {
#     'id': 'budget_food_monthly',
#     'categoryId': 'food',
#     'categoryName': 'Gıda',
#     'amount': 2500.00,
#     'period': 'monthly',
#     'startDate': '2024-11-01T00:00:00Z',
#     'endDate': '2024-11-30T23:59:59Z',
#     'createdAt': '2024-11-01T10:00:00Z',
#     'updatedAt': '2024-11-01T10:00:00Z'
# }
```

## Usage Examples

### Creating a Budget

```python
from models.budget import Budget
from app import db
from datetime import datetime

budget = Budget(
    user_id="user_123",
    category_id="food",
    category_name="Gıda",
    amount=2500.00,
    period='monthly',
    start_date=datetime(2024, 11, 1),
    end_date=datetime(2024, 11, 30)
)

db.session.add(budget)
db.session.commit()
```

### Querying Budgets

```python
from models.budget import Budget

# Find budget by ID
budget = Budget.query.get("budget_food_monthly")

# Find all budgets for a user
user_budgets = Budget.query.filter_by(user_id="user_123").all()

# Find monthly budgets
monthly_budgets = Budget.query.filter_by(period='monthly').all()

# Find budget for specific category
food_budget = Budget.query.filter_by(
    user_id="user_123",
    category_id="food",
    period='monthly'
).first()

# Find active budgets (within date range)
from datetime import datetime
now = datetime.utcnow()
active_budgets = Budget.query.filter(
    Budget.start_date <= now,
    Budget.end_date >= now
).all()
```

### Updating a Budget

```python
budget = Budget.query.get("budget_food_monthly")
budget.amount = 3000.00
budget.updated_at = datetime.utcnow()
db.session.commit()
```

### Calculating Budget vs Actual

```python
from models.transaction import Transaction
from sqlalchemy import func
from datetime import datetime

budget = Budget.query.get("budget_food_monthly")

# Calculate actual spending for the budget period
actual_spending = db.session.query(
    func.sum(Transaction.amount)
).filter_by(
    user_id=budget.user_id,
    category=budget.category_name,
    type='expense'
).filter(
    Transaction.date >= budget.start_date,
    Transaction.date <= budget.end_date
).scalar() or 0.0

# Calculate remaining budget
remaining = float(budget.amount) - float(actual_spending)

# Calculate percentage used
percentage_used = (float(actual_spending) / float(budget.amount) * 100) if float(budget.amount) > 0 else 0

# Determine status
if float(actual_spending) > float(budget.amount):
    status = 'over_budget'
elif percentage_used >= 80:
    status = 'approaching_budget'
else:
    status = 'on_track'
```

## Relationships

### User (Many-to-One)

A budget belongs to one user:

```python
# Get the user for a budget
user = budget.user
```

## Indexes

The following columns and combinations are indexed for performance:
- `user_id`: For fast user-based queries
- `start_date`: For date-based filtering
- `(user_id, category_id)`: Composite index for user + category queries
- `(user_id, period)`: Composite index for user + period queries

## Foreign Key Constraints

- `user_id` references `users.id` with `ON DELETE CASCADE`
  - Deleting a user automatically deletes all their budgets

## Timestamps

- `created_at`: Automatically set when the budget is created
- `updated_at`: Automatically updated whenever the budget record is modified
- `start_date`: Start of the budget period (set explicitly)
- `end_date`: End of the budget period (calculated or set explicitly)

All timestamps use UTC timezone.

## Budget Status Calculation

Budgets can have three statuses when compared to actual spending:

- `on_track`: Spending is within budget (< 80% used)
- `approaching_budget`: 80-100% of budget used
- `over_budget`: Spending exceeds budget (> 100% used)

## Budget Period Calculation

**Monthly Budget:**
- `start_date`: First day of the month (e.g., 2024-11-01)
- `end_date`: Last day of the month (e.g., 2024-11-30)

**Yearly Budget:**
- `start_date`: January 1st of the year (e.g., 2024-01-01)
- `end_date`: December 31st of the year (e.g., 2024-12-31)

## Budget Uniqueness

A user can have only one budget per category per period:
- Same `user_id` + `category_id` + `period` = update existing budget
- Different combination = create new budget

This is enforced at the application level, not the database level.

## File Selection Support

Budgets can be compared against transactions from a specific statement:
- Use `statementId` parameter in `/api/budgets/compare` endpoint
- Enables file-specific budget tracking
- Compares budget against transactions from that statement only

