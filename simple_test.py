"""
Oddiy test - barcha yangi API'larni test qilish
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Health check
print("1️⃣  Health Check...")
response = requests.get(f"{BASE_URL}/health")
print(f"   ✅ Status: {response.json()}")

# 2. Services - ochiq endpoint (token kerak emas)
print("\n2️⃣  Xizmatlar (Services) - Ochiq API")
print("   📍 Mavjud xizmatlar...")
response = requests.get(f"{BASE_URL}/api/v1/services/available")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    services = response.json()
    print(f"   ✅ Xizmatlar soni: {len(services)}")
    for svc in services[:3]:
        print(f"      - {svc.get('name_uz')}: {svc.get('price')} UZS")
else:
    print(f"   Response: {response.text}")

print("\n   📍 Barcha xizmatlar...")
response = requests.get(f"{BASE_URL}/api/v1/services/all")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    services = response.json()
    print(f"   ✅ Jami xizmatlar: {len(services)}")
else:
    print(f"   Response: {response.text}")

# 3. Admin APIs (token kerak, lekin tekshiramiz)
print("\n3️⃣  Admin API'lari test")
print("   ℹ️  Bu API'lar token va admin huquqi talab qiladi")
print("   📍 Admin services endpoint mavjudligini tekshirish...")

# Shunchaki endpoint mavjudligini tekshir
response = requests.get(f"{BASE_URL}/api/v1/admin/services")
if response.status_code == 401:
    print(f"   ✅ Endpoint mavjud (401 Unauthorized - token kerak)")
elif response.status_code == 403:
    print(f"   ✅ Endpoint mavjud (403 Forbidden - admin huquqi kerak)")
else:
    print(f"   ⚠️  Status: {response.status_code}")

# 4. Driver APIs (token kerak)
print("\n4️⃣  Haydovchi API'lari test")
print("   ℹ️  Bu API'lar token va haydovchi huquqi talab qiladi\n")

endpoints = [
    ("Tariflar", "GET", "/api/v1/driver/pricing"),
    ("Taxometer", "GET", "/api/v1/driver/calculate-fare?distance=10&duration=20"),
    ("Safar tarixi", "GET", "/api/v1/driver/rides/history"),
    ("Xabarlar", "GET", "/api/v1/driver/notifications"),
    ("Statistika (barchasi)", "GET", "/api/v1/driver/stats/detailed?period=all"),
    ("Statistika (kunlik)", "GET", "/api/v1/driver/stats/detailed?period=daily&date=2025-11-05"),
]

for name, method, endpoint in endpoints:
    print(f"   📍 {name}...")
    if method == "GET":
        response = requests.get(f"{BASE_URL}{endpoint}")
    
    if response.status_code == 401:
        print(f"      ✅ Endpoint mavjud (401 - token kerak)")
    elif response.status_code == 403:
        print(f"      ✅ Endpoint mavjud (403 - haydovchi huquqi kerak)")
    elif response.status_code == 200:
        print(f"      ✅ Endpoint ishlayapti!")
    else:
        print(f"      ⚠️  Status: {response.status_code}")

print("\n" + "="*60)
print("✅ ASOSIY TESTLAR TUGADI!")
print("="*60)
print("\nℹ️  To'liq test uchun:")
print("   1. Swagger UI ga kiring: http://localhost:8000/docs")
print("   2. Login qiling (OTP orqali)")
print("   3. Barcha endpoint'larni to'g'ridan-to'g'ri sinab ko'ring")
