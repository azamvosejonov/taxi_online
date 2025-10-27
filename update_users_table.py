import sqlite3
from pathlib import Path

# Path to your SQLite database
db_path = Path("/home/azam/Desktop/yaratish/royaltaxi/royaltaxi.db")

# Check if the database exists
if not db_path.exists():
    print(f"Error: Database file not found at {db_path}")
    exit(1)

try:
    # Connect to the database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if the column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'total_rides' not in columns:
        print("Adding 'total_rides' column to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN total_rides INTEGER DEFAULT 0")
        print("Column 'total_rides' added successfully.")
    else:
        print("Column 'total_rides' already exists in 'users' table.")
    
    # Commit changes and close the connection
    conn.commit()
    print("Database update completed successfully.")
    
except sqlite3.Error as e:
    print(f"Database error: {e}")
    
finally:
    if conn:
        conn.close()
