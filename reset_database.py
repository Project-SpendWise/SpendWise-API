"""
Database Reset Script - WARNING: This will DELETE ALL DATA!

This script will:
1. Drop all database tables
2. Delete all uploaded files (optional)
3. Recreate all tables fresh

USE WITH CAUTION - This operation cannot be undone!

Usage:
    python reset_database.py
    
To also delete uploaded files:
    python reset_database.py --delete-files
"""
import sys
import os
import shutil
import argparse

# Ensure we can import from the project
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def confirm_reset():
    """Ask for confirmation before resetting"""
    print("\n" + "="*60)
    print("WARNING: DATABASE RESET")
    print("="*60)
    print("This will DELETE ALL DATA from the database:")
    print("  - All users")
    print("  - All files")
    print("  - All statements")
    print("  - All transactions")
    print("  - All budgets")
    print("\nThis operation CANNOT be undone!")
    print("="*60)
    
    response = input("\nType 'RESET' to confirm: ")
    if response != 'RESET':
        print("\nReset cancelled.")
        return False
    return True

def delete_uploaded_files():
    """Delete all uploaded files from the uploads directory"""
    upload_folder = os.path.join(project_root, 'uploads')
    if os.path.exists(upload_folder):
        print(f"\nDeleting uploaded files from: {upload_folder}")
        try:
            # Delete all files and subdirectories
            for root, dirs, files in os.walk(upload_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"  Deleted: {file_path}")
                    except Exception as e:
                        print(f"  Warning: Could not delete {file_path}: {e}")
            
            # Remove empty directories
            for root, dirs, files in os.walk(upload_folder, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        os.rmdir(dir_path)
                        print(f"  Removed directory: {dir_path}")
                    except Exception as e:
                        print(f"  Warning: Could not remove directory {dir_path}: {e}")
            
            print(f"✓ Uploaded files deleted successfully")
        except Exception as e:
            print(f"Error deleting files: {e}")
    else:
        print(f"Upload folder does not exist: {upload_folder}")

def reset_database(delete_files=False):
    """Reset the database by dropping and recreating all tables"""
    try:
        from app import create_app, db
        from sqlalchemy import inspect
        # Import all models to register them
        from models.user import User
        from models.file import File
        from models.statement import Statement
        from models.transaction import Transaction
        from models.budget import Budget
        
        print("\nInitializing database connection...")
        app = create_app()
        
        with app.app_context():
            # Get list of all tables
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if existing_tables:
                print(f"\nFound {len(existing_tables)} existing tables:")
                for table in existing_tables:
                    print(f"  - {table}")
                
                print("\nDropping all tables...")
                # Drop all tables
                db.drop_all()
                print("✓ All tables dropped")
            else:
                print("\nNo existing tables found")
            
            # Recreate all tables
            print("\nCreating fresh tables...")
            db.create_all()
            
            # Verify tables were created
            inspector = inspect(db.engine)
            new_tables = inspector.get_table_names()
            
            print("\n✓ Database reset successfully!")
            print(f"\nCreated {len(new_tables)} tables:")
            for table in sorted(new_tables):
                print(f"  - {table}")
            
            # Delete uploaded files if requested
            if delete_files:
                delete_uploaded_files()
            
            print("\n" + "="*60)
            print("Database reset complete!")
            print("You can now:")
            print("  1. Register a new user")
            print("  2. Upload statements")
            print("  3. Start fresh with clean data")
            print("="*60 + "\n")
            
    except ImportError as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("  1. Your virtual environment is activated")
        print("  2. All dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error resetting database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Reset the database (WARNING: Deletes all data)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reset_database.py              # Reset database only
  python reset_database.py --delete-files  # Reset database and delete uploaded files
  python reset_database.py --yes        # Skip confirmation (use with caution!)
        """
    )
    parser.add_argument(
        '--delete-files',
        action='store_true',
        help='Also delete all uploaded files from the uploads directory'
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt (use with extreme caution!)'
    )
    
    args = parser.parse_args()
    
    # Confirm unless --yes flag is used
    if not args.yes:
        if not confirm_reset():
            sys.exit(0)
    else:
        print("\n⚠️  Skipping confirmation (--yes flag used)")
        print("⚠️  Proceeding with database reset...\n")
    
    # Reset database
    reset_database(delete_files=args.delete_files)

if __name__ == '__main__':
    main()

