"""
CRUD operations for users.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from models import User
from schemas import UserRegister, UserUpdate

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """Get a user by phone number."""
    return db.query(User).filter(User.phone == phone).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get a list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserRegister) -> User:
    """Create a new user."""
    db_user = User(
        phone=user.phone,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        date_of_birth=user.date_of_birth,
        hashed_password=user.password,  # Password should be hashed before this
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session, db_user: User, user_update: UserUpdate
) -> User:
    """Update a user's information."""
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user by ID."""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Create a user CRUD instance for easier access
user = {
    "get": get_user,
    "get_by_phone": get_user_by_phone,
    "get_multi": get_users,
    "create": create_user,
    "update": update_user,
    "delete": delete_user,
}
