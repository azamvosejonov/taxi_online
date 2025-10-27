"""
Royal Taxi API - Kompleks Test Suite
Barcha API endpointlarini test qilish uchun
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Main application import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models va auth
try:
    from models import User
    from auth import get_password_hash
    from main import app
    from database import Base, get_db
except ImportError as e:
    print(f"Import xatoligi: {e}")
    print("Kerakli fayllar mavjudligini tekshiring...")
    sys.exit(1)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_royaltaxi.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Test data
TEST_USER = {
    "email": "test@example.com",
    "phone": "+998901234567",
    "full_name": "Test User",
    "password": "test1234",
    "is_driver": True,
    "is_admin": False,
    "is_dispatcher": False
}

TEST_ADMIN = {
    "email": "admin@test.com",
    "phone": "+998901234568",
    "full_name": "Admin User",
    "password": "admin1234",
    "is_driver": False,
    "is_admin": True,
    "is_dispatcher": False
}

TEST_DISPATCHER = {
    "email": "dispatcher@test.com",
    "phone": "+998901234569",
    "full_name": "Dispatcher User",
    "password": "dispatcher1234",
    "is_driver": False,
    "is_admin": False,
    "is_dispatcher": True
}

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def access_token_user(db_session):
    # User yaratish
    user = User(
        email=TEST_USER["email"],
        phone=TEST_USER["phone"],
        full_name=TEST_USER["full_name"],
        hashed_password=get_password_hash(TEST_USER["password"]),
        is_driver=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Login qilish
    login_response = client.post("/api/v1/auth/login", data={
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    return login_response.json()["access_token"]

@pytest.fixture
def access_token_admin(db_session):
    # Admin yaratish
    admin = User(
        email=TEST_ADMIN["email"],
        phone=TEST_ADMIN["phone"],
        full_name=TEST_ADMIN["full_name"],
        hashed_password=get_password_hash(TEST_ADMIN["password"]),
        is_admin=True,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()

    login_response = client.post("/api/v1/auth/login", data={
        "username": TEST_ADMIN["email"],
        "password": TEST_ADMIN["password"]
    })
    return login_response.json()["access_token"]

@pytest.fixture
def access_token_dispatcher(db_session):
    # Dispatcher yaratish
    dispatcher = User(
        email=TEST_DISPATCHER["email"],
        phone=TEST_DISPATCHER["phone"],
        full_name=TEST_DISPATCHER["full_name"],
        hashed_password=get_password_hash(TEST_DISPATCHER["password"]),
        is_dispatcher=True,
        is_active=True
    )
    db_session.add(dispatcher)
    db_session.commit()

    login_response = client.post("/api/v1/auth/login", data={
        "username": TEST_DISPATCHER["email"],
        "password": TEST_DISPATCHER["password"]
    })
    return login_response.json()["access_token"]

class TestAuthentication:
    """Authentication endpointlarini test qilish"""

    def test_register_user(self, db_session):
        """Foydalanuvchi ro'yxatdan o'tish"""
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "phone": "+998901234570",
            "full_name": "New User",
            "password": "newpass1234",
            "is_driver": False
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_user(self, access_token_user):
        """Foydalanuvchi tizimga kirish"""
        response = client.post("/api/v1/auth/login", data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_logout_user(self, access_token_user):
        """Foydalanuvchi tizimdan chiqish"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.post("/api/v1/auth/logout", headers=headers)
        assert response.status_code == 200

class TestUserEndpoints:
    """Foydalanuvchi endpointlarini test qilish"""

    def test_get_profile(self, access_token_user):
        """Profil olish"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.get("/api/v1/users/profile", headers=headers)
        assert response.status_code == 200
        assert "email" in response.json()

    def test_update_profile(self, access_token_user):
        """Profil yangilash"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.put("/api/v1/users/profile", headers=headers, json={
            "full_name": "Updated Name",
            "language": "uz"
        })
        assert response.status_code == 200

    def test_get_balance(self, access_token_user):
        """Balans olish"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.get("/api/v1/users/balance", headers=headers)
        assert response.status_code == 200
        assert "balance" in response.json()

    def test_get_user_rides(self, access_token_user):
        """Foydalanuvchi sayohatlarini olish"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.get("/api/v1/users/rides", headers=headers)
        assert response.status_code == 200

    def test_get_user_transactions(self, access_token_user):
        """Foydalanuvchi tranzaksiyalarini olish"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.get("/api/v1/users/transactions", headers=headers)
        assert response.status_code == 200

class TestAdminEndpoints:
    """Admin endpointlarini test qilish"""

    def test_get_all_users(self, access_token_admin):
        """Barcha foydalanuvchilarni olish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 200

    def test_get_system_stats(self, access_token_admin):
        """Tizim statistikasini olish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.get("/api/v1/admin/stats", headers=headers)
        assert response.status_code == 200

    def test_get_daily_analytics(self, access_token_admin):
        """Kunlik analitikani olish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.get("/api/v1/admin/analytics/daily", headers=headers)
        assert response.status_code == 200

    def test_get_weekly_analytics(self, access_token_admin):
        """Haftalik analitikani olish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.get("/api/v1/admin/analytics/weekly", headers=headers)
        assert response.status_code == 200

    def test_deactivate_user(self, access_token_admin):
        """Foydalanuvchini bloklash"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.put("/api/v1/admin/users/1/deactivate", headers=headers)
        assert response.status_code == 200

    def test_approve_user(self, access_token_admin):
        """Foydalanuvchini tasdiqlash"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.put("/api/v1/admin/users/1/approve", headers=headers)
        assert response.status_code == 200

    def test_activate_user(self, access_token_admin):
        """Foydalanuvchini aktivlashtirish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.put("/api/v1/admin/users/1/activate", headers=headers)
        assert response.status_code == 200

    def test_get_income_stats(self, access_token_admin):
        """Daromad statistikasini olish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.get("/api/v1/admin/income/stats", headers=headers)
        assert response.status_code == 200

    def test_get_monthly_income(self, access_token_admin):
        """Oylik daromadni olish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.get("/api/v1/admin/income/monthly/2024/1", headers=headers)
        assert response.status_code == 200

    def test_get_commission_rate(self, access_token_admin):
        """Komissiya stavkasini olish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.get("/api/v1/admin/config/commission-rate", headers=headers)
        assert response.status_code == 200

    def test_set_commission_rate(self, access_token_admin):
        """Komissiya stavkasini o'rnatish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.put("/api/v1/admin/config/commission-rate", headers=headers, json={
            "rate": 15.0
        })
        assert response.status_code == 200

    def test_notify_all_drivers(self, access_token_admin):
        """Barcha haydovchilarga xabar yuborish"""
        headers = {"Authorization": f"Bearer {access_token_admin}"}
        response = client.post("/api/v1/admin/notify/all", headers=headers, json={
            "title": "Test Notification",
            "body": "This is a test notification"
        })
        assert response.status_code == 200

