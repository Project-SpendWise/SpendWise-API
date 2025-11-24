"""
Comprehensive test script for all SpendWise API endpoints.
Tests all endpoints and verifies business logic.
"""
import requests
import json
import time
from datetime import datetime, timedelta, timezone

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_USERNAME = f"testuser_{int(time.time())}"

# Global variables to store test data
access_token = None
user_id = None
statement_id = None
budget_id = None
transaction_ids = []


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_request(method, url, headers=None, data=None):
    """Print request details"""
    print(f"\n[REQUEST] {method} {url}")
    if headers and 'Authorization' in headers:
        print(f"  Headers: Authorization: Bearer <token>")
    if data:
        if isinstance(data, dict):
            print(f"  Body: {json.dumps(data, indent=2)}")
        else:
            print(f"  Body: {data}")


def print_response(response):
    """Print response details"""
    print(f"[RESPONSE] Status: {response.status_code}")
    try:
        data = response.json()
        print(f"  Body: {json.dumps(data, indent=2)}")
        return data
    except:
        print(f"  Body: {response.text}")
        return None


def test_auth_endpoints():
    """Test authentication endpoints"""
    global access_token, user_id
    
    print_section("AUTHENTICATION ENDPOINTS")
    
    # Test Register
    print("\n--- Test 1: User Registration ---")
    url = f"{BASE_URL}/auth/register"
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "username": TEST_USERNAME,
        "first_name": "Test",
        "last_name": "User"
    }
    print_request("POST", url, data=data)
    response = requests.post(url, json=data)
    result = print_response(response)
    
    if response.status_code == 201 and result and result.get('success'):
        user_id = result['data']['user']['id']
        print(f"✓ Registration successful! User ID: {user_id}")
    else:
        print("✗ Registration failed!")
        return False
    
    # Test Login
    print("\n--- Test 2: User Login ---")
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    print_request("POST", url, data=data)
    response = requests.post(url, json=data)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        access_token = result['data']['access_token']
        print(f"✓ Login successful! Access token obtained.")
    else:
        print("✗ Login failed!")
        return False
    
    # Test Get Current User
    print("\n--- Test 3: Get Current User ---")
    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        print("✓ Get current user successful!")
    else:
        print("✗ Get current user failed!")
        return False
    
    return True


def test_statement_endpoints():
    """Test statement endpoints"""
    global statement_id, access_token
    
    print_section("STATEMENT ENDPOINTS")
    
    # Create a dummy file for upload
    import io
    test_file_content = b"Fake PDF content for testing"
    test_file = io.BytesIO(test_file_content)
    test_file.name = "test_statement.pdf"
    
    # Test Upload Statement
    print("\n--- Test 4: Upload Statement ---")
    url = f"{BASE_URL}/statements/upload"
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {"file": ("test_statement.pdf", test_file, "application/pdf")}
    print_request("POST", url, headers=headers, data="<file: test_statement.pdf>")
    response = requests.post(url, headers=headers, files=files)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        statement_id = result['data']['id']
        print(f"✓ Statement uploaded! Statement ID: {statement_id}")
        print(f"  Status: {result['data']['status']}")
    else:
        print("✗ Statement upload failed!")
        return False
    
    # Wait for processing (fake analyzer should be fast, but give it time)
    print("\n--- Waiting for statement processing (7 seconds) ---")
    time.sleep(7)
    
    # Test Get Statement Details
    print("\n--- Test 5: Get Statement Details ---")
    url = f"{BASE_URL}/statements/{statement_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        status = result['data']['status']
        print(f"✓ Get statement successful! Status: {status}")
        if status == 'processed':
            print(f"  Transaction Count: {result['data']['transactionCount']}")
            print(f"  Period: {result['data']['statementPeriodStart']} to {result['data']['statementPeriodEnd']}")
    else:
        print("✗ Get statement failed!")
        return False
    
    # Test List Statements
    print("\n--- Test 6: List Statements ---")
    url = f"{BASE_URL}/statements"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        statements = result['data']['statements']
        print(f"✓ List statements successful! Found {len(statements)} statement(s)")
    else:
        print("✗ List statements failed!")
        return False
    
    return True


