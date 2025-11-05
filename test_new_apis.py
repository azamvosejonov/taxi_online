"""
Test script for all new APIs
Barcha yangi API'larni test qilish
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_all():
    print("\n" + "🚀 BARCHA YANGI API'LARNI TEST QILISH BOSHLANDI\n")
    
    # ============ 1. LOGIN (Token olish) ============
    print("📍 1. Login qilish...")
    login_data = {
        "phone": "+998901234567",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/send-otp", json={"phone": login_data["phone"]})
    
    if response.status_code == 200:
        otp_code = response.json().get("otp_code", "123456")
        print(f"   OTP kod: {otp_code}")
        
        # Verify OTP
        verify_response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
            "phone": login_data["phone"],
            "otp_code": otp_code
        })
        
        if verify_response.status_code == 200 and verify_response.json().get("needs_profile_completion"):
            # Complete profile
            profile_data = {
                "phone": login_data["phone"],
                "first_name": "Test",
                "last_name": "Driver",
                "gender": "Erkak",
                "date_of_birth": "1990-01-01",
                "vehicle_make": "Chevrolet",
                "vehicle_color": "Qora",
                "position": "Haydovchi",
                "license_plate": "01A123AA",
                "tech_passport": "AA1234567"
            }
            complete_response = requests.post(f"{BASE_URL}/api/v1/auth/complete-profile", json=profile_data)
            token = complete_response.json().get("access_token")
        else:
            # Try login
            login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
            if login_response.status_code == 404:
                print("   ⚠️  Foydalanuvchi topilmadi, yangi profil yaratamiz...")
                # Complete profile
                profile_data = {
                    "phone": login_data["phone"],
                    "first_name": "Test",
                    "last_name": "Driver",
                    "gender": "Erkak",
                    "date_of_birth": "1990-01-01",
                    "vehicle_make": "Chevrolet",
                    "vehicle_color": "Qora",
                    "position": "Haydovchi",
                    "license_plate": "01A123AA",
                    "tech_passport": "AA1234567"
                }
                complete_response = requests.post(f"{BASE_URL}/api/v1/auth/complete-profile", json=profile_data)
                token = complete_response.json().get("access_token")
            else:
                token = login_response.json().get("access_token")
    else:
        print(f"   ❌ Login failed: {response.text}")
        return
    
    if not token:
        print("   ❌ Token olinmadi!")
        return
        
    print(f"   ✅ Token olindi!")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # ============ 2. SERVICES API'LARI ============
    print("\n" + "="*60)
    print("📦 XIZMATLAR (SERVICES) API'LARI")
    print("="*60)
    
    # 2.1. Get available services
    response = requests.get(f"{BASE_URL}/api/v1/services/available")
    print_response("2.1. Mavjud xizmatlar", response)
    
    # 2.2. Get all services
    response = requests.get(f"{BASE_URL}/api/v1/services/all")
    print_response("2.2. Barcha xizmatlar", response)
    
    # ============ 3. ADMIN SERVICES API'LARI ============
    print("\n" + "="*60)
    print("👔 ADMIN SERVICES API'LARI")
    print("="*60)
    
    # 3.1. Create service
    service_data = {
        "name": "konditsioner",
        "name_uz": "Konditsioner",
        "name_ru": "Кондиционер",
        "icon": "❄️",
        "price": 5000.0,
        "is_active": True,
        "display_order": 1,
        "description": "Avtomobilni sovutish"
    }
    response = requests.post(f"{BASE_URL}/api/v1/admin/services", json=service_data, headers=headers)
    print_response("3.1. Xizmat yaratish", response)
    
    service_id = None
    if response.status_code in [200, 201]:
        service_id = response.json().get("id")
    
    # 3.2. Get all services (admin)
    response = requests.get(f"{BASE_URL}/api/v1/admin/services", headers=headers)
    print_response("3.2. Admin - barcha xizmatlar", response)
    
    if service_id:
        # 3.3. Update service
        update_data = {
            "price": 6000.0,
            "is_active": True
        }
        response = requests.put(f"{BASE_URL}/api/v1/admin/services/{service_id}", json=update_data, headers=headers)
        print_response(f"3.3. Xizmatni yangilash (ID: {service_id})", response)
        
        # 3.4. Toggle service
        toggle_data = {"is_active": False}
        response = requests.put(f"{BASE_URL}/api/v1/admin/services/{service_id}/toggle", json=toggle_data, headers=headers)
        print_response(f"3.4. Xizmatni o'chirish (ID: {service_id})", response)
    
    # ============ 4. DRIVER API'LARI ============
    print("\n" + "="*60)
    print("🚗 HAYDOVCHI (DRIVER) YANGI API'LARI")
    print("="*60)
    
    # 4.1. Get pricing
    response = requests.get(f"{BASE_URL}/api/v1/driver/pricing", headers=headers)
    print_response("4.1. Tariflarni ko'rish", response)
    
    # 4.2. Calculate fare (Taxometer)
    params = {
        "distance": 10.5,
        "duration": 20,
        "vehicle_type": "economy"
    }
    response = requests.get(f"{BASE_URL}/api/v1/driver/calculate-fare", params=params, headers=headers)
    print_response("4.2. Taxometer - Narx hisoblash", response)
    
    # 4.3. Get ride history
    params = {"page": 1, "limit": 10}
    response = requests.get(f"{BASE_URL}/api/v1/driver/rides/history", params=params, headers=headers)
    print_response("4.3. Safar tarixi", response)
    
    # 4.4. Get notifications
    params = {"page": 1, "limit": 10}
    response = requests.get(f"{BASE_URL}/api/v1/driver/notifications", params=params, headers=headers)
    print_response("4.4. Xabarlar tarixi", response)
    
    # 4.5. Get detailed stats (all time)
    response = requests.get(f"{BASE_URL}/api/v1/driver/stats/detailed?period=all", headers=headers)
    print_response("4.5. Batafsil statistika (barchasi)", response)
    
    # 4.6. Get detailed stats (daily)
    params = {"period": "daily", "date": "2025-11-05"}
    response = requests.get(f"{BASE_URL}/api/v1/driver/stats/detailed", params=params, headers=headers)
    print_response("4.6. Batafsil statistika (kunlik)", response)
    
    # 4.7. Get detailed stats (monthly)
    params = {"period": "monthly", "date": "2025-11-01"}
    response = requests.get(f"{BASE_URL}/api/v1/driver/stats/detailed", params=params, headers=headers)
    print_response("4.7. Batafsil statistika (oylik)", response)
    
    print("\n" + "="*60)
    print("✅ BARCHA TESTLAR TUGADI!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_all()
    except Exception as e:
        print(f"\n❌ Xatolik: {e}")
        import traceback
        traceback.print_exc()
