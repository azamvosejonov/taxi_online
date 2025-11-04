"""
Create admin user for testing
"""
import os
from sqlalchemy.orm import Session
from database import engine, get_db
from models import User
from utils.helpers import hash_password
from datetime import datetime

def create_admin():
    """Create admin user from .env credentials"""
    
    # Get credentials from environment
    admin_phone = os.getenv('ADMIN_PHONE', '+998901234567')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    print(f"Creating admin user...")
    print(f"Phone: {admin_phone}")
    
    # Create database session
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.phone == admin_phone).first()
        
        if existing_admin:
            print(f"✅ Admin user already exists: {admin_phone}")
            
            # Update to admin if not already
            if not existing_admin.is_admin:
                existing_admin.is_admin = True
                existing_admin.is_approved = True
                existing_admin.is_active = True
                db.commit()
                print(f"✅ Updated user to admin")
            
            return existing_admin
        
        # Create new admin user
        hashed_password = hash_password(admin_password)
        
        admin_user = User(
            phone=admin_phone,
            first_name="Admin",
            last_name="User",
            full_name="Admin User",
            gender="Erkak",
            date_of_birth=datetime(1990, 1, 1),
            hashed_password=hashed_password,
            vehicle_make="Admin",
            vehicle_color="Admin",
            position="Administrator",
            license_plate="ADMIN001",
            tech_passport="ADMIN001",
            is_driver=True,
            is_dispatcher=True,
            is_admin=True,
            is_approved=True,
            is_active=True,
            current_balance=0.0,
            required_deposit=0.0,
            rating=5.0,
            total_rides=0
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Admin user created successfully!")
        print(f"   ID: {admin_user.id}")
        print(f"   Phone: {admin_user.phone}")
        print(f"   Password: {admin_password}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    create_admin()
