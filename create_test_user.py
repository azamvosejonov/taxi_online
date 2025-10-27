import sys
from database import SessionLocal
from models import User
from utils.helpers import hash_password

def create_test_user():
    db = SessionLocal()
    try:
        # Check if test user already exists
        test_email = "testuser@example.com"
        existing_user = db.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            print(f"Test user already exists with ID: {existing_user.id}")
            return existing_user
        
        # Create a new test user
        test_password = "testpassword123"
        hashed_password = hash_password(test_password)
        
        new_user = User(
            email=test_email,
            phone="+998901111111",
            password=hashed_password,
            full_name="Test User",
            is_active=True,
            is_admin=False,
            current_balance=0.0,
            required_deposit=0.0,
            total_rides=0,
            rating=5.0
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("Test user created successfully!")
        print(f"Email: {test_email}")
        print(f"Password: {test_password}")
        print(f"User ID: {new_user.id}")
        
        return new_user
        
    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {str(e)}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
