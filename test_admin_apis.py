"""
ADMIN TOKEN BILAN BARCHA ADMIN API'LARNI TEST QILISH
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIrOTk4OTA5OTk5OTk5IiwiZXhwIjoxNzYyMzQyMzc1fQ.6w6Wa2fKNCRuS3v7ONZor_38KBd4MabQz-w8Zz1Rrtw"

headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

def test(name, status, expected=200):
    symbol = "✅" if status == expected else "❌"
    print(f"{symbol} {name}: {status}")

print("=" * 70)
print("🔐 ADMIN TOKEN BILAN BARCHA ADMIN API'LARNI TEST QILISH")
print("=" * 70)
print(f"\n🔑 Admin Token: {ADMIN_TOKEN[:50]}...\n")

# ============ ADMIN SERVICES API'LARI ============
print("=" * 70)
print("📦 ADMIN - XIZMATLARNI BOSHQARISH")
print("=" * 70 + "\n")

# 1. Create service
print("1. POST /admin/services - Xizmat yaratish")
service_data = {
    "name": f"admin_test_{int(datetime.now().timestamp())}",
    "name_uz": "Admin Test Xizmat",
    "name_ru": "Админ Тест Сервис",
    "icon": "🔧",
    "price": 10000.0,
    "is_active": True,
    "display_order": 1,
    "description": "Admin tomonidan yaratilgan test xizmat"
}
response = requests.post(f"{BASE_URL}/api/v1/admin/services", json=service_data, headers=headers)
test("   POST /admin/services", response.status_code, 201)

service_id = None
if response.status_code in [200, 201]:
    data = response.json()
    service_id = data.get("id")
    print(f"   ✨ Yaratilgan xizmat:")
    print(f"      ID: {service_id}")
    print(f"      Nomi: {data.get('name_uz')}")
    print(f"      Narxi: {data.get('price')} UZS")
print()

# 2. Get all services (admin)
print("2. GET /admin/services - Barcha xizmatlarni ko'rish")
response = requests.get(f"{BASE_URL}/api/v1/admin/services", headers=headers)
test("   GET /admin/services", response.status_code)
if response.status_code == 200:
    services = response.json()
    print(f"   📊 Jami xizmatlar: {len(services)}")
    for svc in services[:3]:
        print(f"      - {svc.get('name_uz')}: {svc.get('price')} UZS (Faol: {svc.get('is_active')})")
print()

if service_id:
    # 3. Update service
    print(f"3. PUT /admin/services/{service_id} - Xizmatni yangilash")
    update_data = {
        "price": 15000.0,
        "description": "Yangilangan tavsif - Admin tomonidan"
    }
    response = requests.put(f"{BASE_URL}/api/v1/admin/services/{service_id}", json=update_data, headers=headers)
    test(f"   PUT /admin/services/{service_id}", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print(f"   💰 Yangi narx: {data.get('price')} UZS")
    print()
    
    # 4. Toggle service
    print(f"4. PUT /admin/services/{service_id}/toggle - Faollashtirish/O'chirish")
    toggle_data = {"is_active": False}
    response = requests.put(f"{BASE_URL}/api/v1/admin/services/{service_id}/toggle", json=toggle_data, headers=headers)
    test(f"   PUT /admin/services/{service_id}/toggle", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print(f"   🔴 Xizmat o'chirildi: is_active = {data.get('is_active')}")
    print()
    
    # Toggle back to active
    toggle_data = {"is_active": True}
    response = requests.put(f"{BASE_URL}/api/v1/admin/services/{service_id}/toggle", json=toggle_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   🟢 Xizmat yoqildi: is_active = {data.get('is_active')}")
    print()
    
    # 5. Get single service
    print(f"5. GET /services/{service_id} - Bitta xizmat ma'lumotlari")
    response = requests.get(f"{BASE_URL}/api/v1/services/{service_id}")
    test(f"   GET /services/{service_id}", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print(f"   📝 Xizmat: {data.get('name_uz')}")
        print(f"   💰 Narx: {data.get('price')} UZS")
        print(f"   📊 Faol: {data.get('is_active')}")
    print()

# ============ BOSHQA ADMIN API'LARI ============
print("=" * 70)
print("👔 BOSHQA ADMIN API'LARI")
print("=" * 70 + "\n")

# 6. Get all users
print("6. GET /admin/users - Barcha foydalanuvchilar")
response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
test("   GET /admin/users", response.status_code)
if response.status_code == 200:
    users = response.json()
    print(f"   👥 Jami foydalanuvchilar: {len(users)}")
print()

# 7. Get system stats
print("7. GET /admin/stats - Sistema statistikasi")
response = requests.get(f"{BASE_URL}/api/v1/admin/stats", headers=headers)
test("   GET /admin/stats", response.status_code)
if response.status_code == 200:
    stats = response.json()
    print(f"   📊 Statistika:")
    print(f"      Total users: {stats.get('total_users', 0)}")
    print(f"      Total drivers: {stats.get('total_drivers', 0)}")
    print(f"      Total rides: {stats.get('total_rides', 0)}")
print()

# 8. Get pricing
print("8. GET /admin/pricing - Narxlar konfiguratsiyasi")
response = requests.get(f"{BASE_URL}/api/v1/admin/pricing", headers=headers)
test("   GET /admin/pricing", response.status_code)
if response.status_code == 200:
    pricing = response.json()
    print(f"   💰 Narxlar:")
    print(f"      Economy: {pricing.get('economy', {}).get('base_fare')} UZS")
    print(f"      Comfort: {pricing.get('comfort', {}).get('base_fare')} UZS")
    print(f"      Commission: {pricing.get('commission_rate', 0) * 100}%")
print()

# 9. Calculate fare preview
print("9. GET /admin/pricing/calculate - Narx hisoblash (preview)")
params = {"distance": 15, "duration": 25, "vehicle_type": "economy"}
response = requests.get(f"{BASE_URL}/api/v1/admin/pricing/calculate", params=params, headers=headers)
test("   GET /admin/pricing/calculate", response.status_code)
if response.status_code == 200:
    calc = response.json()
    print(f"   🧮 Hisoblangan narx (15km, 25min, economy):")
    print(f"      Total fare: {calc.get('total_fare')} UZS")
    print(f"      Commission: {calc.get('commission_amount')} UZS")
    print(f"      Driver earnings: {calc.get('driver_earnings')} UZS")
print()

# 10. Get commission rate
print("10. GET /admin/config/commission-rate - Komissiya stavkasi")
response = requests.get(f"{BASE_URL}/api/v1/admin/config/commission-rate", headers=headers)
test("   GET /admin/config/commission-rate", response.status_code)
if response.status_code == 200:
    data = response.json()
    print(f"   📊 Commission rate: {data.get('commission_rate', 0) * 100}%")
print()

# ============ CLEANUP ============
if service_id:
    print("=" * 70)
    print("🧹 CLEANUP - Test xizmatni o'chirish")
    print("=" * 70 + "\n")
    
    print(f"DELETE /admin/services/{service_id}")
    response = requests.delete(f"{BASE_URL}/api/v1/admin/services/{service_id}", headers=headers)
    test(f"   DELETE /admin/services/{service_id}", response.status_code)
    if response.status_code == 200:
        print(f"   🗑️  Xizmat muvaffaqiyatli o'chirildi")
    print()

# ============ SUMMARY ============
print("=" * 70)
print("✅ BARCHA ADMIN API'LAR TEST QILINDI!")
print("=" * 70)
print("\n📊 TEST NATIJALARI:")
print("   ✅ Admin Services: 5 endpoint")
print("   ✅ Admin Management: 5 endpoint")
print("   ✅ JAMI: 10 ta admin endpoint test qilindi!")
print()
print("📖 Dokumentatsiya: API_DOKUMENTATSIYA_TOLIQ.md")
print("🌐 Swagger UI: http://localhost:8000/docs")
