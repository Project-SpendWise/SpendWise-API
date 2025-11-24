# API Testing Guide

This guide explains how to test all SpendWise API endpoints.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Flask server:**
   ```bash
   python app.py
   ```
   
   The server should start on `http://localhost:5000`

## Running the Test Script

The comprehensive test script (`test_all_endpoints.py`) tests all endpoints and verifies business logic.

### Quick Start

```bash
python test_all_endpoints.py
```

### What the Test Script Does

The test script performs the following tests:

1. **Authentication Tests:**
   - User registration
   - User login
   - Get current user profile

2. **Statement Tests:**
   - Upload statement file
   - Get statement details
   - List all statements
   - Verify async processing

3. **Transaction Tests:**
   - Get all transactions
   - Get transactions filtered by statementId (file selection)
   - Get transactions filtered by category
   - Get transaction summary (all)
   - Get transaction summary filtered by statementId (file selection)

4. **Budget Tests:**
   - Create/update budget
   - List budgets
   - Get budget comparison (all)
   - Get budget comparison filtered by statementId (file selection)

5. **Analytics Tests:**
   - Category breakdown
   - Spending trends
   - Financial insights
   - Monthly trends
   - Category trends
   - Weekly patterns
   - Year-over-year comparison
   - Spending forecast
   - All analytics with statementId filtering (file selection)

6. **Error Handling Tests:**
   - Invalid token handling
   - Non-existent resource handling

### Test Output

The script prints:
- Request details (method, URL, headers, body)
- Response details (status code, response body)
- Test results (✓ for pass, ✗ for fail)
- Summary of all test suites

### Critical Business Logic Tests

The script specifically tests the **file selection feature** by:
- Filtering transactions by `statementId`
- Filtering transaction summaries by `statementId`
- Filtering budget comparisons by `statementId`
- Filtering all analytics endpoints by `statementId`

This verifies that the core business logic (file selection/profile system) works correctly.

## Manual Testing

You can also test endpoints manually using curl or a tool like Postman.

### Example: Register User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Example: Upload Statement

```bash
curl -X POST http://localhost:5000/api/statements/upload \
  -H "Authorization: Bearer <your_access_token>" \
  -F "file=@/path/to/statement.pdf"
```

### Example: Get Transactions by Statement ID

```bash
curl -X GET "http://localhost:5000/api/transactions?statementId=stmt_123456" \
  -H "Authorization: Bearer <your_access_token>"
```

## Expected Results

When running the test script, you should see:

1. **All authentication tests pass** - User can register and login
2. **Statement upload succeeds** - File is uploaded and processed
3. **Statement processing completes** - Status changes from "processing" to "processed"
4. **Transactions are generated** - 30-60 mock transactions created
5. **File selection works** - Filtering by statementId returns only that statement's transactions
6. **All analytics work** - All 8 analytics endpoints return data
7. **Budget comparison works** - Budgets can be compared against actual spending

## Troubleshooting

### Server Not Running

If you see connection errors:
- Make sure Flask server is running: `python app.py`
- Check that server is on `http://localhost:5000`
- Verify no firewall is blocking the connection

### Database Errors

If you see database errors:
- Make sure the database file exists: `instance/spendwise.db`
- The tables will be created automatically on first run
- If needed, delete the database file and restart the server

### Statement Processing Not Completing

If statement status stays "processing":
- Wait a few more seconds (processing takes 2-5 seconds)
- Check server logs for errors
- Verify the fake analyzer is working correctly

### Missing Dependencies

If you see import errors:
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're using the correct Python version (3.8+)

## Test Coverage

The test script covers:
- ✅ All authentication endpoints
- ✅ All statement endpoints
- ✅ All transaction endpoints (with filtering)
- ✅ All budget endpoints (with statementId support)
- ✅ All 8 analytics endpoints (with statementId support)
- ✅ Error handling
- ✅ File selection feature (critical business logic)

## Next Steps

After running tests:
1. Review the test output for any failures
2. Check server logs for detailed error messages
3. Verify database contains expected data
4. Test specific endpoints manually if needed
5. Integrate with frontend once all tests pass