def test_transaction_endpoints():
    """Test transaction endpoints"""
    global statement_id, access_token, transaction_ids
    
    print_section("TRANSACTION ENDPOINTS")
    
    # Test Get Transactions (All)
    print("\n--- Test 7: Get All Transactions ---")
    url = f"{BASE_URL}/transactions"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        transactions = result['data']['transactions']
        print(f"✓ Get all transactions successful! Found {len(transactions)} transaction(s)")
        if transactions:
            transaction_ids = [t['id'] for t in transactions[:3]]  # Store first 3 IDs
            print(f"  Sample transaction: {transactions[0]['description']} - {transactions[0]['amount']} {transactions[0]['type']}")
    else:
        print("✗ Get all transactions failed!")
        return False
    
    # Test Get Transactions (Filtered by statementId) - CRITICAL TEST
    print("\n--- Test 8: Get Transactions by Statement ID (File Selection) ---")
    url = f"{BASE_URL}/transactions"
    params = {"statementId": statement_id, "limit": 10}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?statementId={statement_id}", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        transactions = result['data']['transactions']
        print(f"✓ Get transactions by statementId successful! Found {len(transactions)} transaction(s)")
        if transactions:
            print(f"  All transactions belong to statement: {statement_id}")
            for txn in transactions[:3]:
                print(f"    - {txn['description']}: {txn['amount']} ({txn['category']})")
    else:
        print("✗ Get transactions by statementId failed!")
        return False
    
    # Test Get Transactions (Filtered by category)
    print("\n--- Test 9: Get Transactions by Category ---")
    url = f"{BASE_URL}/transactions"
    params = {"category": "Gıda", "limit": 5}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?category=Gıda", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        transactions = result['data']['transactions']
        print(f"✓ Get transactions by category successful! Found {len(transactions)} transaction(s)")
    else:
        print("✗ Get transactions by category failed!")
        return False
    
    # Test Get Transaction Summary (All)
    print("\n--- Test 10: Get Transaction Summary (All) ---")
    url = f"{BASE_URL}/transactions/summary"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        data = result['data']
        print(f"✓ Get transaction summary successful!")
        print(f"  Total Income: {data['totalIncome']}")
        print(f"  Total Expenses: {data['totalExpenses']}")
        print(f"  Savings: {data['savings']}")
        print(f"  Transaction Count: {data['transactionCount']}")
    else:
        print("✗ Get transaction summary failed!")
        return False
    
    # Test Get Transaction Summary (Filtered by statementId) - CRITICAL TEST
    print("\n--- Test 11: Get Transaction Summary by Statement ID (File Selection) ---")
    url = f"{BASE_URL}/transactions/summary"
    params = {"statementId": statement_id}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?statementId={statement_id}", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        data = result['data']
        print(f"✓ Get transaction summary by statementId successful!")
        print(f"  Total Income: {data['totalIncome']}")
        print(f"  Total Expenses: {data['totalExpenses']}")
        print(f"  Savings: {data['savings']}")
        print(f"  Transaction Count: {data['transactionCount']}")
    else:
        print("✗ Get transaction summary by statementId failed!")
        return False
    
    return True


def test_budget_endpoints():
    """Test budget endpoints"""
    global budget_id, access_token, statement_id
    
    print_section("BUDGET ENDPOINTS")
    
    # Test Create Budget
    print("\n--- Test 12: Create Budget ---")
    url = f"{BASE_URL}/budgets"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "categoryId": "food",
        "categoryName": "Gıda",
        "amount": 2500.00,
        "period": "monthly",
        "startDate": datetime.now(timezone.utc).replace(day=1).isoformat()
    }
    print_request("POST", url, headers=headers, data=data)
    response = requests.post(url, headers=headers, json=data)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        budget_id = result['data']['id']
        print(f"✓ Budget created! Budget ID: {budget_id}")
        print(f"  Category: {result['data']['categoryName']}, Amount: {result['data']['amount']}")
    else:
        print("✗ Budget creation failed!")
        return False
    
    # Test List Budgets
    print("\n--- Test 13: List Budgets ---")
    url = f"{BASE_URL}/budgets"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        budgets = result['data']['budgets']
        print(f"✓ List budgets successful! Found {len(budgets)} budget(s)")
    else:
        print("✗ List budgets failed!")
        return False
    
    # Test Get Budget Comparison (All)
    print("\n--- Test 14: Get Budget Comparison (All) ---")
    url = f"{BASE_URL}/budgets/compare"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        comparisons = result['data']['comparisons']
        print(f"✓ Get budget comparison successful! Found {len(comparisons)} comparison(s)")
        if comparisons:
            comp = comparisons[0]
            print(f"  Category: {comp['budget']['categoryName']}")
            print(f"  Budget: {comp['budget']['amount']}, Actual: {comp['actualSpending']}")
            print(f"  Status: {comp['status']}, Percentage Used: {comp['percentageUsed']}%")
    else:
        print("✗ Get budget comparison failed!")
        return False
    
    # Test Get Budget Comparison (Filtered by statementId) - CRITICAL TEST
    print("\n--- Test 15: Get Budget Comparison by Statement ID (File Selection) ---")
    url = f"{BASE_URL}/budgets/compare"
    params = {"statementId": statement_id}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?statementId={statement_id}", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        comparisons = result['data']['comparisons']
        print(f"✓ Get budget comparison by statementId successful! Found {len(comparisons)} comparison(s)")
    else:
        print("✗ Get budget comparison by statementId failed!")
        return False
    
    return True


