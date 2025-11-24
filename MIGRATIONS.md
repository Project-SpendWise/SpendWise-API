# Database Migrations

## Initial Setup

To create database migrations for the new models (Statement, Transaction, Budget), run the following commands:

```bash
# Activate your virtual environment first
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

# Initialize migrations (if not already done)
flask db init

# Create migration for new models
flask db migrate -m "Add statements, transactions, and budgets tables"

# Apply migration
flask db upgrade
```

## Note

The application will automatically create tables using `db.create_all()` when first run, but using migrations is the recommended approach for production deployments.

