"""
Database initialization script.
Creates all database tables if they don't exist.
"""
from app import create_app, db
from models import User, File, Statement, Transaction, Budget

def init_database():
    """Initialize database with all tables"""
    app = create_app()
    
    with app.app_context():
        # Import all models to ensure they're registered
        # This ensures SQLAlchemy knows about all tables
        print("Creating database tables...")
        
        # Create all tables
        db.create_all()
        
        print("✓ Database tables created successfully!")
        print("\nTables created:")
        print("  - users")
        print("  - files")
        print("  - statements")
        print("  - transactions")
        print("  - budgets")
        print("\nDatabase initialization complete!")

if __name__ == "__main__":
    init_database()


