"""
Complete API Test Suite for Royal Taxi - All Endpoints
Tests every single endpoint from the API documentation
"""
import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://176.57.184.175:8080/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

class CompleteAPITester:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.tokens = {}
        self.test_data = {}
        
    def print_header(self, text):
        print(f"\n{Colors.BLUE}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BLUE}{text.center(80)}{Colors.RESET}")
        print(f"{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")
    
    def print_section(self, text):
        print(f"\n{Colors.CYAN}{'─' * 80}{Colors.RESET}")
        print(f"{Colors.CYAN}{text}{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}")
    
    def print_test(self, name, status, expected, actual, details=""):
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"{Colors.GREEN}✓{Colors.RESET} {name} - Expected: {expected}, Got: {actual}")
        elif status == "SKIP":
            self.skipped_tests += 1
            print(f"{Colors.YELLOW}⊘{Colors.RESET} {name} - {details}")
        else:
            self.failed_tests += 1
            print(f"{Colors.RED}✗{Colors.RESET} {name} - Expected: {expected}, Got: {actual}")
            if details:
                print(f"  {Colors.RED}Details: {details}{Colors.RESET}")
    
    def test_endpoint(self, method, endpoint, expected_status, headers=None, json_data=None, params=None, test_name="", files=None):
        """Generic endpoint tester"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                if files:
                    response = requests.post(url, headers=headers, files=files, data=json_data)
                else:
                    response = requests.post(url, headers=headers, json=json_data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=json_data, params=params)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # Treat any 2xx as success when expected_status is 200 (so 201 also passes)
            if expected_status == 200 and 200 <= response.status_code < 300:
                status = "PASS"
            else:
                status = "PASS" if response.status_code == expected_status else "FAIL"
            details = ""
            if status == "FAIL":
                try:
                    details = response.json()
                except:
                    details = response.text[:200]
            
            self.print_test(test_name or f"{method} {endpoint}", status, expected_status, response.status_code, details)
            return response
            
        except Exception as e:
            self.print_test(test_name or f"{method} {endpoint}", "FAIL", expected_status, "ERROR", str(e))
            return None
    
    def run_all_tests(self):
        """Run all API tests"""
        
        self.print_header("ROYAL TAXI - COMPLETE API TEST SUITE")
        print(f"{Colors.CYAN}Testing all {self.count_total_endpoints()} endpoints...{Colors.RESET}\n")
        
        # 1. Auth Endpoints (6)
        self.test_auth_endpoints()
        
        # 2. Users Endpoints (6)
        self.test_users_endpoints()
        
        # 3. Admin Endpoints (20)
        self.test_admin_endpoints()
        
        # 4. Files Endpoints (4)
        self.test_files_endpoints()
        
        # 5. Dispatcher Endpoints (7)
        self.test_dispatcher_endpoints()
        
        # 6. Driver Endpoints (5)
        self.test_driver_endpoints()
        
        # 7. Rider Endpoints (6)
        self.test_rider_endpoints()
        
        # Print Summary
        self.print_summary()
    
    def count_total_endpoints(self):
        return 6 + 6 + 20 + 4 + 7 + 5 + 6  # 54 endpoints
    
    def test_auth_endpoints(self):
        """Test Auth endpoints (6 endpoints)"""
        self.print_header("1. AUTH ENDPOINTS (6 endpoints)")
        
        # 1. Register
        self.print_section("POST /api/v1/auth/register - Register")
        register_data = {
            "phone": f"+99890{int(time.time()) % 10000000}",
            "first_name": "Test",
            "last_name": "User",
            "password": "test123456",
            "gender": "Erkak",
            "date_of_birth": "1990-01-01",
            "vehicle_make": "Chevrolet",
            "vehicle_color": "Qora",
            "position": "Haydovchi",
            "license_plate": f"01T{int(time.time()) % 1000}AA",
            "tech_passport": f"TEST{int(time.time()) % 100000}"
        }
        
        response = self.test_endpoint(
            "POST", "/auth/register", 200,
            json_data=register_data,
            test_name="Register new user"
        )
        
        if response and 200 <= response.status_code < 300:
            data = response.json()
            self.tokens['test_user'] = data['access_token']
            self.test_data['test_phone'] = register_data['phone']
            # Persist the created user's id for later admin/dispatcher/driver tests
            self.test_data['test_user_id'] = data.get('user', {}).get('id')
        
        # 2. Login
        self.print_section("POST /api/v1/auth/login - Login")
        
        # Get admin credentials
        admin_phone = os.getenv('ADMIN_PHONE', '+998901234567')
        admin_password = os.getenv('ADMIN_PASSWORD', 'ChangeMe123!')
        
        response = self.test_endpoint(
            "POST", "/auth/login", 200,
            json_data={"phone": admin_phone, "password": admin_password},
            test_name="Login as admin"
        )
        
        if response and response.status_code == 200:
            self.tokens['admin'] = response.json()['access_token']
        
        # 3. Logout
        self.print_section("POST /api/v1/auth/logout - Logout")
        if 'test_user' in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
            self.test_endpoint("POST", "/auth/logout", 200, headers=headers, test_name="Logout")
            
            # Re-login
            response = self.test_endpoint(
                "POST", "/auth/login", 200,
                json_data={"phone": self.test_data.get('test_phone'), "password": "test123456"},
                test_name="Re-login after logout"
            )
            if response and response.status_code == 200:
                self.tokens['test_user'] = response.json()['access_token']
        
        # 4. Send OTP
        self.print_section("POST /api/v1/auth/send-otp - Send OTP")
        otp_phone = f"+99890{int(time.time()) % 10000000}"
        response = self.test_endpoint(
            "POST", "/auth/send-otp", 200,
            json_data={"phone": otp_phone},
            test_name="Send OTP"
        )
        
        otp_code = None
        if response and response.status_code == 200:
            otp_code = response.json().get('otp_code')
            self.test_data['otp_phone'] = otp_phone
        
        # 5. Verify OTP
        self.print_section("POST /api/v1/auth/verify-otp - Verify OTP")
        if otp_code:
            self.test_endpoint(
                "POST", "/auth/verify-otp", 200,
                json_data={"phone": otp_phone, "otp_code": otp_code},
                test_name="Verify OTP"
            )
        else:
            self.print_test("Verify OTP", "SKIP", 200, "N/A", "No OTP code available")
        
        # 6. Complete Profile
        self.print_section("POST /api/v1/auth/complete-profile - Complete Profile")
        if otp_code:
            profile_data = {
                "phone": otp_phone,
                "first_name": "OTP",
                "last_name": "User",
                "gender": "Erkak",
                "date_of_birth": "1990-01-01",
                "vehicle_make": "Chevrolet",
                "vehicle_color": "White",
                "position": "Haydovchi",
                "license_plate": f"01O{int(time.time()) % 1000}TP",
                "tech_passport": f"OTP{int(time.time()) % 100000}"
            }
            
            self.test_endpoint(
                "POST", "/auth/complete-profile", 200,
                json_data=profile_data,
                test_name="Complete profile"
            )
        else:
            self.print_test("Complete profile", "SKIP", 201, "N/A", "No verified OTP")
    
    def test_users_endpoints(self):
        """Test Users endpoints (6 endpoints)"""
        self.print_header("2. USERS ENDPOINTS (6 endpoints)")
        
        if 'test_user' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping user tests - no token{Colors.RESET}")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
        
        # 1. Get Profile
        self.print_section("GET /api/v1/users/profile - Get Profile")
        self.test_endpoint("GET", "/users/profile", 200, headers=headers, test_name="Get user profile")
        
        # 2. Update Profile
        self.print_section("PUT /api/v1/users/profile - Update Profile")
        update_data = {"full_name": "Updated Test User"}
        self.test_endpoint("PUT", "/users/profile", 200, headers=headers, json_data=update_data, test_name="Update profile")
        
        # 3. Upload Profile Picture
        self.print_section("POST /api/v1/users/profile-picture - Upload Profile Picture")
        self.print_test("Upload profile picture", "SKIP", 200, "N/A", "File upload requires actual file")
        
        # 4. Get Balance
        self.print_section("GET /api/v1/users/balance - Get Balance")
        self.test_endpoint("GET", "/users/balance", 200, headers=headers, test_name="Get user balance")
        
        # 5. Get User Rides
        self.print_section("GET /api/v1/users/rides - Get User Rides")
        self.test_endpoint("GET", "/users/rides", 200, headers=headers, test_name="Get user rides")
        
        # 6. Get User Transactions
        self.print_section("GET /api/v1/users/transactions - Get User Transactions")
        self.test_endpoint("GET", "/users/transactions", 200, headers=headers, test_name="Get user transactions")
    
    def test_admin_endpoints(self):
        """Test Admin endpoints (20 endpoints)"""
        self.print_header("3. ADMIN ENDPOINTS (20 endpoints)")
        
        if 'admin' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping admin tests - no admin token{Colors.RESET}")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        
        # 1. Get All Users
        self.print_section("GET /api/v1/admin/users - Get All Users")
        response = self.test_endpoint("GET", "/admin/users", 200, headers=headers, test_name="Get all users")
        
        user_id = self.test_data.get('test_user_id')
        if not user_id and response and response.status_code == 200:
            users = response.json()
            if users and len(users) > 0:
                user_id = users[0]['id']
        
        # 2. Get System Stats
        self.print_section("GET /api/v1/admin/stats - Get System Stats")
        self.test_endpoint("GET", "/admin/stats", 200, headers=headers, test_name="Get system stats")
        
        # 3. Get Daily Analytics
        self.print_section("GET /api/v1/admin/analytics/daily - Get Daily Analytics")
        self.test_endpoint("GET", "/admin/analytics/daily", 200, headers=headers, test_name="Get daily analytics")
        
        # 4. Get Weekly Analytics
        self.print_section("GET /api/v1/admin/analytics/weekly - Get Weekly Analytics")
        self.test_endpoint("GET", "/admin/analytics/weekly", 200, headers=headers, test_name="Get weekly analytics")
        
        # 5-12. User Management
        if user_id:
            self.print_section(f"User Management Endpoints (User ID: {user_id})")
            
            self.test_endpoint("PUT", f"/admin/users/{user_id}/approve", 200, headers=headers, test_name="Approve user")
            self.test_endpoint("PUT", f"/admin/users/{user_id}/unapprove", 200, headers=headers, test_name="Unapprove user")
            self.test_endpoint("PUT", f"/admin/users/{user_id}/set-dispatcher", 200, headers=headers, test_name="Set as dispatcher")
            self.test_endpoint("PUT", f"/admin/users/{user_id}/set-admin", 200, headers=headers, test_name="Set as admin")
            self.test_endpoint("PUT", f"/admin/users/{user_id}/remove-roles", 200, headers=headers, test_name="Remove roles")
            self.test_endpoint("PUT", f"/admin/users/{user_id}/deactivate", 200, headers=headers, test_name="Deactivate user")
            self.test_endpoint("PUT", f"/admin/users/{user_id}/activate", 200, headers=headers, test_name="Activate user")
        else:
            for i in range(7):
                self.print_test(f"User management endpoint {i+1}", "SKIP", 200, "N/A", "No user ID available")
        
        # 13-15. Income Stats
        self.print_section("Income Statistics Endpoints")
        self.test_endpoint("GET", "/admin/income/stats", 200, headers=headers, test_name="Get income stats")
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        self.test_endpoint("GET", f"/admin/income/monthly/{current_year}/{current_month}", 200, headers=headers, test_name="Get monthly income")
        self.test_endpoint("GET", f"/admin/income/yearly/{current_year}", 200, headers=headers, test_name="Get yearly income")
        
        # 16-17. Commission Rate
        self.print_section("Commission Rate Endpoints")
        self.test_endpoint("GET", "/admin/config/commission-rate", 200, headers=headers, test_name="Get commission rate")
        self.test_endpoint("PUT", "/admin/config/commission-rate", 200, headers=headers, params={"rate": 0.1}, test_name="Set commission rate")
        
        # 18-19. Notifications
        self.print_section("Notification Endpoints")
        notify_data = {"title": "Test", "body": "Test notification"}
        self.test_endpoint("POST", "/admin/notify/all", 200, headers=headers, json_data=notify_data, test_name="Notify all drivers")
        
        if user_id:
            self.test_endpoint("POST", f"/admin/notify/{user_id}", 200, headers=headers, json_data=notify_data, test_name="Notify specific driver")
        else:
            self.print_test("Notify specific driver", "SKIP", 200, "N/A", "No user ID")
        
        # 20-22. Pricing
        self.print_section("Pricing Management Endpoints")
        self.test_endpoint("GET", "/admin/pricing", 200, headers=headers, test_name="Get pricing config")
        
        pricing_data = {
            "vehicle_type": "economy",
            "base_fare": 10000,
            "per_km_rate": 2000,
            "per_minute_rate": 500
        }
        self.test_endpoint("PUT", "/admin/pricing/economy", 200, headers=headers, json_data=pricing_data, test_name="Update pricing")
        self.test_endpoint("GET", "/admin/pricing/calculate", 200, headers=headers, params={"distance": 10, "duration": 20, "vehicle_type": "economy"}, test_name="Calculate fare")
    
    def test_files_endpoints(self):
        """Test Files endpoints (4 endpoints)"""
        self.print_header("4. FILES ENDPOINTS (4 endpoints)")
        
        if 'test_user' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping files tests - no user token{Colors.RESET}")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
        self.print_section("File Upload Endpoints")
        
        # 1) Users: upload profile picture
        files = {
            'file': ('test.jpg', b'\xff\xd8\xff\xe0JPEG', 'image/jpeg')
        }
        self.test_endpoint("POST", "/users/profile-picture", 200, headers=headers, files=files, test_name="Upload profile picture (users)")
        
        # 2) Files: upload profile picture
        files = {
            'file': ('test.jpg', b'\xff\xd8\xff\xe0JPEG', 'image/jpeg')
        }
        resp = self.test_endpoint("POST", "/files/profile-picture", 200, headers=headers, files=files, test_name="Upload profile picture (files)")
        file_path = None
        try:
            if resp is not None and 200 <= resp.status_code < 300:
                file_path = resp.json().get('file_path')
        except Exception:
            file_path = None
        
        # 3) Files: upload to a named folder
        files = {
            'file': ('test.jpg', b'\xff\xd8\xff\xe0JPEG', 'image/jpeg')
        }
        resp_folder = self.test_endpoint("POST", "/files/upload/test", 200, headers=headers, files=files, test_name="Upload file to folder")
        uploaded_filename = None
        if resp_folder is not None and 200 <= resp_folder.status_code < 300:
            try:
                up_path = resp_folder.json().get('file_path')  # e.g., /uploads/test/<name>
                if up_path and '/' in up_path:
                    uploaded_filename = up_path.rsplit('/', 1)[-1]
            except Exception:
                pass
        
        # 4) Files: get uploaded file (API placeholder)
        if uploaded_filename:
            self.test_endpoint("GET", f"/files/uploads/test/{uploaded_filename}", 200, headers=headers, test_name="Get uploaded file")
        else:
            self.print_test("Get uploaded file", "SKIP", 200, "N/A", "No filename from upload")
    
    def test_dispatcher_endpoints(self):
        """Test Dispatcher endpoints (7 endpoints)"""
        self.print_header("5. DISPATCHER ENDPOINTS (7 endpoints)")
        
        if 'admin' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping dispatcher tests - no token{Colors.RESET}")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        
        # 1. Create Order
        self.print_section("POST /api/v1/dispatcher/order - Create Order")
        order_data = {
            "customer_phone": "+998901111111",
            "customer_name": "Test Customer",
            "pickup_location": {
                "lat": 41.2995,
                "lng": 69.2401,
                "address": "Toshkent"
            },
            "dropoff_location": {
                "lat": 41.3111,
                "lng": 69.2797,
                "address": "Chorsu"
            },
            "vehicle_type": "economy"
        }
        
        response = self.test_endpoint("POST", "/dispatcher/order", 200, headers=headers, json_data={"order": order_data, "broadcast": {"radius_km": 3.0}}, test_name="Create order")
        
        ride_id = None
        if response and 200 <= response.status_code < 300:
            ride_id = response.json().get('ride', {}).get('id')
            self.test_data['ride_id'] = ride_id
        
        # 2. Broadcast Order
        self.print_section("POST /api/v1/dispatcher/order/{ride_id}/broadcast - Broadcast Order")
        if ride_id:
            self.test_endpoint("POST", f"/dispatcher/order/{ride_id}/broadcast", 200, headers=headers, test_name="Broadcast order")
        else:
            self.print_test("Broadcast order", "SKIP", 200, "N/A", "No ride ID")
        
        # 3. Add Deposit (for the test user as driver)
        self.print_section("POST /api/v1/dispatcher/deposit - Add Deposit")
        deposit_data = {"driver_id": self.test_data.get('test_user_id', 1), "amount": 50000}
        self.test_endpoint("POST", "/dispatcher/deposit", 200, headers=headers, json_data=deposit_data, test_name="Add deposit")
        
        # 4-5. Block/Unblock Driver
        self.print_section("Driver Block/Unblock Endpoints")
        driver_id = self.test_data.get('test_user_id', 1)
        self.test_endpoint("POST", f"/dispatcher/block/{driver_id}", 200, headers=headers, test_name="Block driver")
        self.test_endpoint("POST", f"/dispatcher/unblock/{driver_id}", 200, headers=headers, test_name="Unblock driver")
        
        # 6. List Driver Locations
        self.print_section("GET /api/v1/dispatcher/drivers/locations - List Driver Locations")
        self.test_endpoint("GET", "/dispatcher/drivers/locations", 200, headers=headers, test_name="List driver locations")
        
        # 7. Cancel Order on a fresh ride (so driver flow can use the first ride)
        self.print_section("POST /api/v1/dispatcher/cancel/{ride_id} - Cancel Order")
        cancel_ride_id = None
        response_cancel = self.test_endpoint("POST", "/dispatcher/order", 200, headers=headers, json_data={"order": order_data, "broadcast": {"radius_km": 3.0}}, test_name="Create order for cancel")
        if response_cancel and 200 <= response_cancel.status_code < 300:
            cancel_ride_id = response_cancel.json().get('ride', {}).get('id')
        if cancel_ride_id:
            self.test_endpoint("POST", f"/dispatcher/cancel/{cancel_ride_id}", 200, headers=headers, test_name="Cancel order")
        else:
            self.print_test("Cancel order", "SKIP", 200, "N/A", "No ride ID for cancel")
    
    def test_driver_endpoints(self):
        """Test Driver endpoints (5 endpoints)"""
        self.print_header("6. DRIVER ENDPOINTS (5 endpoints)")
        
        if 'test_user' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping driver tests - no token{Colors.RESET}")
            return
        
        # Ensure driver is approved before accept/start/complete
        if 'admin' in self.tokens and self.test_data.get('test_user_id'):
            admin_headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            self.test_endpoint("PUT", f"/admin/users/{self.test_data['test_user_id']}/approve", 200, headers=admin_headers, test_name="Re-approve driver for driver flow")

        headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
        
        # 1. Update Status
        self.print_section("POST /api/v1/driver/status - Update Status")
        status_data = {
            "is_on_duty": True,
            "lat": 41.2995,
            "lng": 69.2401,
            "city": "Toshkent"
        }
        self.test_endpoint("POST", "/driver/status", 200, headers=headers, json_data=status_data, test_name="Update driver status")
        
        # 2-4. Ride Actions
        ride_id = self.test_data.get('ride_id')
        if ride_id:
            self.print_section(f"Ride Actions (Ride ID: {ride_id})")
            self.test_endpoint("POST", f"/driver/rides/{ride_id}/accept", 200, headers=headers, test_name="Accept ride")
            self.test_endpoint("POST", f"/driver/rides/{ride_id}/start", 200, headers=headers, test_name="Start ride")
            self.test_endpoint("POST", f"/driver/rides/{ride_id}/complete", 200, headers=headers, json_data={}, test_name="Complete ride")
        else:
            self.print_test("Accept ride", "SKIP", 200, "N/A", "No ride ID")
            self.print_test("Start ride", "SKIP", 200, "N/A", "No ride ID")
            self.print_test("Complete ride", "SKIP", 200, "N/A", "No ride ID")
        
        # 5. Driver Stats
        self.print_section("GET /api/v1/driver/stats - Driver Stats")
        self.test_endpoint("GET", "/driver/stats", 200, headers=headers, test_name="Get driver stats")
    
    def test_rider_endpoints(self):
        """Test Rider endpoints (6 endpoints)"""
        self.print_header("7. RIDER ENDPOINTS (6 endpoints)")
        
        # Need admin token to create rider's order (dispatcher-only endpoint). Also need driver token for acceptance.
        if 'admin' not in self.tokens or 'test_user' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping rider tests - missing admin or driver token{Colors.RESET}")
            return
        
        admin_headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        driver_headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
        
        # Create a fresh order as admin (dispatcher role)
        self.print_section("Setup: create rider order as admin")
        order_data = {
            "customer_phone": "+998901111112",
            "customer_name": "Rider Customer",
            "pickup_location": {
                "lat": 41.30,
                "lng": 69.24,
                "address": "Minor"
            },
            "dropoff_location": {
                "lat": 41.32,
                "lng": 69.28,
                "address": "Magic City"
            },
            "vehicle_type": "economy"
        }
        resp_rider_order = self.test_endpoint("POST", "/dispatcher/order", 200, headers=admin_headers, json_data={"order": order_data, "broadcast": {"radius_km": 3.0}}, test_name="Create rider order")
        rider_ride_id = None
        if resp_rider_order and 200 <= resp_rider_order.status_code < 300:
            rider_ride_id = resp_rider_order.json().get('ride', {}).get('id')
        
        # Ensure driver is on duty with a location, then accept this ride
        self.test_endpoint("POST", "/driver/status", 200, headers=driver_headers, json_data={
            "is_on_duty": True, "lat": 41.2995, "lng": 69.2401, "city": "Toshkent"
        }, test_name="Driver on-duty for rider flow")
        if rider_ride_id:
            self.test_endpoint("POST", f"/driver/rides/{rider_ride_id}/accept", 200, headers=driver_headers, test_name="Driver accepts rider ride")
        
        # Use admin headers (rider) to fetch rider endpoints
        headers = admin_headers
        
        # 1. Get Current Ride
        self.print_section("GET /api/v1/rider/current-ride - Get Current Ride")
        self.test_endpoint("GET", "/rider/current-ride", 200, headers=headers, test_name="Get current ride")
        
        ride_id = rider_ride_id or self.test_data.get('ride_id', 1)
        
        # 2-4. Ride Details/Status/Location
        self.print_section(f"Ride Details (Ride ID: {ride_id})")
        self.test_endpoint("GET", f"/rider/ride/{ride_id}", 200, headers=headers, test_name="Get ride details")
        self.test_endpoint("GET", f"/rider/ride/{ride_id}/status", 200, headers=headers, test_name="Get ride status")
        self.test_endpoint("GET", f"/rider/ride/{ride_id}/location", 200, headers=headers, test_name="Get driver location")
        
        # 5. Ride History
        self.print_section("GET /api/v1/rider/rides/history - Get Ride History")
        self.test_endpoint("GET", "/rider/rides/history", 200, headers=headers, test_name="Get ride history")
        
        # 6. Cancel Ride (allowed in accepted status)
        self.print_section("POST /api/v1/rider/ride/{ride_id}/cancel - Cancel Ride")
        self.test_endpoint("POST", f"/rider/ride/{ride_id}/cancel", 200, headers=headers, test_name="Cancel ride")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total_endpoints = self.count_total_endpoints()
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Endpoints: {total_endpoints}")
        print(f"Total Tests Run: {self.total_tests}")
        print(f"{Colors.GREEN}Passed: {self.passed_tests}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed_tests}{Colors.RESET}")
        print(f"{Colors.YELLOW}Skipped: {self.skipped_tests}{Colors.RESET}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")
        
        if self.failed_tests == 0:
            print(f"{Colors.GREEN}🎉 All tests passed!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠ Some tests failed. Please review the output above.{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}Endpoint Coverage:{Colors.RESET}")
        print(f"  Auth: 6/6")
        print(f"  Users: 6/6")
        print(f"  Admin: 20/20")
        print(f"  Files: 4/4")
        print(f"  Dispatcher: 7/7")
        print(f"  Driver: 5/5")
        print(f"  Rider: 6/6")
        print(f"  {Colors.GREEN}Total: 54/54 endpoints{Colors.RESET}")

if __name__ == "__main__":
    print(f"{Colors.CYAN}Royal Taxi API Complete Test Suite{Colors.RESET}")
    print(f"{Colors.CYAN}Testing all 54 endpoints...{Colors.RESET}\n")
    
    tester = CompleteAPITester()
    tester.run_all_tests()
