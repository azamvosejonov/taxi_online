"""
Comprehensive API Test Suite for Royal Taxi
Tests all endpoints with success (200) and error cases (400, 422, 403, 404)
"""
import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8080/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

class APITester:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.tokens = {}
        self.test_data = {}
        
    def print_header(self, text):
        print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BLUE}{text.center(70)}{Colors.RESET}")
        print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    def print_test(self, name, status, expected, actual, details=""):
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"{Colors.GREEN}✓{Colors.RESET} {name}")
            print(f"  Expected: {expected}, Got: {actual}")
        else:
            self.failed_tests += 1
            print(f"{Colors.RED}✗{Colors.RESET} {name}")
            print(f"  Expected: {expected}, Got: {actual}")
            if details:
                print(f"  Details: {details}")
    
    def test_endpoint(self, method, endpoint, expected_status, headers=None, json_data=None, params=None, test_name=""):
        """Generic endpoint tester"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=json_data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=json_data, params=params)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            status = "PASS" if response.status_code == expected_status else "FAIL"
            details = response.json() if response.text else "No response body"
            
            self.print_test(
                test_name or f"{method} {endpoint}",
                status,
                expected_status,
                response.status_code,
                details if status == "FAIL" else ""
            )
            
            return response
            
        except Exception as e:
            self.print_test(
                test_name or f"{method} {endpoint}",
                "FAIL",
                expected_status,
                "ERROR",
                str(e)
            )
            return None
    
    def run_all_tests(self):
        """Run all API tests"""
        
        self.print_header("ROYAL TAXI API COMPREHENSIVE TEST SUITE")
        
        # 1. Authentication Tests
        self.test_auth_endpoints()
        
        # 2. OTP Authentication Tests
        self.test_otp_endpoints()
        
        # 3. User Management Tests
        self.test_user_endpoints()
        
        # 4. Admin Tests
        self.test_admin_endpoints()
        
        # 5. Dispatcher Tests
        self.test_dispatcher_endpoints()
        
        # 6. Driver Tests
        self.test_driver_endpoints()
        
        # 7. Rider Tests
        self.test_rider_endpoints()
        
        # 8. File Upload Tests
        self.test_file_endpoints()
        
        # Print Summary
        self.print_summary()
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.print_header("1. AUTHENTICATION ENDPOINTS")
        
        # Test 1.1: Register - Success (201)
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
            "POST", "/auth/register", 201,
            json_data=register_data,
            test_name="Register new user - Success"
        )
        
        if response and response.status_code == 201:
            self.tokens['test_user'] = response.json()['access_token']
            self.test_data['test_phone'] = register_data['phone']
        
        # Test 1.2: Register - Duplicate phone (400)
        self.test_endpoint(
            "POST", "/auth/register", 400,
            json_data=register_data,
            test_name="Register duplicate phone - Error 400"
        )
        
        # Test 1.3: Register - Invalid phone format (422)
        invalid_register = register_data.copy()
        invalid_register['phone'] = "123456789"
        self.test_endpoint(
            "POST", "/auth/register", 422,
            json_data=invalid_register,
            test_name="Register invalid phone - Error 422"
        )
        
        # Test 1.4: Register - Missing required field (422)
        incomplete_register = {"phone": "+998901234567"}
        self.test_endpoint(
            "POST", "/auth/register", 422,
            json_data=incomplete_register,
            test_name="Register missing fields - Error 422"
        )
        
        # Test 1.5: Login - Success (200)
        login_data = {
            "phone": self.test_data.get('test_phone', '+998901234567'),
            "password": "test123456"
        }
        
        response = self.test_endpoint(
            "POST", "/auth/login", 200,
            json_data=login_data,
            test_name="Login - Success"
        )
        
        if response and response.status_code == 200:
            self.tokens['logged_in_user'] = response.json()['access_token']
        
        # Test 1.6: Login - Wrong password (400)
        wrong_login = login_data.copy()
        wrong_login['password'] = "wrongpassword"
        self.test_endpoint(
            "POST", "/auth/login", 400,
            json_data=wrong_login,
            test_name="Login wrong password - Error 400"
        )
        
        # Test 1.7: Login - Invalid phone format (422)
        invalid_login = {"phone": "invalid", "password": "test123"}
        self.test_endpoint(
            "POST", "/auth/login", 422,
            json_data=invalid_login,
            test_name="Login invalid phone - Error 422"
        )
        
        # Test 1.8: Logout - Success (200)
        if 'logged_in_user' in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['logged_in_user']}"}
            self.test_endpoint(
                "POST", "/auth/logout", 200,
                headers=headers,
                test_name="Logout - Success"
            )
        
        # Test 1.9: Logout - No token (401)
        self.test_endpoint(
            "POST", "/auth/logout", 401,
            test_name="Logout without token - Error 401"
        )
    
    def test_otp_endpoints(self):
        """Test OTP authentication endpoints"""
        self.print_header("2. OTP AUTHENTICATION ENDPOINTS")
        
        # Test 2.1: Send OTP - Success (200)
        otp_phone = f"+99890{int(time.time()) % 10000000}"
        response = self.test_endpoint(
            "POST", "/auth/send-otp", 200,
            json_data={"phone": otp_phone},
            test_name="Send OTP - Success"
        )
        
        otp_code = None
        if response and response.status_code == 200:
            otp_code = response.json().get('otp_code')
            self.test_data['otp_phone'] = otp_phone
        
        # Test 2.2: Send OTP - Invalid phone (422)
        self.test_endpoint(
            "POST", "/auth/send-otp", 422,
            json_data={"phone": "invalid"},
            test_name="Send OTP invalid phone - Error 422"
        )
        
        # Test 2.3: Verify OTP - Success (200)
        if otp_code:
            self.test_endpoint(
                "POST", "/auth/verify-otp", 200,
                json_data={"phone": otp_phone, "otp_code": otp_code},
                test_name="Verify OTP - Success"
            )
        
        # Test 2.4: Verify OTP - Wrong code (400)
        self.test_endpoint(
            "POST", "/auth/verify-otp", 400,
            json_data={"phone": otp_phone, "otp_code": "000000"},
            test_name="Verify OTP wrong code - Error 400"
        )
        
        # Test 2.5: Verify OTP - Invalid format (422)
        self.test_endpoint(
            "POST", "/auth/verify-otp", 422,
            json_data={"phone": otp_phone, "otp_code": "12345"},
            test_name="Verify OTP invalid format - Error 422"
        )
        
        # Test 2.6: Complete Profile - Success (201)
        if otp_code:
            profile_data = {
                "phone": otp_phone,
                "first_name": "OTP",
                "last_name": "User",
                "gender": "Erkak",
                "date_of_birth": "1990-01-01",
                "vehicle_make": "Toyota",
                "vehicle_color": "Oq",
                "position": "Haydovchi",
                "license_plate": f"01O{int(time.time()) % 1000}TP",
                "tech_passport": f"OTP{int(time.time()) % 100000}"
            }
            
            self.test_endpoint(
                "POST", "/auth/complete-profile", 201,
                json_data=profile_data,
                test_name="Complete profile - Success"
            )
        
        # Test 2.7: Complete Profile - Not verified (400)
        unverified_profile = {
            "phone": "+998909999999",
            "first_name": "Test",
            "last_name": "User",
            "gender": "Erkak",
            "date_of_birth": "1990-01-01",
            "vehicle_make": "Toyota",
            "vehicle_color": "Oq",
            "position": "Haydovchi",
            "license_plate": "01T999ZZ",
            "tech_passport": "TEST999999"
        }
        
        self.test_endpoint(
            "POST", "/auth/complete-profile", 400,
            json_data=unverified_profile,
            test_name="Complete profile not verified - Error 400"
        )
    
    def test_user_endpoints(self):
        """Test user management endpoints"""
        self.print_header("3. USER MANAGEMENT ENDPOINTS")
        
        if 'test_user' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping user tests - no token available{Colors.RESET}")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
        
        # Test 3.1: Get current user - Success (200)
        self.test_endpoint(
            "GET", "/users/me", 200,
            headers=headers,
            test_name="Get current user - Success"
        )
        
        # Test 3.2: Get current user - No token (401)
        self.test_endpoint(
            "GET", "/users/me", 401,
            test_name="Get current user no token - Error 401"
        )
        
        # Test 3.3: Get current user - Invalid token (401)
        bad_headers = {"Authorization": "Bearer invalid_token"}
        self.test_endpoint(
            "GET", "/users/me", 401,
            headers=bad_headers,
            test_name="Get current user invalid token - Error 401"
        )
    
    def test_admin_endpoints(self):
        """Test admin endpoints"""
        self.print_header("4. ADMIN ENDPOINTS")
        
        # Get admin credentials from environment or ask user
        admin_phone = os.getenv('ADMIN_PHONE', '').strip()
        admin_password = os.getenv('ADMIN_PASSWORD', '').strip()
        
        if not admin_phone or admin_phone == '+1234567890':
            print(f"{Colors.YELLOW}ℹ Admin credentials not found in .env{Colors.RESET}")
            admin_phone = input("Admin telefon raqam (+998XXXXXXXXX) yoki Enter (skip): ").strip()
            
            if not admin_phone:
                print(f"{Colors.YELLOW}⚠ Skipping admin tests - no admin credentials{Colors.RESET}")
                return
            
            admin_password = input("Admin parol: ").strip()
        else:
            print(f"{Colors.YELLOW}ℹ Using admin credentials from .env: {admin_phone}{Colors.RESET}")
        
        # Login as admin
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"phone": admin_phone, "password": admin_password}
        )
        
        if response.status_code != 200:
            print(f"{Colors.YELLOW}⚠ Skipping admin tests - login failed{Colors.RESET}")
            return
        
        admin_token = response.json()['access_token']
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test 4.1: Get all users - Success (200)
        self.test_endpoint(
            "GET", "/admin/users", 200,
            headers=admin_headers,
            test_name="Admin get all users - Success"
        )
        
        # Test 4.2: Get all users - Non-admin (403)
        if 'test_user' in self.tokens:
            user_headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
            self.test_endpoint(
                "GET", "/admin/users", 403,
                headers=user_headers,
                test_name="Admin endpoint non-admin - Error 403"
            )
        
        # Test 4.3: Get stats - Success (200)
        self.test_endpoint(
            "GET", "/admin/stats", 200,
            headers=admin_headers,
            test_name="Admin get stats - Success"
        )
        
        # Test 4.4: Get pricing config - Success (200)
        self.test_endpoint(
            "GET", "/admin/pricing", 200,
            headers=admin_headers,
            test_name="Admin get pricing - Success"
        )
        
        # Test 4.5: Calculate fare - Success (200)
        self.test_endpoint(
            "GET", "/admin/pricing/calculate", 200,
            headers=admin_headers,
            params={"distance": 10, "duration": 20, "vehicle_type": "economy"},
            test_name="Admin calculate fare - Success"
        )
        
        # Test 4.6: Calculate fare - Invalid vehicle type (400)
        self.test_endpoint(
            "GET", "/admin/pricing/calculate", 400,
            headers=admin_headers,
            params={"distance": 10, "duration": 20, "vehicle_type": "invalid"},
            test_name="Admin calculate fare invalid type - Error 400"
        )
        
        # Test 4.7: Update pricing - Success (200)
        pricing_data = {
            "vehicle_type": "economy",
            "base_fare": 10000,
            "per_km_rate": 2000,
            "per_minute_rate": 500
        }
        
        self.test_endpoint(
            "PUT", "/admin/pricing/economy", 200,
            headers=admin_headers,
            json_data=pricing_data,
            test_name="Admin update pricing - Success"
        )
        
        # Test 4.8: Update pricing - Invalid type (400)
        self.test_endpoint(
            "PUT", "/admin/pricing/invalid", 400,
            headers=admin_headers,
            json_data=pricing_data,
            test_name="Admin update pricing invalid type - Error 400"
        )
        
        # Test 4.9: Update pricing - Invalid data (422)
        invalid_pricing = {"vehicle_type": "economy", "base_fare": -1000}
        self.test_endpoint(
            "PUT", "/admin/pricing/economy", 422,
            headers=admin_headers,
            json_data=invalid_pricing,
            test_name="Admin update pricing invalid data - Error 422"
        )
        
        # Test 4.10: Set commission rate - Success (200)
        self.test_endpoint(
            "PUT", "/admin/config/commission-rate", 200,
            headers=admin_headers,
            params={"rate": 0.1},
            test_name="Admin set commission - Success"
        )
        
        # Test 4.11: Set commission rate - Invalid (400)
        self.test_endpoint(
            "PUT", "/admin/config/commission-rate", 400,
            headers=admin_headers,
            params={"rate": 1.5},
            test_name="Admin set commission invalid - Error 400"
        )
    
    def test_dispatcher_endpoints(self):
        """Test dispatcher endpoints"""
        self.print_header("5. DISPATCHER ENDPOINTS")
        
        if 'test_user' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping dispatcher tests - no token{Colors.RESET}")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
        
        # Test 5.1: Create order - Success (201)
        order_data = {
            "customer_phone": "+998901111111",
            "customer_name": "Test Customer",
            "pickup_location": {
                "lat": 41.2995,
                "lng": 69.2401,
                "address": "Toshkent, Amir Temur ko'chasi"
            },
            "dropoff_location": {
                "lat": 41.3111,
                "lng": 69.2797,
                "address": "Toshkent, Chorsu bozori"
            },
            "vehicle_type": "economy"
        }
        
        response = self.test_endpoint(
            "POST", "/dispatcher/order", 201,
            headers=headers,
            json_data=order_data,
            test_name="Dispatcher create order - Success"
        )
        
        if response and response.status_code == 201:
            self.test_data['ride_id'] = response.json()['ride']['id']
        
        # Test 5.2: Create order - Invalid phone (422)
        invalid_order = order_data.copy()
        invalid_order['customer_phone'] = "invalid"
        self.test_endpoint(
            "POST", "/dispatcher/order", 422,
            headers=headers,
            json_data=invalid_order,
            test_name="Dispatcher create order invalid phone - Error 422"
        )
        
        # Test 5.3: Create order - Missing location (422)
        incomplete_order = {"customer_phone": "+998901111111"}
        self.test_endpoint(
            "POST", "/dispatcher/order", 422,
            headers=headers,
            json_data=incomplete_order,
            test_name="Dispatcher create order missing data - Error 422"
        )
    
    def test_driver_endpoints(self):
        """Test driver endpoints"""
        self.print_header("6. DRIVER ENDPOINTS")
        
        if 'test_user' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping driver tests - no token{Colors.RESET}")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
        
        # Test 6.1: Update status - Success (200)
        status_data = {
            "is_on_duty": True,
            "lat": 41.2995,
            "lng": 69.2401,
            "city": "Toshkent"
        }
        
        self.test_endpoint(
            "POST", "/driver/status", 200,
            headers=headers,
            json_data=status_data,
            test_name="Driver update status - Success"
        )
        
        # Test 6.2: Update status - Invalid coordinates (422)
        invalid_status = {
            "is_on_duty": True,
            "lat": 999,
            "lng": 999
        }
        
        self.test_endpoint(
            "POST", "/driver/status", 422,
            headers=headers,
            json_data=invalid_status,
            test_name="Driver update status invalid coords - Error 422"
        )
        
        # Test 6.3: Get stats - Success (200)
        self.test_endpoint(
            "GET", "/driver/stats", 200,
            headers=headers,
            test_name="Driver get stats - Success"
        )
    
    def test_rider_endpoints(self):
        """Test rider endpoints"""
        self.print_header("7. RIDER ENDPOINTS")
        
        if 'test_user' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping rider tests - no token{Colors.RESET}")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['test_user']}"}
        
        # Test 7.1: Update location - Success (200)
        if 'ride_id' in self.test_data:
            location_data = {
                "lat": 41.3000,
                "lng": 69.2450
            }
            
            self.test_endpoint(
                "POST", f"/rider/rides/{self.test_data['ride_id']}/location", 200,
                headers=headers,
                json_data=location_data,
                test_name="Rider update location - Success"
            )
        
        # Test 7.2: Update location - Invalid ride (404)
        location_data = {"lat": 41.3000, "lng": 69.2450}
        self.test_endpoint(
            "POST", "/rider/rides/99999/location", 404,
            headers=headers,
            json_data=location_data,
            test_name="Rider update location invalid ride - Error 404"
        )
    
    def test_file_endpoints(self):
        """Test file upload endpoints"""
        self.print_header("8. FILE UPLOAD ENDPOINTS")
        
        if 'test_user' not in self.tokens:
            print(f"{Colors.YELLOW}⚠ Skipping file tests - no token{Colors.RESET}")
            return
        
        print(f"{Colors.YELLOW}ℹ File upload tests require actual files - skipping for now{Colors.RESET}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"{Colors.GREEN}Passed: {self.passed_tests}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed_tests}{Colors.RESET}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")
        
        if self.failed_tests == 0:
            print(f"{Colors.GREEN}🎉 All tests passed!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠ Some tests failed. Please review the output above.{Colors.RESET}")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