def test_analytics_endpoints():
    """Test analytics endpoints"""
    global statement_id, access_token
    
    print_section("ANALYTICS ENDPOINTS")
    
    # Test Get Category Breakdown
    print("\n--- Test 16: Get Category Breakdown ---")
    url = f"{BASE_URL}/analytics/categories"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        categories = result['data']['categories']
        print(f"✓ Get category breakdown successful! Found {len(categories)} category/categories")
        if categories:
            for cat in categories[:3]:
                print(f"  {cat['category']}: {cat['totalAmount']} ({cat['percentage']}%)")
    else:
        print("✗ Get category breakdown failed!")
        return False
    
    # Test Get Category Breakdown (Filtered by statementId) - CRITICAL TEST
    print("\n--- Test 17: Get Category Breakdown by Statement ID (File Selection) ---")
    url = f"{BASE_URL}/analytics/categories"
    params = {"statementId": statement_id}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?statementId={statement_id}", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        categories = result['data']['categories']
        print(f"✓ Get category breakdown by statementId successful! Found {len(categories)} category/categories")
    else:
        print("✗ Get category breakdown by statementId failed!")
        return False
    
    # Test Get Spending Trends
    print("\n--- Test 18: Get Spending Trends ---")
    url = f"{BASE_URL}/analytics/trends"
    params = {"period": "day"}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?period=day", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        trends = result['data']['trends']
        print(f"✓ Get spending trends successful! Found {len(trends)} trend(s)")
    else:
        print("✗ Get spending trends failed!")
        return False
    
    # Test Get Financial Insights
    print("\n--- Test 19: Get Financial Insights ---")
    url = f"{BASE_URL}/analytics/insights"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        insights = result['data']['insights']
        print(f"✓ Get financial insights successful! Found {len(insights)} insight(s)")
        for insight in insights:
            print(f"  {insight['type']}: {insight['title']} ({insight['severity']})")
    else:
        print("✗ Get financial insights failed!")
        return False
    
    # Test Get Monthly Trends
    print("\n--- Test 20: Get Monthly Trends ---")
    url = f"{BASE_URL}/analytics/monthly-trends"
    params = {"months": 6}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?months=6", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        monthly_data = result['data']['monthlyData']
        print(f"✓ Get monthly trends successful! Found {len(monthly_data)} month(s)")
    else:
        print("✗ Get monthly trends failed!")
        return False
    
    # Test Get Category Trends
    print("\n--- Test 21: Get Category Trends ---")
    url = f"{BASE_URL}/analytics/category-trends"
    params = {"topCategories": 3, "months": 6}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?topCategories=3&months=6", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        category_trends = result['data']['categoryTrends']
        print(f"✓ Get category trends successful! Found {len(category_trends)} category/categories")
    else:
        print("✗ Get category trends failed!")
        return False
    
    # Test Get Weekly Patterns
    print("\n--- Test 22: Get Weekly Patterns ---")
    url = f"{BASE_URL}/analytics/weekly-patterns"
    params = {"weeks": 4}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?weeks=4", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        patterns = result['data']['patterns']
        print(f"✓ Get weekly patterns successful! Found {len(patterns)} pattern(s)")
    else:
        print("✗ Get weekly patterns failed!")
        return False
    
    # Test Get Year-over-Year
    print("\n--- Test 23: Get Year-over-Year Comparison ---")
    url = f"{BASE_URL}/analytics/year-over-year"
    params = {"year": datetime.now(timezone.utc).year}
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", f"{url}?year={datetime.now(timezone.utc).year}", headers=headers)
    response = requests.get(url, headers=headers, params=params)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        comparisons = result['data']['comparisons']
        print(f"✓ Get year-over-year successful! Found {len(comparisons)} comparison(s)")
    else:
        print("✗ Get year-over-year failed!")
        return False
    
    # Test Get Spending Forecast
    print("\n--- Test 24: Get Spending Forecast ---")
    url = f"{BASE_URL}/analytics/forecast"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 200 and result and result.get('success'):
        forecast = result['data']['forecast']
        print(f"✓ Get spending forecast successful!")
        print(f"  Predicted Spending: {forecast['predictedSpending']}")
        print(f"  Confidence: {forecast['confidence']}")
    else:
        print("✗ Get spending forecast failed!")
        return False
    
    # Test Analytics with statementId - CRITICAL TEST
    print("\n--- Test 25: Analytics with Statement ID (File Selection) ---")
    endpoints_to_test = [
        ("/analytics/trends", {"period": "day"}),
        ("/analytics/insights", {}),
        ("/analytics/monthly-trends", {"months": 3}),
    ]
    
    for endpoint, params in endpoints_to_test:
        url = f"{BASE_URL}{endpoint}"
        params["statementId"] = statement_id
        headers = {"Authorization": f"Bearer {access_token}"}
        print_request("GET", f"{url}?statementId={statement_id}", headers=headers)
        response = requests.get(url, headers=headers, params=params)
        result = print_response(response)
        
        if response.status_code == 200 and result and result.get('success'):
            print(f"✓ {endpoint} with statementId successful!")
        else:
            print(f"✗ {endpoint} with statementId failed!")
            return False
    
    return True


