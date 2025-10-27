"""
Debug script to find 401 issue
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🔍 DEBUGGING 401 ERROR")
print("=" * 70)

# Step 1: Register and get token
print("\n1️⃣ REGISTERING USER...")
timestamp = int(time.time())
phone_suffix = str(timestamp)[-8:]

register_data = {
    "email": f"debug_{timestamp}@example.com",
    "password": "DebugPass123!",
    "full_name": "Debug User",
    "phone": f"+9989{phone_suffix}",
    "is_driver": False,
    "language": "uz"
}

response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
print(f"Status: {response.status_code}")

if response.status_code != 200:
    print(f"❌ Registration failed: {response.json()}")
    exit(1)

data = response.json()
token = data.get('access_token')
print(f"✅ Token received: {token[:50]}...")
print(f"Token length: {len(token)}")
print(f"Token type: {data.get('token_type')}")

# Step 2: Test with different header formats
print("\n2️⃣ TESTING DIFFERENT AUTHORIZATION FORMATS...\n")

test_cases = [
    ("Bearer {token}", f"Bearer {token}"),
    ("bearer {token}", f"bearer {token}"),
    ("Just token", token),
    ("Bearer with space", f"Bearer  {token}"),
]

for name, auth_value in test_cases:
    print(f"Testing: {name}")
    headers = {"Authorization": auth_value}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v2/customers/", headers=headers)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ SUCCESS with this format!")
            print(f"  Correct format: {auth_value[:60]}...")
            break
        elif response.status_code == 401:
            print(f"  ❌ 401 - {response.json()}")
        else:
            print(f"  ⚠️ {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()

# Step 3: Check token parts
print("\n3️⃣ TOKEN STRUCTURE...")
parts = token.split('.')
print(f"Token parts: {len(parts)}")
if len(parts) == 3:
    print(f"✅ Valid JWT structure")
    print(f"Header: {parts[0][:20]}...")
    print(f"Payload: {parts[1][:20]}...")
    print(f"Signature: {parts[2][:20]}...")
else:
    print(f"❌ Invalid JWT structure!")

# Step 4: Try decoding token payload
print("\n4️⃣ TOKEN PAYLOAD...")
try:
    import base64
    # Add padding if needed
    payload = parts[1]
    padding = 4 - len(payload) % 4
    if padding != 4:
        payload += '=' * padding
    
    decoded = base64.b64decode(payload)
    payload_data = json.loads(decoded)
    print(f"Decoded payload:")
    print(json.dumps(payload_data, indent=2))
except Exception as e:
    print(f"❌ Cannot decode: {e}")

# Step 5: Test auth endpoint directly
print("\n5️⃣ TESTING AUTH ENDPOINTS...")

print("\na) Test /api/v1/auth/logout (requires auth):")
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/api/v1/auth/logout", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   ✅ Auth working!")
    print(f"   Response: {response.json()}")
else:
    print(f"   ❌ {response.json() if response.status_code != 200 else 'OK'}")

# Step 6: Check which endpoints work
print("\n6️⃣ TESTING ALL ENDPOINTS...")

endpoints = [
    ("/api/v1/auth/login", "POST", None),  # No auth needed
    ("/api/v1/auth/logout", "POST", headers),  # Auth needed
    ("/api/v2/customers/", "GET", headers),  # Auth needed
    ("/api/v1/users/me", "GET", headers),  # Auth needed (if exists)
]

for endpoint, method, hdrs in endpoints:
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=hdrs)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", headers=hdrs)
        
        status_emoji = "✅" if response.status_code in [200, 404] else "❌"
        print(f"{status_emoji} {method:4} {endpoint:30} -> {response.status_code}")
        
        if response.status_code == 401:
            print(f"     Detail: {response.json().get('detail')}")
    except Exception as e:
        print(f"❌ {method:4} {endpoint:30} -> Error: {e}")

print("\n" + "=" * 70)
print("🔍 DEBUGGING COMPLETED")
print("=" * 70)
print("\n📋 RECOMMENDATION:")
print("   Agar har joy 401 bersa - backend oauth2_scheme muammosi")
print("   Agar ba'zi joylar ishlasa - Swagger UI configuration muammosi")
print("=" * 70)
