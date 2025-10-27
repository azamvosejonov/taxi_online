"""
Test script for the customer and ride management system
"""
import requests
import json
from datetime import datetime

# API base URL (update this based on your setup)
BASE_URL = "http://localhost:8000/api/v2"

# Test authentication credentials
# Using the test user we just created
TEST_USER = {
    "username": "testuser@example.com",  # Email of the test user
    "password": "testpassword123"  # Password for the test user
}

# Test data
TEST_CUSTOMER = {
    "phone": "+998912345678",
    "first_name": "Test",
    "last_name": "User"
}

TEST_RIDE = {
    "customer_phone": "+998912345678",
    "customer_name": "Test User",
    "pickup_location": {
        "lat": 40.7128,
        "lng": 74.0060,
        "address": "Test Pickup Location"
    },
    "dropoff_location": {
        "lat": 40.7128,
        "lng": 74.0060,
        "address": "Test Dropoff Location"
    },
    "vehicle_type": "economy"
}

def print_response(response, title):
    """Print API response in a formatted way"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except:
        print("Response:", response.text)
    print("="*50 + "\n")

def check_server_status():
    """Check if the API server is running and accessible"""
    try:
        health_url = "http://localhost:8000/health"
        print(f"\nChecking server status at: {health_url}")
        response = requests.get(health_url, timeout=5)
        print(f"Server status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Server is running and healthy")
            return True
        else:
            print(f"✗ Server returned status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Could not connect to the server at http://localhost:8000")
        print("Please make sure the server is running. You can start it with:")
        print("uvicorn main:app --reload")
        print(f"\nError details: {str(e)}")
        return False

def get_auth_headers():
    """Get authentication headers"""
    # First, check if server is running
    if not check_server_status():
        return None
        
    login_url = "http://localhost:8000/api/v1/auth/login"
    try:
        print(f"\nAttempting to authenticate with: {login_url}")
        print(f"Using username: {TEST_USER['username']}")
        
        # Try to login with the provided credentials
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        print(f"Sending login request with data: {login_data}")
        response = requests.post(
            login_url,
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text[:500]}")
        
        if response.status_code != 200:
            print("\n=== Authentication Failed ===")
            print(f"Status code: {response.status_code}")
            try:
                print("Response JSON:", response.json())
            except:
                print("Response text:", response.text)
            return None
            
        # Try to get the token from different possible response formats
        response_data = response.json()
        token = response_data.get('access_token') or response_data.get('token')
        
        if not token:
            print("\n=== Token not found in response ===")
            print(response_data)
            return None
        
        print(f"\n✓ Successfully authenticated. Token: {token[:10]}...")
        return {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print(f"\n=== Error during authentication ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")

def test_customer_flow():
    """Test the complete customer and ride flow"""
    print("\n" + "="*60)
    print("  ROYAL TAXI - API TEST SCRIPT")
    print("  " + "="*60)
    
    # Get authentication headers
    print("\n[1/3] Authenticating...")
    headers = get_auth_headers()
    if not headers:
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        print("Please check the error messages above and ensure the server is running correctly.")
        if "500" in str(headers):
            print("\n⚠️  Server returned 500 error. Check the server logs for more details.")
            print("You can run the server in development mode with detailed errors using:")
            print("uvicorn main:app --reload")
        return
        
    # 1. Create a new customer
    print("1. Creating a new customer...")
    response = requests.post(
        f"{BASE_URL}/customers/",
        json=TEST_CUSTOMER,
        headers=headers
    )
    print_response(response, "Create Customer")
    
    if response.status_code != 201:
        print("Failed to create customer")
        return
    
    customer = response.json()
    
    # 2. Get customer by ID
    print("2. Getting customer by ID...")
    response = requests.get(
        f"{BASE_URL}/customers/{customer['id']}",
        headers=headers
    )
    print_response(response, "Get Customer by ID")
    
    # 3. Get customer by phone
    print("3. Getting customer by phone...")
    response = requests.get(
        f"{BASE_URL}/customers/phone/{TEST_CUSTOMER['phone']}",
        headers=headers
    )
    print_response(response, "Get Customer by Phone")
    
    # 4. Update customer
    print("4. Updating customer...")
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    response = requests.put(
        f"{BASE_URL}/customers/{customer['id']}",
        json=update_data,
        headers=headers
    )
    print_response(response, "Update Customer")
    
    # 5. List all customers
    print("5. Listing all customers...")
    response = requests.get(
        f"{BASE_URL}/customers/",
        headers=headers
    )
    print_response(response, "List Customers")
    
    # 6. Create a new ride for the customer
    print("6. Creating a new ride...")
    response = requests.post(
        f"{BASE_URL}/rides/book",
        json=TEST_RIDE,
        headers=headers
    )
    print_response(response, "Create Ride")
    
    if response.status_code != 200:
        print("Failed to create ride")
        return
    
    ride = response.json()
    
    # 7. Get ride details
    print("7. Getting ride details...")
    response = requests.get(
        f"{BASE_URL}/rides/{ride['id']}",
        headers=headers
    )
    print_response(response, "Get Ride Details")
    
    # 8. List all rides
    print("8. Listing all rides...")
    response = requests.get(
        f"{BASE_URL}/rides/",
        headers=headers
    )
    print_response(response, "List Rides")
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    print("Starting customer and ride management system test...\n")
    test_customer_flow()
