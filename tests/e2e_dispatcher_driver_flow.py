import random
import string
import os
import sys
from fastapi.testclient import TestClient

# Ensure repo root is in sys.path so `from main import app` works when running this file directly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from main import app


def gen_phone():
    # +998 followed by 9 digits; ensure starts with +9989...
    tail = ''.join(random.choices('0123456789', k=8))
    return "+9989" + tail


def register_or_login(client: TestClient, email: str, phone: str, password: str, full_name: str, is_admin=False, is_driver=False):
    reg_payload = {
        "email": email,
        "phone": phone,
        "full_name": full_name,
        "password": password,
        "is_driver": is_driver,
        "is_admin": is_admin,
        "language": "uz"
    }
    r = client.post("/api/v1/auth/register", json=reg_payload)
    if r.status_code == 200:
        data = r.json()
        return data["access_token"], data["user"]["id"]
    # if already exists, login
    login_payload = {"username": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_payload)
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    data = r.json()
    return data["access_token"], data["user"]["id"]


def test_e2e_flow():
    client = TestClient(app)

    # Prepare identities
    admin_email = "admin_" + ''.join(random.choices(string.ascii_lowercase, k=6)) + "@example.com"
    admin_phone = gen_phone()
    driver_email = "driver_" + ''.join(random.choices(string.ascii_lowercase, k=6)) + "@example.com"
    driver_phone = gen_phone()
    password = "Passw0rd!"

    # 1) Admin register/login
    admin_token, admin_id = register_or_login(client, admin_email, admin_phone, password, "Admin User", is_admin=True)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2) Driver register/login
    driver_token, driver_id = register_or_login(client, driver_email, driver_phone, password, "Driver User", is_driver=True)
    driver_headers = {"Authorization": f"Bearer {driver_token}"}

    # 3) Approve driver (admin)
    r = client.put(f"/api/v1/admin/users/{driver_id}/approve", headers=admin_headers)
    assert r.status_code == 200, r.text

    # 4) Admin deposit 20000 UZS to driver
    r = client.post("/api/v1/dispatcher/deposit", json={"driver_id": driver_id, "amount": 20000}, headers=admin_headers)
    assert r.status_code == 200, r.text

    # 5) Driver on-duty + set location near pickup
    r = client.post("/api/v1/driver/status", json={
        "is_on_duty": True,
        "lat": 41.3111,
        "lng": 69.2797,
        "city": "Tashkent"
    }, headers=driver_headers)
    assert r.status_code == 200, r.text

    # 6) Dispatcher (admin acts as dispatcher) creates order
    order_body = {
        "order": {
            "customer_phone": gen_phone(),
            "customer_name": "Customer A",
            "pickup_location": {"lat": 41.3111, "lng": 69.2797, "address": "Chorsu", "city": "Tashkent"},
            "dropoff_location": {"lat": 41.3275, "lng": 69.2813, "address": "Amir Temur", "city": "Tashkent"},
            "vehicle_type": "economy"
        }
    }
    r = client.post("/api/v1/dispatcher/order", json=order_body, headers=admin_headers)
    assert r.status_code == 200, r.text
    data = r.json()
    ride_id = data["ride"]["id"]

    # 7) Driver accepts ride
    r = client.post(f"/api/v1/driver/rides/{ride_id}/accept", headers=driver_headers)
    assert r.status_code == 200, r.text

    # 8) Driver starts ride
    r = client.post(f"/api/v1/driver/rides/{ride_id}/start", headers=driver_headers)
    assert r.status_code == 200, r.text

    # 9) Driver completes ride with final fare 50000
    r = client.post(f"/api/v1/driver/rides/{ride_id}/complete", json={"final_fare": 50000}, headers=driver_headers)
    assert r.status_code == 200, r.text
    complete_data = r.json()
    assert complete_data["commission_rate"] == 0.10
    assert complete_data["commission"] == 5000.0

    # 10) Verify remaining deposit ~= 15000
    remaining = float(complete_data["remaining_deposit"])
    assert 14999 <= remaining <= 15001, f"Unexpected remaining deposit: {remaining}"

    # 11) Driver stats
    r = client.get("/api/v1/driver/stats", headers=driver_headers)
    assert r.status_code == 200, r.text

    print("E2E dispatcher-driver flow PASSED.")


if __name__ == "__main__":
    test_e2e_flow()
    print("OK")
