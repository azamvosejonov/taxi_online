import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set test environment variable for database override
os.environ["TESTING"] = "true"

# Import only models and config, not the full main app to avoid FastAPI initialization issues
from models import Base
from config import SECRET_KEY, ALGORITHM

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_royaltaxi.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

# Test configuration
@pytest.fixture
def db():
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client():
    """Create test client by importing and initializing the app."""
    # Import here to avoid issues during conftest loading
    from main import app
    return TestClient(app)

@pytest.fixture
def test_user(db):
    """Create a test user."""
    from models import User
    from utils.helpers import get_password_hash

    user = User(
        email="test@example.com",
        phone="+998901234567",
        password="hashed_password_placeholder",  # Skip actual hashing in tests
        full_name="Test User",
        is_driver=False,
        is_admin=False,
        language="uz"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_driver(db):
    """Create a test driver."""
    from models import User
    from utils.helpers import get_password_hash

    driver = User(
        email="driver@example.com",
        phone="+998901234568",
        password="hashed_password_placeholder",  # Skip actual hashing in tests
        full_name="Test Driver",
        is_driver=True,
        is_admin=False,
        is_approved=True,
        current_balance=5000.0,
        language="uz"
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver

@pytest.fixture
def test_admin(db):
    """Create a test admin."""
    from models import User
    from utils.helpers import get_password_hash

    admin = User(
        email="admin@example.com",
        phone="+998901234569",
        password="hashed_password_placeholder",  # Skip actual hashing in tests
        full_name="Test Admin",
        is_driver=False,
        is_admin=True,
        language="uz"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for a test user."""
    from utils.helpers import create_access_token

    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def driver_auth_headers(test_driver):
    """Get authentication headers for a test driver."""
    from utils.helpers import create_access_token

    token = create_access_token(data={"sub": test_driver.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers(test_admin):
    """Get authentication headers for a test admin."""
    from utils.helpers import create_access_token

    token = create_access_token(data={"sub": test_admin.email})
    return {"Authorization": f"Bearer {token}"}
