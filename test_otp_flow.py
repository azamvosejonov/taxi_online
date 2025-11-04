"""
Test script for OTP authentication flow
"""
import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def test_otp_flow():
    """Test the complete OTP authentication flow"""
    
    # Test data - use a new phone number
    import random
    phone = f"+99890{random.randint(1000000, 9999999)}"
    
    print("=" * 60)
    print("Testing OTP Authentication Flow")
    print("=" * 60)
    
    # Step 1: Send OTP
    print("\n1️⃣  Step 1: Sending OTP to phone number...")
    response = requests.post(
        f"{BASE_URL}/auth/send-otp",
        json={"phone": phone}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code != 200:
        print("❌ Failed to send OTP")
        return
    
    # Get OTP code from response (in production, this would be sent via SMS)
    otp_code = response.json().get("otp_code")
    print(f"\n✅ OTP sent successfully! Code: {otp_code}")
    
    # Step 2: Verify OTP
    print("\n2️⃣  Step 2: Verifying OTP code...")
    response = requests.post(
        f"{BASE_URL}/auth/verify-otp",
        json={
            "phone": phone,
            "otp_code": otp_code
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code != 200:
        print("❌ Failed to verify OTP")
        return
    
    verify_result = response.json()
    print(f"\n✅ OTP verified successfully!")
    print(f"Needs profile completion: {verify_result.get('needs_profile_completion')}")
    
    # Step 3: Complete profile (if needed)
    if verify_result.get('needs_profile_completion'):
        print("\n3️⃣  Step 3: Completing user profile...")
        response = requests.post(
            f"{BASE_URL}/auth/complete-profile",
            json={
                "phone": phone,
                "first_name": "Test",
                "last_name": "User",
                "gender": "Erkak",
                "date_of_birth": "1990-01-01",
                "vehicle_make": "Chevrolet",
                "vehicle_color": "Qora",
                "position": "Haydovchi",
                "license_plate": "01T999ST",
                "tech_passport": "TEST123456"
            }
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code != 201:
            print("❌ Failed to complete profile")
            return
        
        result = response.json()
        print(f"\n✅ Profile completed successfully!")
        print(f"Access Token: {result.get('access_token')[:50]}...")
        print(f"User ID: {result.get('user', {}).get('id')}")
        print(f"Full Name: {result.get('user', {}).get('full_name')}")
    else:
        print("\n✅ User already exists, no profile completion needed")
    
    print("\n" + "=" * 60)
    print("✅ OTP Flow Test Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_otp_flow()
