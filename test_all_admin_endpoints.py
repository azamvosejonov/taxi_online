"""
BARCHA 24 TA ADMIN API'NI TO'LIQ TEST QILISH
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

success_count = 0
total_count = 0

def test(name, response, expected=200):
    global success_count, total_count
    total_count += 1
    status = response.status_code
    success = status == expected
    if success:
        success_count += 1
    
    symbol = "✅" if success else "❌"
    print(f"{symbol} {name}: {status}")
    
    if success and response.text:
        try:
            data = response.json()
            # Print key info
            if isinstance(data, list):
                print(f"   📊 Items: {len(data)}")
            elif isinstance(data, dict):
                keys_to_show = ['total', 'total_users', 'total_rides', 'commission_rate', 'message', 'user_id']
                for key in keys_to_show:
                    if key in data:
                        print(f"   📌 {key}: {data[key]}")
        except:
            pass
    elif not success:
        print(f"   ⚠️  {response.text[:150]}")
    
    return response

print("=" * 70)
print("🔐 BARCHA 24 TA ADMIN API'NI TEST QILISH")
print("=" * 70)
print(f"Token: {ADMIN_TOKEN[:40]}...\n")

# ============ 1. USER MANAGEMENT (11 endpoints) ============
print("=" * 70)
print("👥 USER MANAGEMENT API'LAR (11 ta)")
print("=" * 70 + "\n")

# 1. Get all users
print("1. GET /admin/users")
r = test("   Get All Users", requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers))
print()

# 2. Get system stats
print("2. GET /admin/stats")
r = test("   Get System Stats", requests.get(f"{BASE_URL}/api/v1/admin/stats", headers=headers))
print()

# 3. Daily analytics
print("3. GET /admin/analytics/daily")
r = test("   Get Daily Analytics", 
    requests.get(f"{BASE_URL}/api/v1/admin/analytics/daily", headers=headers))
print()

# 4. Weekly analytics
print("4. GET /admin/analytics/weekly")
r = test("   Get Weekly Analytics",
    requests.get(f"{BASE_URL}/api/v1/admin/analytics/weekly", headers=headers))
print()

# Get a user ID for testing
users_response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
test_user_id = None
if users_response.status_code == 200:
    users = users_response.json()
    # Find a non-admin user for testing
    for user in users:
        if not user.get('is_admin') and user.get('id') != 21:
            test_user_id = user.get('id')
            break
    
    if not test_user_id and users:
        test_user_id = users[0].get('id')

if test_user_id:
    print(f"📝 Test uchun User ID: {test_user_id}\n")
    
    # 5. Approve user
    print(f"5. PUT /admin/users/{test_user_id}/approve")
    r = test("   Approve User",
        requests.put(f"{BASE_URL}/api/v1/admin/users/{test_user_id}/approve", headers=headers))
    print()
    
    # 6. Unapprove user
    print(f"6. PUT /admin/users/{test_user_id}/unapprove")
    r = test("   Unapprove User",
        requests.put(f"{BASE_URL}/api/v1/admin/users/{test_user_id}/unapprove", headers=headers))
    print()
    
    # 7. Set as dispatcher
    print(f"7. PUT /admin/users/{test_user_id}/set-dispatcher")
    r = test("   Set User As Dispatcher",
        requests.put(f"{BASE_URL}/api/v1/admin/users/{test_user_id}/set-dispatcher", headers=headers))
    print()
    
    # 8. Set as admin
    print(f"8. PUT /admin/users/{test_user_id}/set-admin")
    r = test("   Set User As Admin",
        requests.put(f"{BASE_URL}/api/v1/admin/users/{test_user_id}/set-admin", headers=headers))
    print()
    
    # 9. Remove roles
    print(f"9. PUT /admin/users/{test_user_id}/remove-roles")
    r = test("   Remove User Roles",
        requests.put(f"{BASE_URL}/api/v1/admin/users/{test_user_id}/remove-roles", headers=headers))
    print()
    
    # 10. Deactivate user
    print(f"10. PUT /admin/users/{test_user_id}/deactivate")
    r = test("   Deactivate User",
        requests.put(f"{BASE_URL}/api/v1/admin/users/{test_user_id}/deactivate", headers=headers))
    print()
    
    # 11. Activate user
    print(f"11. PUT /admin/users/{test_user_id}/activate")
    r = test("   Activate User",
        requests.put(f"{BASE_URL}/api/v1/admin/users/{test_user_id}/activate", headers=headers))
    print()
else:
    print("⚠️  Test user topilmadi, user management API'lar o'tkazildi\n")
    total_count += 7  # Skip 7 endpoints

# ============ 2. INCOME & ANALYTICS (3 endpoints) ============
print("=" * 70)
print("💰 INCOME & ANALYTICS API'LAR (3 ta)")
print("=" * 70 + "\n")

# 12. Income stats
print("12. GET /admin/income/stats")
r = test("   Get Income Stats",
    requests.get(f"{BASE_URL}/api/v1/admin/income/stats", headers=headers))
print()

# 13. Monthly income
print("13. GET /admin/income/monthly/2025/11")
r = test("   Get Monthly Income",
    requests.get(f"{BASE_URL}/api/v1/admin/income/monthly/2025/11", headers=headers))
print()

# 14. Yearly income
print("14. GET /admin/income/yearly/2025")
r = test("   Get Yearly Income",
    requests.get(f"{BASE_URL}/api/v1/admin/income/yearly/2025", headers=headers))
print()

# ============ 3. CONFIGURATION (2 endpoints) ============
print("=" * 70)
print("⚙️  CONFIGURATION API'LAR (2 ta)")
print("=" * 70 + "\n")

# 15. Get commission rate
print("15. GET /admin/config/commission-rate")
r = test("   Get Commission Rate",
    requests.get(f"{BASE_URL}/api/v1/admin/config/commission-rate", headers=headers))
print()

# 16. Set commission rate
print("16. PUT /admin/config/commission-rate")
r = test("   Set Commission Rate",
    requests.put(f"{BASE_URL}/api/v1/admin/config/commission-rate?rate=0.10", headers=headers))
print()

# ============ 4. NOTIFICATIONS (2 endpoints) ============
print("=" * 70)
print("📢 NOTIFICATION API'LAR (2 ta)")
print("=" * 70 + "\n")

# 17. Notify all drivers
print("17. POST /admin/notify/all")
notify_data = {"title": "Test Xabar", "body": "Bu test xabari"}
r = test("   Notify All Drivers",
    requests.post(f"{BASE_URL}/api/v1/admin/notify/all", json=notify_data, headers=headers))
print()

# 18. Notify specific driver
if test_user_id:
    print(f"18. POST /admin/notify/{test_user_id}")
    r = test("   Notify Driver",
        requests.post(f"{BASE_URL}/api/v1/admin/notify/{test_user_id}", json=notify_data, headers=headers))
    print()
else:
    print("18. ⚠️  Notify Driver - user topilmadi\n")
    total_count += 1

# ============ 5. PRICING (3 endpoints) ============
print("=" * 70)
print("💵 PRICING API'LAR (3 ta)")
print("=" * 70 + "\n")

# 19. Get pricing config
print("19. GET /admin/pricing")
r = test("   Get Pricing Config",
    requests.get(f"{BASE_URL}/api/v1/admin/pricing", headers=headers))
print()

# 20. Update vehicle pricing
print("20. PUT /admin/pricing/economy")
pricing_data = {
    "vehicle_type": "economy",
    "base_fare": 10000,
    "per_km_rate": 2000,
    "per_minute_rate": 500
}
r = test("   Update Vehicle Pricing",
    requests.put(f"{BASE_URL}/api/v1/admin/pricing/economy", json=pricing_data, headers=headers))
print()

# 21. Calculate fare preview
print("21. GET /admin/pricing/calculate")
r = test("   Calculate Fare Preview",
    requests.get(f"{BASE_URL}/api/v1/admin/pricing/calculate?distance=10&duration=15&vehicle_type=economy", 
    headers=headers))
print()

# ============ 6. SERVICES (5 endpoints) ============
print("=" * 70)
print("🛍️  SERVICES API'LAR (5 ta)")
print("=" * 70 + "\n")

# 22. Get all services
print("22. GET /admin/services")
r = test("   Get All Services Admin",
    requests.get(f"{BASE_URL}/api/v1/admin/services", headers=headers))
print()

# 23. Create service
print("23. POST /admin/services")
service_data = {
    "name": f"final_test_{int(datetime.now().timestamp())}",
    "name_uz": "Final Test Xizmat",
    "name_ru": "Финал Тест Сервис",
    "icon": "🎯",
    "price": 8000.0,
    "is_active": True,
    "display_order": 1,
    "description": "Final test uchun xizmat"
}
r = test("   Create Service",
    requests.post(f"{BASE_URL}/api/v1/admin/services", json=service_data, headers=headers), 201)

service_id = None
if r and r.status_code in [200, 201]:
    service_id = r.json().get('id')
    print(f"   ✨ Service ID: {service_id}")
print()

if service_id:
    # 24. Update service
    print(f"24. PUT /admin/services/{service_id}")
    update_data = {"price": 9000.0}
    r = test("   Update Service",
        requests.put(f"{BASE_URL}/api/v1/admin/services/{service_id}", json=update_data, headers=headers))
    print()
    
    # 25. Toggle service
    print(f"25. PUT /admin/services/{service_id}/toggle")
    toggle_data = {"is_active": False}
    r = test("   Toggle Service",
        requests.put(f"{BASE_URL}/api/v1/admin/services/{service_id}/toggle", json=toggle_data, headers=headers))
    print()
    
    # 26. Delete service
    print(f"26. DELETE /admin/services/{service_id}")
    r = test("   Delete Service",
        requests.delete(f"{BASE_URL}/api/v1/admin/services/{service_id}", headers=headers))
    print()
else:
    print("24-26. ⚠️  Service API'lar - xizmat yaratilmadi\n")
    total_count += 3

# ============ SUMMARY ============
print("=" * 70)
print("📊 TEST NATIJALARI")
print("=" * 70)
print(f"\n✅ Muvaffaqiyatli: {success_count}/{total_count}")
print(f"📊 Foiz: {(success_count/total_count*100):.1f}%\n")

print("📋 API kategoriyalar:")
print(f"   👥 User Management: 11 endpoint")
print(f"   💰 Income & Analytics: 3 endpoint")
print(f"   ⚙️  Configuration: 2 endpoint")
print(f"   📢 Notifications: 2 endpoint")
print(f"   💵 Pricing: 3 endpoint")
print(f"   🛍️  Services: 5 endpoint")
print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"   📍 JAMI: 26 endpoint\n")

if success_count == total_count:
    print("🎉 BARCHA API'LAR 100% ISHLAYAPTI!")
else:
    print(f"⚠️  {total_count - success_count} ta API xatolik bilan ishladi")

print("\n🌐 Swagger UI: http://localhost:8000/docs")
