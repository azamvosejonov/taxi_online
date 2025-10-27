"""
Test logout API endpoint
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_logout_api():
    print("=" * 60)
    print("🧪 Testing Logout API")
    print("=" * 60)
    
    # Step 1: Register and get token
    print("\n1️⃣ Registering user to get token...")
    timestamp = int(time.time())
    phone_suffix = str(timestamp)[-8:]
    
    register_data = {
        "email": f"logout_test_{timestamp}@example.com",
        "password": "TestPassword123!",
        "full_name": "Logout Test User",
        "phone": f"+9989{phone_suffix}",
        "is_driver": False,
        "language": "uz"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    print(f"   Register Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Registration failed: {response.json()}")
        return
    
    data = response.json()
    token = data.get('access_token')
    print(f"   ✅ Got token: {token[:30]}...")
    
    # Step 2: Test protected endpoint WITH token (should work)
    print("\n2️⃣ Testing protected endpoint WITH token...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v2/customers/", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Token working! Protected endpoint accessible")
    else:
        print(f"   ❌ Token not working: {response.status_code}")
    
    # Step 3: Call logout API
    print("\n3️⃣ Calling logout API...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/logout", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        logout_data = response.json()
        print(f"   ✅ Logout successful!")
        print(f"   Message: {logout_data.get('message')}")
        print(f"   User: {logout_data.get('user', {}).get('email')}")
    else:
        print(f"   ❌ Logout failed: {response.json()}")
    
    # Step 4: Try to use the same token again (should still work until expiration)
    print("\n4️⃣ Testing if token still works after logout...")
    response = requests.get(f"{BASE_URL}/api/v2/customers/", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ℹ️ Token still works (JWT tokens can't be invalidated)")
        print(f"   💡 Client must delete token from storage")
    else:
        print(f"   ❌ Token invalidated: {response.status_code}")
    
    # Step 5: Test logout WITHOUT token (should fail)
    print("\n5️⃣ Testing logout WITHOUT token...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/logout")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 401:
        print(f"   ✅ Correctly returns 401 without token")
    else:
        print(f"   ⚠️ Unexpected status: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Logout API Test Completed!")
    print("=" * 60)
    print("\n📝 Eslatma:")
    print("   - Logout API ishga tushdi ✅")
    print("   - Token server tarafda invalidate qilinmaydi (JWT xususiyati)")
    print("   - Client tokenni o'chirishi kerak (localStorage.removeItem)")
    print("   - Swagger UI da logout tugmasi backend API ni chaqiradi")
    print("=" * 60)

if __name__ == "__main__":
    test_logout_api()
