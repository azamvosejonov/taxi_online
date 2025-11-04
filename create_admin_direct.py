"""
Create admin user directly with SQL
"""
import sqlite3
import os
from utils.helpers import hash_password
from datetime import datetime

def create_admin_direct():
    """Create admin user using direct SQL"""
    
    # Get credentials from environment
    admin_phone = os.getenv('ADMIN_PHONE', '+998901234567')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    print(f"Creating admin user...")
    print(f"Phone: {admin_phone}")
    print(f"Password: {admin_password}")
    
    # Hash password
    hashed_password = hash_password(admin_password)
    
    # Connect to database
    conn = sqlite3.connect('instance/royaltaxi.db')
    cursor = conn.cursor()
    
    try:
        # Check if admin exists
        cursor.execute("SELECT id, is_admin FROM users WHERE phone = ?", (admin_phone,))
        existing = cursor.fetchone()
        
        if existing:
            user_id, is_admin = existing
            print(f"✅ User already exists: ID {user_id}")
            
            # Update to admin and set password
            cursor.execute("""
                UPDATE users 
                SET is_admin = 1, 
                    is_approved = 1, 
                    is_active = 1,
                    is_dispatcher = 1,
                    password = ?
                WHERE phone = ?
            """, (hashed_password, admin_phone))
            
            conn.commit()
            print(f"✅ Updated user to admin")
            return
        
        # Create new admin
        cursor.execute("""
            INSERT INTO users (
                phone, password, full_name,
                vehicle_type, vehicle_number, license_number, vehicle_model, vehicle_color,
                is_driver, is_dispatcher, is_admin,
                is_approved, is_active, current_balance, required_deposit,
                rating, total_rides, language
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            admin_phone, hashed_password, "Admin User",
            "economy", "ADMIN001", "ADMIN001", "Admin Car", "Black",
            1, 1, 1,
            1, 1, 0.0, 0.0,
            5.0, 0, "uz"
        ))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        print(f"✅ Admin user created successfully!")
        print(f"   ID: {user_id}")
        print(f"   Phone: {admin_phone}")
        print(f"   Password: {admin_password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    create_admin_direct()
