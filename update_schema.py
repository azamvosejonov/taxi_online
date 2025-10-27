import sqlite3
import sys
from pathlib import Path

def update_database_schema(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Create customers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL UNIQUE,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_ride_at TIMESTAMP,
            total_rides INTEGER DEFAULT 0
        )''')
        
        # Create index on phone for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone)')
        
        # 2. Add is_dispatcher column to users if it doesn't exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_dispatcher' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN is_dispatcher BOOLEAN DEFAULT 0')
        
        # 3. Add customer_id to rides if it doesn't exist
        cursor.execute("PRAGMA table_info(rides)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'customer_id' not in columns:
            cursor.execute('ALTER TABLE rides ADD COLUMN customer_id INTEGER')
            
            # Create a foreign key (SQLite needs to recreate the table to add FK)
            # We'll do this in a separate step after migrating data
        
        # 4. Make required columns NOT NULL if they aren't already
        # First, check if the columns are nullable
        cursor.execute('''SELECT name FROM pragma_table_info('users') 
                         WHERE "notnull" = 0 AND name IN ('phone', 'password', 'full_name')''')
        nullable_columns = [row[0] for row in cursor.fetchall()]
        
        for column in nullable_columns:
            # Set default empty string for any NULL values
            cursor.execute(f'UPDATE users SET {column} = "" WHERE {column} IS NULL')
            # Alter column to NOT NULL
            cursor.execute(f'ALTER TABLE users RENAME TO users_old')
            
            # Create new table with NOT NULL constraint
            cursor.execute(f'''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    phone TEXT NOT NULL,
                    password TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    profile_photo TEXT,
                    is_driver BOOLEAN DEFAULT 0,
                    is_dispatcher BOOLEAN DEFAULT 0,
                    is_admin BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    language TEXT DEFAULT 'uz',
                    emergency_contact TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    vehicle_type TEXT,
                    vehicle_number TEXT,
                    license_number TEXT,
                    vehicle_model TEXT,
                    vehicle_color TEXT,
                    rating REAL DEFAULT 5.0,
                    current_balance REAL DEFAULT 0.0,
                    required_deposit REAL DEFAULT 0.0,
                    is_approved BOOLEAN DEFAULT 0,
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    current_location TEXT,
                    city TEXT,
                    FOREIGN KEY (approved_by) REFERENCES users(id)
                )
            ''')
            
            # Copy data from old table to new table
            cursor.execute('''
                INSERT INTO users (
                    id, email, phone, password, full_name, profile_photo,
                    is_driver, is_admin, is_active, language, emergency_contact,
                    created_at, vehicle_type, vehicle_number, license_number,
                    vehicle_model, vehicle_color, rating, current_balance,
                    required_deposit, is_approved, approved_by, approved_at,
                    current_location, city, is_dispatcher
                ) SELECT 
                    id, email, COALESCE(phone, ''), COALESCE(password, ''), 
                    COALESCE(full_name, ''), profile_photo, is_driver, is_admin, 
                    is_active, language, emergency_contact, created_at, 
                    vehicle_type, vehicle_number, license_number, vehicle_model, 
                    vehicle_color, rating, current_balance, required_deposit, 
                    is_approved, approved_by, approved_at, current_location, 
                    city, 0 as is_dispatcher 
                FROM users_old
            ''')
            
            # Drop the old table
            cursor.execute('DROP TABLE users_old')
            
            # Recreate indexes and triggers if needed
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)')
        
        # 5. Create foreign key for customer_id in rides
        # First, get the current schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='rides'")
        table_sql = cursor.fetchone()[0]
        
        if 'FOREIGN KEY(customer_id) REFERENCES customers(id)' not in table_sql:
            # SQLite doesn't support adding foreign keys with ALTER TABLE, so we need to recreate the table
            cursor.execute('ALTER TABLE rides RENAME TO rides_old')
            
            # Create new table with foreign key
            cursor.execute('''
                CREATE TABLE rides (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    rider_id INTEGER,
                    driver_id INTEGER,
                    pickup_location TEXT,
                    dropoff_location TEXT,
                    current_location TEXT,
                    fare REAL,
                    duration INTEGER,
                    vehicle_type TEXT,
                    status TEXT,
                    created_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (rider_id) REFERENCES users(id),
                    FOREIGN KEY (driver_id) REFERENCES users(id)
                )
            ''')
            
            # Copy data from old table to new table
            cursor.execute('''
                INSERT INTO rides (
                    id, rider_id, driver_id, pickup_location, dropoff_location,
                    current_location, fare, duration, vehicle_type, status,
                    created_at, completed_at
                ) SELECT 
                    id, rider_id, driver_id, pickup_location, dropoff_location,
                    current_location, fare, duration, vehicle_type, status,
                    created_at, completed_at
                FROM rides_old
            ''')
            
            # Drop the old table
            cursor.execute('DROP TABLE rides_old')
            
            # Recreate indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rides_rider_id ON rides(rider_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rides_driver_id ON rides(driver_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rides_customer_id ON rides(customer_id)')
        
        # Commit changes
        conn.commit()
        print("Database schema updated successfully!")
        
    except Exception as e:
        print(f"Error updating database schema: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Get the database path (adjust as needed)
    db_path = Path("/home/azam/Desktop/yaratish/royaltaxi/royaltaxi.db")
    
    # Create parent directories if they don't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Update the database schema
    update_database_schema(str(db_path))