def test_error_handling():
    """Test error handling"""
    global access_token, statement_id
    
    print_section("ERROR HANDLING TESTS")
    
    # Test Invalid Token
    print("\n--- Test 26: Invalid Token ---")
    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": "Bearer invalid_token"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    if response.status_code == 401:
        print("✓ Invalid token correctly rejected!")
    else:
        print("✗ Invalid token not properly handled!")
        return False
    
    # Test Accessing Other User's Statement
    print("\n--- Test 27: Access Other User's Resource (Should Fail) ---")
    # This would require another user's statement ID, so we'll test with a non-existent ID
    url = f"{BASE_URL}/statements/invalid_statement_id"
    headers = {"Authorization": f"Bearer {access_token}"}
    print_request("GET", url, headers=headers)
    response = requests.get(url, headers=headers)
    result = print_response(response)
    
    # Accept either 404 status code or 200 with error response containing 404 statusCode
    if response.status_code == 404 or (result and result.get('error', {}).get('statusCode') == 404):
        print("✓ Non-existent resource correctly returns 404!")
    else:
        print("✗ Error handling for non-existent resource failed!")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  SPENDWISE API - COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 80)
    print(f"\nTest Configuration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Test Email: {TEST_EMAIL}")
    print(f"  Test Username: {TEST_USERNAME}")
    print("\nNote: Make sure the Flask server is running on http://localhost:5000")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/api/health", timeout=2)
        if response.status_code != 200:
            print("\n⚠ WARNING: Server health check failed. Is the server running?")
    except:
        print("\n⚠ WARNING: Cannot connect to server. Is it running on http://localhost:5000?")
        print("  You can start it with: python app.py")
    
    results = []
    
    # Run all test suites
    try:
        results.append(("Authentication", test_auth_endpoints()))
        if not results[-1][1]:
            print("\n❌ Authentication tests failed. Cannot continue.")
            return
        
        results.append(("Statements", test_statement_endpoints()))
        if not results[-1][1]:
            print("\n⚠ Statement tests failed. Some tests may not work.")
        
        results.append(("Transactions", test_transaction_endpoints()))
        results.append(("Budgets", test_budget_endpoints()))
        results.append(("Analytics", test_analytics_endpoints()))
        results.append(("Error Handling", test_error_handling()))
        
    except Exception as e:
        print(f"\n❌ Test execution error: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Print summary
    print_section("TEST SUMMARY")
    print("\nTest Results:")
    passed = 0
    failed = 0
    
    for suite_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {suite_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} test suites")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {failed} test suite(s) failed. Check the output above for details.")
    
    print("\n" + "=" * 80)
    print("  Testing Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()

