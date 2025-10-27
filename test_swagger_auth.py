"""
Test script to verify automatic Swagger token authorization
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_register_with_token():
    """Test registration and verify token is returned"""
    print("\n🧪 Testing Registration...")
    
    # Create a test user
    timestamp = int(time.time())
    test_user = {
        "email": f"test_swagger_{timestamp}@example.com",
        "password": "TestPassword123!",
        "full_name": "Test Swagger User",
        "phone": f"+99890123{timestamp % 10000}",
        "is_driver": False,
        "language": "uz"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=test_user)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data, "❌ No access_token in response!"
        assert "token_type" in data, "❌ No token_type in response!"
        assert data["token_type"] == "bearer", "❌ Wrong token_type!"
        print(f"✅ Registration successful! Token: {data['access_token'][:30]}...")
        return data["access_token"]
    else:
        print(f"❌ Registration failed: {response.json()}")
        return None

def test_login_with_token():
    """Test login and verify token is returned"""
    print("\n🧪 Testing Login...")
    
    # Use a known user or create one first
    login_data = {
        "username": "test@example.com",  # Update with a valid user
        "password": "Test123!"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert "access_token" in data, "❌ No access_token in response!"
        assert "token_type" in data, "❌ No token_type in response!"
        assert data["token_type"] == "bearer", "❌ Wrong token_type!"
        print(f"✅ Login successful! Token: {data['access_token'][:30]}...")
        return data["access_token"]
    else:
        print(f"ℹ️ Login failed (expected if user doesn't exist): {response.json()}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint with the token"""
    print("\n🧪 Testing Protected Endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Successfully accessed protected endpoint!")
        print(f"User Data: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Failed to access protected endpoint: {response.json()}")

def test_swagger_ui_available():
    """Test that custom Swagger UI is available"""
    print("\n🧪 Testing Custom Swagger UI...")
    
    response = requests.get(f"{BASE_URL}/docs")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        html_content = response.text
        if "responseInterceptor" in html_content and "localStorage.setItem('swagger_auth_token'" in html_content:
            print(f"✅ Custom Swagger UI is working with auto-token handling!")
        else:
            print(f"⚠️ Swagger UI loaded but custom token handling might not be present")
    else:
        print(f"❌ Failed to load Swagger UI")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Royal Taxi API - Swagger Auto-Authorization Test")
    print("=" * 60)
    
    # Test Swagger UI availability
    test_swagger_ui_available()
    
    # Test registration
    token = test_register_with_token()
    
    # Test protected endpoint with the new token
    if token:
        test_protected_endpoint(token)
    
    # Test login
    login_token = test_login_with_token()
    if login_token:
        test_protected_endpoint(login_token)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\n📝 Instructions for manual testing:")
    print("1. Open http://localhost:8000/docs in your browser")
    print("2. Try the /api/v1/auth/register or /api/v1/auth/login endpoint")
    print("3. After successful login/registration, the token will be")
    print("   automatically applied to the Swagger UI authorization")
    print("4. You'll see a green banner confirming auto-authorization")
    print("5. Now you can test any protected endpoint without 401 errors!")
    print("=" * 60)