class TestDispatcherEndpoints:
    """Dispatcher endpointlarini test qilish"""

    def test_create_order(self, access_token_dispatcher):
        """Buyurtma yaratish"""
        headers = {"Authorization": f"Bearer {access_token_dispatcher}"}
        response = client.post("/api/v1/dispatcher/order", headers=headers, json={
            "customer_phone": "+998901234572",
            "customer_name": "Test Customer",
            "pickup_location": {
                "lat": 41.3111,
                "lng": 69.2797,
                "address": "Test pickup location"
            },
            "dropoff_location": {
                "lat": 41.3112,
                "lng": 69.2798,
                "address": "Test dropoff location"
            },
            "vehicle_type": "economy"
        })
        assert response.status_code == 200

    def test_broadcast_order(self, access_token_dispatcher):
        """Buyurtmani broadcast qilish"""
        headers = {"Authorization": f"Bearer {access_token_dispatcher}"}
        response = client.post("/api/v1/dispatcher/order/1/broadcast", headers=headers)
        assert response.status_code == 200

    def test_add_deposit(self, access_token_dispatcher):
        """Depozit qo'shish"""
        headers = {"Authorization": f"Bearer {access_token_dispatcher}"}
        response = client.post("/api/v1/dispatcher/deposit", headers=headers, json={
            "driver_id": 1,
            "amount": 100.0
        })
        assert response.status_code == 200

    def test_block_driver(self, access_token_dispatcher):
        """Haydovchini bloklash"""
        headers = {"Authorization": f"Bearer {access_token_dispatcher}"}
        response = client.post("/api/v1/dispatcher/block/1", headers=headers)
        assert response.status_code == 200

    def test_unblock_driver(self, access_token_dispatcher):
        """Haydovchini blokdan chiqarish"""
        headers = {"Authorization": f"Bearer {access_token_dispatcher}"}
        response = client.post("/api/v1/dispatcher/unblock/1", headers=headers)
        assert response.status_code == 200

    def test_get_driver_locations(self, access_token_dispatcher):
        """Haydovchi joylashuvlarini olish"""
        headers = {"Authorization": f"Bearer {access_token_dispatcher}"}
        response = client.get("/api/v1/dispatcher/drivers/locations", headers=headers)
        assert response.status_code == 200

class TestDriverEndpoints:
    """Haydovchi endpointlarini test qilish"""

    def test_update_driver_status(self, access_token_user):
        """Haydovchi holatini yangilash"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.post("/api/v1/driver/status", headers=headers, json={
            "is_on_duty": True,
            "lat": 41.3111,
            "lng": 69.2797,
            "city": "Toshkent"
        })
        assert response.status_code == 200

    def test_accept_ride(self, access_token_user):
        """Sayohatni qabul qilish"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.post("/api/v1/driver/rides/1/accept", headers=headers)
        assert response.status_code == 200

    def test_start_ride(self, access_token_user):
        """Sayohatni boshlash"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.post("/api/v1/driver/rides/1/start", headers=headers)
        assert response.status_code == 200

    def test_complete_ride(self, access_token_user):
        """Sayohatni yakunlash"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.post("/api/v1/driver/rides/1/complete", headers=headers, json={
            "final_fare": 50.0
        })
        assert response.status_code == 200

    def test_get_driver_stats(self, access_token_user):
        """Haydovchi statistikasini olish"""
        headers = {"Authorization": f"Bearer {access_token_user}"}
        response = client.get("/api/v1/driver/stats", headers=headers)
        assert response.status_code == 200

# Testlarni ishga tushirish
if __name__ == "__main__":
    print("🚀 Royal Taxi API testlarini ishga tushirish...")
    pytest.main([__file__, "-v", "--tb=short"])
