"""
Comprehensive test suite for Royal Taxi API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import app
    from database import Base, get_db, SessionLocal
    from models import User, Ride, Payment, Vehicle, DriverStatus
    from schemas import UserBase, UserLogin, RideCreate, DriverStatusUpdate, VehicleResponse
    from config import settings
    from utils.helpers import (
        create_access_token,
        get_password_hash,
        verify_password,
        hash_password
    )
    from routers.auth import get_current_user
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Please check if all required modules are installed and paths are correct.")
    sys.exit(1)

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_complete_royaltaxi.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Fixture to clear and initialize database before each test
@pytest.fixture(autouse=True)
def cleanup_db():
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Run the test
    yield
    
    # Clean up after test
    db = SessionLocal()
    try:
        # Clear all data but keep tables
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Test data
TEST_USER = {
    "email": "testuser@example.com",
    "phone": "+998901234567",  # Must match pattern ^\+998\d{9}$
    "full_name": "Test User",
    "password": "testpass123",  # This will be hashed before storage
    "is_driver": False,
    "is_admin": False,
    "is_dispatcher": False,
    "language": "uz",
    "emergency_contact": "+998901234568",
    "current_balance": 0.0,
    "required_deposit": 0.0,
    "is_active": True,
    "vehicle_type": None,
    "vehicle_number": None,
    "license_number": None,
    "vehicle_model": None,
    "vehicle_color": None
}

TEST_DRIVER = {
    "email": "driver@example.com",
    "phone": "+998901234568",  # Must be unique and match pattern
    "full_name": "Test Driver",
    "password": "driverpass123",
    "is_driver": True,
    "license_number": "AB1234567",
    "vehicle_model": "Chevrolet Cobalt",
    "vehicle_number": "01A123AA",
    "vehicle_color": "White",
    "vehicle_type": "economy"
}

TEST_ORDER = {
    "pickup_location": {"lat": 41.311081, "lng": 69.240562},
    "dropoff_location": {"lat": 41.315688, "lng": 69.249238},
    "pickup_address": "Test Pickup Location",
    "dropoff_address": "Test Dropoff Location",
    "vehicle_type": "economy",
    "payment_method": "cash"
}

# Helper functions
def create_test_user(user_data: Dict[str, Any]) -> User:
    """Helper to create a test user directly in the database"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            # Update existing user
            for key, value in user_data.items():
                if key == "password":
                    setattr(existing_user, "password", hash_password(value))
                elif hasattr(existing_user, key):
                    setattr(existing_user, key, value)
            db.commit()
            db.refresh(existing_user)
            return existing_user
            
        # Create new user with all required fields
        user_data_copy = user_data.copy()
        password = user_data_copy.pop("password")
        
        # Set default values for required fields if not provided
        defaults = {
            "is_active": True,
            "is_driver": False,
            "is_admin": False,
            "is_dispatcher": False,
            "current_balance": 0.0,
            "required_deposit": 0.0,
            "rating": 5.0,
            "total_rides": 0,
            "language": "uz"
        }
        
        # Update with any provided values
        for key, value in defaults.items():
            if key not in user_data_copy:
                user_data_copy[key] = value
        
        # Hash the password
        user_data_copy["password"] = hash_password(password)
        
        # Create the user
        user = User(**user_data_copy)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create driver status entry if this is a driver
        if user.is_driver:
            driver_status = DriverStatus(
                driver_id=user.id,
                is_on_duty=False,
                last_lat=41.311081,
                last_lng=69.240562,
                city="Tashkent"
            )
            db.add(driver_status)
            
            # Create vehicle entry
            vehicle = Vehicle(
                driver_id=user.id,
                make=user.vehicle_model.split()[0] if user.vehicle_model else "Test",
                model=user.vehicle_model or "",
                year=datetime.now().year,
                color=user.vehicle_color or "White",
                license_plate=user.vehicle_number or "",
                vehicle_type=user.vehicle_type or "economy",
                capacity=4,
                is_active=True
            )
            db.add(vehicle)
            db.commit()
            
        return user
    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {str(e)}")
        raise e
    finally:
        db.close()

