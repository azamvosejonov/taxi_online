from database import SessionLocal
from models import User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n=== Users in Database ===")
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Phone: {user.phone}")
            print(f"Full Name: {user.full_name}")
            print(f"Is Active: {user.is_active}")
            print(f"Is Admin: {user.is_admin}")
            print(f"Created At: {user.created_at}")
            print("-" * 50)
    except Exception as e:
        print(f"Error listing users: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
