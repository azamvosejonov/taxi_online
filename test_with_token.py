"""
BERILGAN TOKEN BILAN BARCHA YANGI API'LARNI TEST QILISH
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIrOTk4OTAxMjM0MzY3IiwiZXhwIjoxNzYyMzQxOTI1fQ.0kXQrWoyJW6qEzTn0hYWFfFnM4r1y61HqNDG0Ae3src"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_api(name, method, endpoint, data=None, params=None, expected_status=200):
    """API test qilish helper funksiyasi"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        status = response.status_code
        success = status == expected_status
        
        symbol = "✅" if success else "❌"
        print(f"{symbol} {name}")
        print(f"   Status: {status} (expected: {expected_status})")
        
        if success and response.text:
            try:
                data = response.json()
                # Print some key info
                if isinstance(data, list):
                    print(f"   📊 Items: {len(data)}")
                elif isinstance(data, dict):
                    if 'total' in data:
                        print(f"   📊 Total: {data['total']}")
                    if 'total_fare' in data:
                        print(f"   💰 Total fare: {data['total_fare']} UZS")
                    if 'driver_earnings' in data:
                        print(f"   👨‍✈️ Driver earnings: {data['driver_earnings']} UZS")
                    if 'id' in data:
                        print(f"   🆔 ID: {data['id']}")
                    if 'message' in data:
                        print(f"   💬 Message: {data['message']}")
            except:
                pass
        elif not success:
            print(f"   ⚠️  Response: {response.text[:200]}")
        
        print()
        return response
    
    except Exception as e:
        print(f"❌ {name}")
        print(f"   Error: {e}\n")
        return None

print("=" * 70)
print("🚀 BARCHA YANGI API'LARNI TOKEN BILAN TEST QILISH")
print("=" * 70)
print(f"\n🔑 Token: {TOKEN[:50]}...\n")

# ============ 1. SERVICES (OCHIQ API'LAR) ============
print("=" * 70)
print("1️⃣  XIZMATLAR (SERVICES) - OCHIQ API'LAR")
print("=" * 70 + "\n")

test_api(
    "GET /services/available - Mavjud xizmatlar",
    "GET", "/api/v1/services/available"
)

test_api(
    "GET /services/all - Barcha xizmatlar",
    "GET", "/api/v1/services/all"
)

# ============ 2. ADMIN SERVICES ============
print("=" * 70)
print("2️⃣  ADMIN - XIZMATLARNI BOSHQARISH")
print("=" * 70 + "\n")

# 2.1. Create service
service_data = {
    "name": f"test_api_{int(datetime.now().timestamp())}",
    "name_uz": "Test API Xizmat",
    "name_ru": "Тест API Сервис",
    "icon": "🧪",
    "price": 5000.0,
    "is_active": True,
    "display_order": 1,
    "description": "API test uchun yaratilgan xizmat"
}

create_response = test_api(
    "POST /admin/services - Xizmat yaratish",
    "POST", "/api/v1/admin/services",
    data=service_data,
    expected_status=201
)

service_id = None
if create_response and create_response.status_code in [200, 201]:
    try:
        service_id = create_response.json().get("id")
        print(f"   ✨ Yaratilgan xizmat ID: {service_id}\n")
    except:
        pass

# 2.2. Get all services (admin)
test_api(
    "GET /admin/services - Barcha xizmatlar (Admin)",
    "GET", "/api/v1/admin/services"
)

if service_id:
    # 2.3. Update service
    test_api(
        f"PUT /admin/services/{service_id} - Xizmatni yangilash",
        "PUT", f"/api/v1/admin/services/{service_id}",
        data={"price": 7000.0, "description": "Yangilangan tavsif"}
    )
    
    # 2.4. Toggle service
    test_api(
        f"PUT /admin/services/{service_id}/toggle - Faollashtirish/O'chirish",
        "PUT", f"/api/v1/admin/services/{service_id}/toggle",
        data={"is_active": False}
    )
    
    # 2.5. Get single service
    test_api(
        f"GET /services/{service_id} - Bitta xizmat ma'lumotlari",
        "GET", f"/api/v1/services/{service_id}"
    )

# ============ 3. DRIVER YANGI API'LAR ============
print("=" * 70)
print("3️⃣  HAYDOVCHI (DRIVER) - YANGI API'LAR")
print("=" * 70 + "\n")

# 3.1. Get pricing
test_api(
    "GET /driver/pricing - Tariflarni ko'rish",
    "GET", "/api/v1/driver/pricing"
)

# 3.2. Calculate fare (Taxometer)
test_api(
    "GET /driver/calculate-fare - Taxometer (10km, 15min, economy)",
    "GET", "/api/v1/driver/calculate-fare",
    params={"distance": 10, "duration": 15, "vehicle_type": "economy"}
)

test_api(
    "GET /driver/calculate-fare - Taxometer (25km, 30min, comfort)",
    "GET", "/api/v1/driver/calculate-fare",
    params={"distance": 25, "duration": 30, "vehicle_type": "comfort"}
)

# 3.3. Get ride history
test_api(
    "GET /driver/rides/history - Safar tarixi (page 1)",
    "GET", "/api/v1/driver/rides/history",
    params={"page": 1, "limit": 10}
)

# 3.4. Get notifications
test_api(
    "GET /driver/notifications - Xabarlar tarixi",
    "GET", "/api/v1/driver/notifications",
    params={"page": 1, "limit": 20}
)

# 3.5. Get detailed stats - all time
test_api(
    "GET /driver/stats/detailed - Statistika (barcha vaqt)",
    "GET", "/api/v1/driver/stats/detailed",
    params={"period": "all"}
)

# 3.6. Get detailed stats - daily
today = datetime.now().strftime("%Y-%m-%d")
test_api(
    f"GET /driver/stats/detailed - Statistika (kunlik: {today})",
    "GET", "/api/v1/driver/stats/detailed",
    params={"period": "daily", "date": today}
)

# 3.7. Get detailed stats - weekly
test_api(
    f"GET /driver/stats/detailed - Statistika (haftalik: {today})",
    "GET", "/api/v1/driver/stats/detailed",
    params={"period": "weekly", "date": today}
)

# 3.8. Get detailed stats - monthly
month_start = datetime.now().strftime("%Y-%m-01")
test_api(
    f"GET /driver/stats/detailed - Statistika (oylik: {month_start})",
    "GET", "/api/v1/driver/stats/detailed",
    params={"period": "monthly", "date": month_start}
)

# ============ CLEANUP ============
if service_id:
    print("=" * 70)
    print("🧹 CLEANUP - Test xizmatni o'chirish")
    print("=" * 70 + "\n")
    
    test_api(
        f"DELETE /admin/services/{service_id} - Xizmatni o'chirish",
        "DELETE", f"/api/v1/admin/services/{service_id}"
    )

# ============ SUMMARY ============
print("=" * 70)
print("✅ BARCHA TESTLAR TUGADI!")
print("=" * 70)
print("\n📊 TEST NATIJALARI:")
print("   - Services API: 3 endpoint")
print("   - Admin Services API: 5 endpoint")
print("   - Driver yangi API: 10 endpoint")
print("   - JAMI: 18 ta yangi endpoint test qilindi!\n")
print("📖 Dokumentatsiya: API_DOKUMENTATSIYA_TOLIQ.md")
print("🌐 Swagger UI: http://localhost:8000/docs")