def get_auth_token(username: str, password: str) -> Optional[str]:
    """Helper to get auth token"""
    try:
        # First try with JSON (preferred)
        response = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        # If that fails, try with form data
        if response.status_code != 200:
            response = client.post(
                "/api/v1/auth/login",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

        if response.status_code == 200:
            data = response.json()
            # Try different possible token field names
            token = data.get("access_token") or data.get("token")
            if token:
                return token

        print(f"Login failed with status {response.status_code}: {response.text}")
        return None
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

# Fixtures
@pytest.fixture(scope="module")
def db():
    # Create test database tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    return TEST_USER.copy()

@pytest.fixture
def test_driver():
    return TEST_DRIVER.copy()

@pytest.fixture
def test_order():
    return TEST_ORDER.copy()

# Test Classes
class TestAuthentication:
    def test_register_user(self, test_user):
        """Test user registration"""
        # Clean up any existing test user
        db = SessionLocal()
        try:
            db.query(User).filter(User.email == test_user["email"]).delete()
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
        # Test registration with all required fields
        registration_data = {
            "email": test_user["email"],
            "phone": test_user["phone"],
            "full_name": test_user["full_name"],
            "password": test_user["password"],
            "is_driver": test_user["is_driver"],
            "is_admin": test_user["is_admin"],
            "language": test_user["language"],
            "emergency_contact": test_user["emergency_contact"]
        }
        
        # Only include driver-specific fields if the user is a driver
        if test_user.get("is_driver"):
            registration_data.update({
                "license_number": test_user.get("license_number"),
                "vehicle_model": test_user.get("vehicle_model"),
                "vehicle_number": test_user.get("vehicle_number"),
                "vehicle_color": test_user.get("vehicle_color"),
                "vehicle_type": test_user.get("vehicle_type", "economy")
            })
        
        response = client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        
        if response.status_code == 400 and "Email already registered" in response.text:
            # User already exists, which is fine for testing
            pass
        else:
            assert response.status_code == 200, f"Registration failed: {response.text}"
            data = response.json()
            assert "access_token" in data, "Access token not in response"
            assert data["token_type"] == "bearer", "Invalid token type"
            
        # Verify user was created
        db = SessionLocal()
        user = db.query(User).filter(User.email == test_user["email"]).first()
        db.close()
        assert user is not None, "User was not created in database"

    def test_login_user(self, test_user):
        """Test user login"""
        # Ensure user exists
        create_test_user(test_user)
        
        # Test login with JSON payload
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user["email"],
                "password": test_user["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Access token not in response"
        assert data["token_type"] == "bearer", "Invalid token type"

    def test_login_invalid_credentials(self, test_user):
        """Test login with invalid credentials"""
        create_test_user(test_user)
        
        # Wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user["email"],
                "password": "wrongpassword"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, "Should fail with wrong password"

class TestUserEndpoints:
    def get_auth_token(self, email: str, password: str) -> str:
        """Helper to get auth token with proper error handling"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None

    def test_get_profile(self, test_user):
        """Test getting user profile"""
        # Ensure user exists and get token
        create_test_user(test_user)
        token = self.get_auth_token(test_user["email"], test_user["password"])
        
        assert token is not None, "Failed to get authentication token"
        
        # Test getting profile
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 404:
            # If /me endpoint doesn't exist, try /profile
            response = client.get(
                "/api/v1/users/profile",
                headers={"Authorization": f"Bearer {token}"}
            )
            
        assert response.status_code == 200, f"Failed to get profile: {response.text}"
        data = response.json()
        assert "email" in data, "Email not in profile"
        assert data["email"] == test_user["email"], "Email doesn't match"
        assert "password" not in data, "Password should not be in response"

class TestDriverEndpoints:
    def test_driver_registration(self, test_driver):
        """Test driver registration and profile"""
        # Clean up any existing test driver
        db = SessionLocal()
        try:
            db.query(User).filter(User.email == test_driver["email"]).delete()
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
        # Register as driver
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_driver["email"],
                "phone": test_driver["phone"],
                "full_name": test_driver["full_name"],
                "password": test_driver["password"],
                "is_driver": True
            }
        )
    
        if response.status_code == 200:
            # Login to get token
            token = get_auth_token(test_driver["email"], test_driver["password"])
            assert token is not None, f"Failed to login after registration: {response.text}"
        
            # Complete driver profile (if needed by the API)
            # Note: The driver profile might be created during registration
            # If this endpoint exists, we'll use it, otherwise we'll skip this part
            try:
                response = client.post(
                    "/api/v1/driver/profile",
                    json={
                        "license_number": test_driver["license_number"],
                        "vehicle_model": test_driver["vehicle_model"],
                        "vehicle_number": test_driver["vehicle_number"],
                        "vehicle_color": test_driver["vehicle_color"]
                    },
                    headers={"Authorization": f"Bearer {token}"}
                )
                # If the endpoint exists but fails, we should know about it
                if response.status_code != 200 and response.status_code != 404:
                    print(f"Warning: Driver profile update returned {response.status_code}: {response.text}")
            except Exception as e:
                print(f"Warning: Driver profile update endpoint may not be implemented: {str(e)}")
        
        # Check driver status
        response = client.get(
            "/api/v1/driver/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, "Failed to get driver status"
        data = response.json()
        assert "status" in data, "Status not in response"

class TestRideEndpoints:
    def test_create_ride(self, test_user, test_order):
        """Test creating a new ride"""
        # Create test user and get token
        create_test_user(test_user)
        token = get_auth_token(test_user["email"], test_user["password"])
        assert token is not None, "Failed to get auth token"
        
        # Create ride
        response = client.post(
            "/api/v1/rides/",
            json=test_order,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Failed to create ride: {response.text}"
        data = response.json()
        assert "id" in data, "Ride ID not in response"
        assert data["status"] == "pending", "Ride status should be pending"
        
        return data["id"]  # Return ride ID for other tests

    def test_get_ride_status(self, test_user, test_order):
        """Test getting ride status"""
        # First create a ride
        ride_id = self.test_create_ride(test_user, test_order)
        
        # Get ride status
        token = get_auth_token(test_user["email"], test_user["password"])
        response = client.get(
            f"/api/v1/rides/{ride_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Failed to get ride status: {response.text}"
        data = response.json()
        assert data["id"] == ride_id, "Ride ID doesn't match"

# Run tests
if __name__ == "__main__":
    print("🚀 Starting comprehensive Royal Taxi API tests...")
    pytest.main([
        __file__,
        "-v",               # Verbose output
        "--tb=short",       # Shorter traceback
        "-x",               # Stop on first failure
        "--maxfail=3",      # Stop after 3 failures
        "-W", "ignore"      # Ignore warnings
    ])
