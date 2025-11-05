"""
BARCHA YANGI API'LARNI 200 OK BILAN TEST QILISH
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_test(name, status, expected=200):
    symbol = "✅" if status == expected else "❌"
    print(f"{symbol} {name}: {status} {'OK' if status == expected else 'FAILED'}")

print("🚀 BARCHA YANGI API'LARNI 200 BILAN TEST QILISH\n")

# ============ 1. OTP BILAN LOGIN ============
print("=" * 60)
print("1️⃣  AUTHENTICATION - OTP FLOW")
print("=" * 60)

phone = "+998991234567"
token = None
user_id = None

# Alternative: Use database directly to get OTP
print("\n🔄 Database'dan OTP kod olish...")
try:
    from database import SessionLocal
    from models import OTPVerification
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    
    # Step 1: Send OTP
    print(f"\n📞 OTP yuborish: {phone}")
    response = requests.post(f"{BASE_URL}/api/v1/auth/send-otp", json={"phone": phone})
    print_test("Send OTP", response.status_code)
    
    if response.status_code == 200:
        # Get OTP from database
        otp_record = db.query(OTPVerification).filter(
            OTPVerification.phone == phone,
            OTPVerification.is_verified == False,
            OTPVerification.expires_at > datetime.utcnow()
        ).order_by(OTPVerification.created_at.desc()).first()
        
        if otp_record:
            otp_code = otp_record.otp_code
            print(f"   📧 OTP kod (database'dan): {otp_code}")
            
            # Step 2: Verify OTP
            print(f"\n🔐 OTP ni tasdiqlash")
            verify_response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
                "phone": phone,
                "otp_code": otp_code
            })
            print_test("Verify OTP", verify_response.status_code)
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                
                # Step 3: Complete Profile (if needed)
                if verify_data.get("needs_profile_completion"):
                    print(f"\n👤 Profil to'ldirish kerak")
                    profile_data = {
                        "phone": phone,
                        "first_name": "Test",
                        "last_name": "Haydovchi",
                        "gender": "Erkak",
                        "date_of_birth": "1990-01-01",
                        "vehicle_make": "Chevrolet",
                        "vehicle_color": "Qora",
                        "position": "Haydovchi",
                        "license_plate": "01T123ST",
                        "tech_passport": "TT1234567"
                    }
                    complete_response = requests.post(f"{BASE_URL}/api/v1/auth/complete-profile", json=profile_data)
                    print_test("Complete Profile", complete_response.status_code)
                    
                    if complete_response.status_code == 200:
                        token = complete_response.json().get("access_token")
                        user_id = complete_response.json().get("user", {}).get("id")
                        print(f"   ✅ Token olindi! User ID: {user_id}")
                else:
                    print(f"   ⚠️  Profil allaqachon mavjud, login qiling")
                    # Login with phone/password
                    login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
                        "phone": phone,
                        "password": "test123"
                    })
                    if login_response.status_code == 200:
                        token = login_response.json().get("access_token")
                        user_id = login_response.json().get("user", {}).get("id")
                        print(f"   ✅ Token olindi! User ID: {user_id}")
        else:
            print("   ❌ Database'da OTP topilmadi")
    
    db.close()
    
except Exception as e:
    print(f"   ⚠️  Database usuli ishlamadi: {e}")
    print(f"   🔄 Mavjud user bilan login qilamiz...")
    
    # Fallback: login with existing user
    login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "phone": "+998901234567",
        "password": "test123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        user_id = login_response.json().get("user", {}).get("id")
        print(f"   ✅ Token olindi! User ID: {user_id}")

if not token:
    print("\n❌ Token olinmadi! Test to'xtatiladi.")
    print("ℹ️  Iloji: Swagger UI'da login qiling: http://localhost:8000/docs")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# ============ 2. SERVICES API'LARI (OCHIQ) ============
print("\n" + "=" * 60)
print("2️⃣  XIZMATLAR (SERVICES) - OCHIQ API'LAR")
print("=" * 60 + "\n")

response = requests.get(f"{BASE_URL}/api/v1/services/available")
print_test("GET /services/available", response.status_code)

response = requests.get(f"{BASE_URL}/api/v1/services/all")
print_test("GET /services/all", response.status_code)

# ============ 3. ADMIN SERVICES ============
print("\n" + "=" * 60)
print("3️⃣  ADMIN - XIZMATLARNI BOSHQARISH")
print("=" * 60 + "\n")

# Create service
service_data = {
    "name": f"test_service_{datetime.now().timestamp()}",
    "name_uz": "Test Xizmat",
    "name_ru": "Тест Сервис",
    "icon": "🧪",
    "price": 5000.0,
    "is_active": True,
    "display_order": 1,
    "description": "Test uchun xizmat"
}
response = requests.post(f"{BASE_URL}/api/v1/admin/services", json=service_data, headers=headers)
print_test("POST /admin/services (Create)", response.status_code, 201)

service_id = None
if response.status_code in [200, 201]:
    service_id = response.json().get("id")
    print(f"   📝 Yaratilgan xizmat ID: {service_id}")

# Get all services (admin)
response = requests.get(f"{BASE_URL}/api/v1/admin/services", headers=headers)
print_test("GET /admin/services (List)", response.status_code)

if service_id:
    # Update service
    update_data = {"price": 7000.0}
    response = requests.put(f"{BASE_URL}/api/v1/admin/services/{service_id}", json=update_data, headers=headers)
    print_test(f"PUT /admin/services/{service_id} (Update)", response.status_code)
    
    # Toggle service
    toggle_data = {"is_active": False}
    response = requests.put(f"{BASE_URL}/api/v1/admin/services/{service_id}/toggle", json=toggle_data, headers=headers)
    print_test(f"PUT /admin/services/{service_id}/toggle", response.status_code)
    
    # Get single service
    response = requests.get(f"{BASE_URL}/api/v1/services/{service_id}")
    print_test(f"GET /services/{service_id}", response.status_code)

# ============ 4. DRIVER API'LARI ============
print("\n" + "=" * 60)
print("4️⃣  HAYDOVCHI (DRIVER) YANGI API'LAR")
print("=" * 60 + "\n")

# Get pricing
response = requests.get(f"{BASE_URL}/api/v1/driver/pricing", headers=headers)
print_test("GET /driver/pricing", response.status_code)
if response.status_code == 200:
    pricing = response.json()
    print(f"   💰 Economy base fare: {pricing.get('economy', {}).get('base_fare')} UZS")

# Calculate fare (Taxometer)
params = {"distance": 10, "duration": 15, "vehicle_type": "economy"}
response = requests.get(f"{BASE_URL}/api/v1/driver/calculate-fare", params=params, headers=headers)
print_test("GET /driver/calculate-fare (Taxometer)", response.status_code)
if response.status_code == 200:
    calc = response.json()
    print(f"   🧮 Hisoblangan narx: {calc.get('total_fare')} UZS")
    print(f"   👨‍✈️ Haydovchi daromadi: {calc.get('driver_earnings')} UZS")

# Get ride history
params = {"page": 1, "limit": 10}
response = requests.get(f"{BASE_URL}/api/v1/driver/rides/history", params=params, headers=headers)
print_test("GET /driver/rides/history", response.status_code)
if response.status_code == 200:
    history = response.json()
    print(f"   📋 Jami safarlar: {history.get('total')}")

# Get notifications
params = {"page": 1, "limit": 10}
response = requests.get(f"{BASE_URL}/api/v1/driver/notifications", params=params, headers=headers)
print_test("GET /driver/notifications", response.status_code)
if response.status_code == 200:
    notifs = response.json()
    print(f"   📬 Jami xabarlar: {notifs.get('total')}")

# Get detailed stats - all time
response = requests.get(f"{BASE_URL}/api/v1/driver/stats/detailed?period=all", headers=headers)
print_test("GET /driver/stats/detailed (period=all)", response.status_code)
if response.status_code == 200:
    stats = response.json()
    print(f"   📊 Jami safarlar: {stats.get('total_rides')}")
    print(f"   💵 Jami daromad: {stats.get('total_revenue')} UZS")

# Get detailed stats - daily
today = datetime.now().strftime("%Y-%m-%d")
params = {"period": "daily", "date": today}
response = requests.get(f"{BASE_URL}/api/v1/driver/stats/detailed", params=params, headers=headers)
print_test(f"GET /driver/stats/detailed (daily, {today})", response.status_code)

# Get detailed stats - monthly
month = datetime.now().strftime("%Y-%m-01")
params = {"period": "monthly", "date": month}
response = requests.get(f"{BASE_URL}/api/v1/driver/stats/detailed", params=params, headers=headers)
print_test(f"GET /driver/stats/detailed (monthly, {month})", response.status_code)

# ============ CLEANUP ============
if service_id:
    print("\n" + "=" * 60)
    print("🧹 CLEANUP - Test xizmatni o'chirish")
    print("=" * 60 + "\n")
    response = requests.delete(f"{BASE_URL}/api/v1/admin/services/{service_id}", headers=headers)
    print_test(f"DELETE /admin/services/{service_id}", response.status_code)

# ============ SUMMARY ============
print("\n" + "=" * 60)
print("✅ BARCHA TESTLAR TUGADI!")
print("=" * 60)
print("\n📝 Swagger UI: http://localhost:8000/docs")
print("📖 API Docs: /home/azam/Desktop/yaratish/royaltaxi/API_DOKUMENTATSIYA_TOLIQ.md")
