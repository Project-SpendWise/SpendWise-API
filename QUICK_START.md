# Quick Start Guide

## Step 1: Create Database Tables

**IMPORTANT**: Before testing endpoints, you must create the database tables.

### Option A: Automatic (Recommended)
Just restart your Flask server - it will create tables automatically:
```bash
python app.py
```

### Option B: Manual Setup
If tables weren't created automatically, run:
```bash
python setup_database.py
```

## Step 2: Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Step 3: Run Tests

In another terminal:
```bash
python test_all_endpoints.py
```

## Troubleshooting

### "no such table: statements" Error

This means the database tables weren't created. Solutions:

1. **Restart the Flask server** - Tables are created automatically on startup
2. **Run setup script**: `python setup_database.py`
3. **Delete and recreate**: Delete `instance/spendwise.db` and restart server

### Tables Already Exist

If you see "table already exists" errors, that's fine - the tables are already created.

## Integration Notes

- **File Upload** (`/api/files/upload`) - General file storage (already working)
- **Statement Upload** (`/api/statements/upload`) - Bank statements with transaction extraction
- Both use the same file storage utilities
- Statements are processed asynchronously to extract transactions
- Files and Statements are separate entities (statements are for financial processing)


