"""
Migration script to add profile fields to statements table.
Run this script to add profile metadata columns to existing statements table.

Usage:
    python migrate_add_profile_fields.py
"""
import sys
import os

# Ensure we can import from the project
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app import create_app, db
    from sqlalchemy import text
    
    print("Starting migration: Adding profile fields to statements table...")
    app = create_app()
    
    with app.app_context():
        # Check if columns already exist by trying to query them
        try:
            db.session.execute(text("SELECT profile_name FROM statements LIMIT 1"))
            print("Profile columns already exist. Migration not needed.")
            sys.exit(0)
        except Exception:
            # Columns don't exist, proceed with migration
            pass
        
        print("Adding profile columns to statements table...")
        
        # Add new columns with ALTER TABLE
        # SQLite doesn't support adding multiple columns in one statement, so we do them one by one
        migrations = [
            "ALTER TABLE statements ADD COLUMN profile_name VARCHAR(255)",
            "ALTER TABLE statements ADD COLUMN profile_description TEXT",
            "ALTER TABLE statements ADD COLUMN account_type VARCHAR(100)",
            "ALTER TABLE statements ADD COLUMN bank_name VARCHAR(255)",
            "ALTER TABLE statements ADD COLUMN color VARCHAR(7)",
            "ALTER TABLE statements ADD COLUMN icon VARCHAR(50)",
            "ALTER TABLE statements ADD COLUMN is_default BOOLEAN DEFAULT 0 NOT NULL"
        ]
        
        for migration in migrations:
            try:
                db.session.execute(text(migration))
                print(f"  ✓ {migration.split('ADD COLUMN')[1].strip()}")
            except Exception as e:
                # Column might already exist, check error message
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"  - Column already exists: {migration.split('ADD COLUMN')[1].strip()}")
                else:
                    raise
        
        # Update existing records: set profile_name to file_name if null
        print("\nUpdating existing records...")
        update_query = text("""
            UPDATE statements 
            SET profile_name = file_name 
            WHERE profile_name IS NULL OR profile_name = ''
        """)
        result = db.session.execute(update_query)
        updated_count = result.rowcount
        print(f"  ✓ Updated {updated_count} existing statements with default profile_name")
        
        # Commit all changes
        db.session.commit()
        
        print("\n✓ Migration completed successfully!")
        print("\nAdded columns:")
        print("  - profile_name")
        print("  - profile_description")
        print("  - account_type")
        print("  - bank_name")
        print("  - color")
        print("  - icon")
        print("  - is_default")
        print("\nExisting statements have been updated with default profile_name = file_name")
        
except ImportError as e:
    print(f"Error: {e}")
    print("\nMake sure:")
    print("  1. Your virtual environment is activated")
    print("  2. All dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error during migration: {e}")
    import traceback
    traceback.print_exc()
    db.session.rollback()
    sys.exit(1)

