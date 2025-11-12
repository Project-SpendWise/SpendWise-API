# Transaction Categorization

The transaction extraction system now includes AI-powered categorization using Groq, making your transactions ready for analysis.

## Features

- **Automatic Categorization**: Transactions are automatically categorized into standard financial categories
- **Subcategories**: Each transaction gets a specific subcategory for detailed analysis
- **Confidence Scores**: Each categorization includes a confidence score (0.0 to 1.0)
- **Tags**: Additional tags can be added for flexible filtering
- **Analysis-Ready**: Includes summary statistics for easy analysis

## Categories

The system uses the following standard categories:

- **Food & Dining**: Restaurants, Groceries, Fast Food, Coffee & Beverages, Food Delivery
- **Shopping**: Clothing & Apparel, Electronics, Home & Garden, Online Shopping, Department Stores
- **Bills & Utilities**: Electricity, Water, Gas, Internet & Phone, Cable & TV, Insurance
- **Transportation**: Gas & Fuel, Public Transit, Parking, Taxi & Rideshare, Vehicle Maintenance
- **Entertainment**: Movies & Theater, Sports & Recreation, Music & Concerts, Gaming, Streaming Services
- **Healthcare**: Doctor & Medical, Pharmacy, Dental, Hospital, Health Insurance
- **Education**: Tuition, Books & Supplies, Courses & Training
- **Personal Care**: Hair & Beauty, Gym & Fitness, Personal Services
- **Travel**: Hotels, Flights, Car Rental, Travel Services
- **Financial**: Bank Fees, Interest, Investment, Loan Payment, Transfer Fees
- **Income**: Salary, Freelance, Investment Returns, Refunds, Other Income
- **Transfers**: Internal Transfer, External Transfer, Payment to Others
- **Other**: Uncategorized, Miscellaneous

## Usage

### Basic Usage (with categorization)

```bash
python main.py --file samples/statement.pdf
```

Categorization is enabled by default.

### Skip Categorization

If you want to skip categorization (faster, but no categories):

```bash
python main.py --file samples/statement.pdf --no-categorize
```

## Output Format

Each transaction in the output JSON now includes:

```json
{
  "transaction_id": "TXN001",
  "date": "2025-10-15T14:30:00",
  "description": "Market alışverişi",
  "amount": -150.50,
  "currency": "TRY",
  "transaction_type": "debit",
  "category": "Food & Dining",
  "subcategory": "Groceries",
  "category_confidence": 0.95,
  "tags": ["grocery", "supermarket"]
}
```

## Analysis Summary

The output includes a `categorization_summary` section with:

- Total transactions count
- Statistics by category (count and total amount)
- Statistics by subcategory
- Statistics by transaction type (debit/credit)
- Top categories by amount

Example:

```json
{
  "categorization_summary": {
    "total_transactions": 150,
    "categories": {
      "Food & Dining": {
        "count": 45,
        "total_amount": 3250.50,
        "subcategories": {
          "Groceries": {
            "count": 30,
            "total_amount": 2100.00
          },
          "Restaurants": {
            "count": 15,
            "total_amount": 1150.50
          }
        }
      }
    },
    "by_type": {
      "debit": {
        "count": 120,
        "total_amount": 15000.00
      },
      "credit": {
        "count": 30,
        "total_amount": 5000.00
      }
    }
  }
}
```

## How It Works

1. **Extraction**: Transactions are extracted from bank statements
2. **Categorization**: Groq AI analyzes each transaction's description, amount, and context
3. **Batch Processing**: Large files are processed in batches to respect rate limits
4. **Summary Generation**: Statistics are automatically calculated for analysis

## Turkish Language Support

The categorization engine understands Turkish keywords and merchant names:

- "MARKET", "SÜPERMARKET", "MIGROS", "A101", "BIM" → Food & Dining > Groceries
- "RESTORAN", "CAFE", "KAHVE" → Food & Dining > Restaurants or Coffee & Beverages
- "AKARYAKIT", "BENZIN", "PETROL" → Transportation > Gas & Fuel
- "ELEKTRİK", "SU", "DOĞALGAZ" → Bills & Utilities
- "HASTANE", "ECZANE", "DOKTOR" → Healthcare
- "KART KOMİSYONU", "BANKA ÜCRETİ" → Financial > Bank Fees
- "MAAŞ", "MAAŞ ÖDEMESİ" → Income > Salary

## Performance

- Categorization adds minimal overhead (typically 2-5 seconds per 50 transactions)
- Batch processing respects Groq rate limits (30 requests per minute)
- Automatic delays between batches prevent rate limit errors

## Analysis Examples

With categorized transactions, you can easily:

1. **Spending Analysis**: See where your money goes by category
2. **Budget Tracking**: Compare spending against budgets by category
3. **Trend Analysis**: Track spending trends over time
4. **Merchant Analysis**: Identify top merchants in each category
5. **Financial Planning**: Make informed decisions based on categorized spending

## Integration

The categorized transactions are ready to be imported into:
- Personal finance apps
- Budgeting tools
- Financial analysis dashboards
- Database systems
- Spreadsheet applications

