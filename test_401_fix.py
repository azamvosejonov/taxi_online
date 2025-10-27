"""
Test to verify 401 error is fixed after login
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_full_flow():
    print("=" * 60)
    print("🧪 Testing 401 Error Fix")
    print("=" * 60)
    
    # Step 1: Try protected endpoint without token (should get 401)
    print("\n1️⃣ Testing protected endpoint WITHOUT token...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/me")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly returns 401 without token")
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 2: Login to get token
    print("\n2️⃣ Logging in to get token...")
    timestamp = int(time.time())
    
    # First register a new user
    phone_suffix = str(timestamp)[-8:]  # Last 8 digits
    register_data = {
        "email": f"test_{timestamp}@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "phone": f"+9989{phone_suffix}",  # +998 + 9 digits
        "is_driver": False,
        "language": "uz"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    print(f"   Register Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"   ✅ Got token: {token[:30]}...")
        
        # Step 3: Try protected endpoint WITH token
        print("\n3️⃣ Testing protected endpoint WITH token...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try different endpoints
        endpoints_to_test = [
            "/api/v1/users/me",
            "/api/v2/customers/",
            "/api/v1/rides/"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                print(f"   {endpoint}")
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 401:
                    print(f"      ❌ STILL GETTING 401! Token not working!")
                    print(f"      Response: {response.json()}")
                elif response.status_code == 404:
                    print(f"      ℹ️ 404 - Endpoint not found (expected for some)")
                elif response.status_code == 200:
                    print(f"      ✅ SUCCESS! No 401 error!")
                else:
                    print(f"      ℹ️ Status {response.status_code}")
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        # Step 4: Test that token format is correct
        print("\n4️⃣ Verifying token format...")
        print(f"   Token starts with: {token[:20]}")
        print(f"   Token type: JWT (should have 3 parts separated by .)")
        parts = token.split('.')
        print(f"   Token parts: {len(parts)}")
        if len(parts) == 3:
            print(f"   ✅ Token format is correct")
        else:
            print(f"   ❌ Token format is WRONG!")
            
    else:
        print(f"   ❌ Registration failed: {response.json()}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_full_flow()
