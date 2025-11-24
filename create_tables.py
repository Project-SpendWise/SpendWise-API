"""
Simple script to create database tables.
Run this once to initialize the database.
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path is set
from app import create_app, db

# Import all models to register them with SQLAlchemy
from models.user import User
from models.file import File
from models.statement import Statement
from models.transaction import Transaction
from models.budget import Budget

def create_tables():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        try:
            db.create_all()
            print("✓ Database tables created successfully!")
            print("\nCreated tables:")
            print("  - users")
            print("  - files")
            print("  - statements")
            print("  - transactions")
            print("  - budgets")
            print("\nYou can now run the Flask server and test the endpoints.")
        except Exception as e:
            print(f"✗ Error creating tables: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_tables()


