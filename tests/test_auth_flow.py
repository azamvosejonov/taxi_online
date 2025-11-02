"""
Test authentication flow with phone-based authentication
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import User

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_register_new_user():
    # Clean up test data
    db = next(override_get_db())
    db.query(User).filter(User.phone == "+998901234567").delete()
    db.commit()
    
    # Test registration
    response = client.post(
        "/api/v1/auth/register",
        json={
            "phone": "+998901234567",
            "password": "test1234",
            "first_name": "Test",
            "last_name": "User",
            "is_driver": True,
            "vehicle_make": "Chevrolet",
            "vehicle_model": "Cobalt",
            "vehicle_color": "Oq",
            "license_plate": "01A123AA",
            "tech_passport": "AAB1234567",
            "position": "Haydovchi"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["phone"] == "+998901234567"
    assert data["user"]["is_driver"] == True

def test_login_with_phone():
    # Test login with correct credentials
    response = client.post(
        "/api/v1/auth/login",
        json={
            "phone": "+998901234567",
            "password": "test1234"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["phone"] == "+998901234567"

def test_login_with_wrong_password():
    # Test login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "phone": "+998901234567",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect phone number or password" in response.text

def test_register_duplicate_phone():
    # Test duplicate phone registration
    response = client.post(
        "/api/v1/auth/register",
        json={
            "phone": "+998901234567",  # Already registered
            "password": "anotherpass",
            "first_name": "Another",
            "last_name": "User"
        }
    )
    assert response.status_code == 400
    assert "Bu telefon raqam allaqachon ro'yxatdan o'tgan" in response.text

def test_get_current_user():
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "phone": "+998901234567",
            "password": "test1234"
        }
    )
    token = login_response.json()["access_token"]
    
    # Test getting current user with token
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "+998901234567"
    assert data["first_name"] == "Test"
    assert data["is_driver"] == True

# Clean up after tests
def test_cleanup():
    db = next(override_get_db())
    db.query(User).filter(User.phone == "+998901234567").delete()
    db.commit()
    db.close()
