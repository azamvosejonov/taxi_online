"""
Add missing columns to database
"""
import sqlite3

def fix_database():
    """Add all missing columns to users table"""
    
    conn = sqlite3.connect('instance/royaltaxi.db')
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(users);")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    print("Existing columns:", existing_columns)
    print("\nAdding missing columns...")
    
    # Define all required columns with their types and defaults
    required_columns = {
        'is_on_duty': ('BOOLEAN', '0'),
        'hashed_password': ('TEXT', 'NULL'),
    }
    
    added_count = 0
    for column_name, (column_type, default_value) in required_columns.items():
        if column_name not in existing_columns:
            try:
                sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                if default_value != 'NULL':
                    sql += f" DEFAULT {default_value}"
                
                cursor.execute(sql)
                print(f"✅ Added column: {column_name}")
                added_count += 1
            except Exception as e:
                print(f"❌ Error adding {column_name}: {e}")
        else:
            print(f"⊘ Column {column_name} already exists")
    
    # Copy password to hashed_password if needed
    if 'hashed_password' in required_columns and 'hashed_password' not in existing_columns:
        try:
            cursor.execute("UPDATE users SET hashed_password = password WHERE hashed_password IS NULL")
            print("✅ Copied password to hashed_password")
        except Exception as e:
            print(f"⚠️ Could not copy password: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database fix complete! Added {added_count} columns.")
    print("\nNow restart the server:")
    print("  CTRL+C")
    print("  uvicorn main:app --host 0.0.0.0 --port 8080 --reload")

if __name__ == "__main__":
    fix_database()
