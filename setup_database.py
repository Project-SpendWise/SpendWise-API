"""
Database setup script - Run this once to create all tables.
Make sure your virtual environment is activated before running.
"""
import sys
import os

# Ensure we can import from the project
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app import create_app, db
    # Import all models to register them
    from models.user import User
    from models.file import File
    from models.statement import Statement
    from models.transaction import Transaction
    from models.budget import Budget
    
    print("Initializing database...")
    app = create_app()
    
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("\n✓ Database tables created successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - files") 
        print("  - statements")
        print("  - transactions")
        print("  - budgets")
        print("\nYou can now start the Flask server and test the endpoints.")
        
except ImportError as e:
    print(f"Error: {e}")
    print("\nMake sure:")
    print("  1. Your virtual environment is activated")
    print("  2. All dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error creating tables: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


