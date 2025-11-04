"""
Test script for Admin Pricing Management
"""
import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def test_admin_pricing():
    """Test admin pricing management endpoints"""
    
    print("=" * 60)
    print("Admin Narxlarni Boshqarish Test")
    print("=" * 60)
    
    # Step 1: Admin login
    print("\n1️⃣  Admin login...")
    admin_phone = input("Admin telefon raqam (+998XXXXXXXXX): ").strip()
    admin_password = input("Admin parol: ").strip()
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "phone": admin_phone,
            "password": admin_password
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login xatosi: {response.json()}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Login muvaffaqiyatli! Token: {token[:50]}...")
    
    # Step 2: Get current pricing
    print("\n2️⃣  Hozirgi narxlarni ko'rish...")
    response = requests.get(f"{BASE_URL}/admin/pricing", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Xato: {response.json()}")
        return
    
    pricing = response.json()
    print(f"\n✅ Hozirgi narxlar:")
    print(f"\n📊 Economy:")
    print(f"   Boshlang'ich: {pricing['economy']['base_fare']:,} so'm")
    print(f"   Har km: {pricing['economy']['per_km_rate']:,} so'm")
    print(f"   Har daqiqa: {pricing['economy']['per_minute_rate']:,} so'm")
    
    print(f"\n📊 Comfort:")
    print(f"   Boshlang'ich: {pricing['comfort']['base_fare']:,} so'm")
    print(f"   Har km: {pricing['comfort']['per_km_rate']:,} so'm")
    print(f"   Har daqiqa: {pricing['comfort']['per_minute_rate']:,} so'm")
    
    print(f"\n📊 Business:")
    print(f"   Boshlang'ich: {pricing['business']['base_fare']:,} so'm")
    print(f"   Har km: {pricing['business']['per_km_rate']:,} so'm")
    print(f"   Har daqiqa: {pricing['business']['per_minute_rate']:,} so'm")
    
    print(f"\n💰 Komissiya: {pricing['commission_rate'] * 100}%")
    
    # Step 3: Calculate fare
    print("\n3️⃣  Narxni hisoblash (10 km, 20 daqiqa, economy)...")
    response = requests.get(
        f"{BASE_URL}/admin/pricing/calculate",
        params={
            "distance": 10,
            "duration": 20,
            "vehicle_type": "economy"
        },
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Xato: {response.json()}")
        return
    
    calc = response.json()
    print(f"\n✅ Hisoblash natijasi:")
    print(f"   Masofa: {calc['distance_km']} km")
    print(f"   Vaqt: {calc['duration_minutes']} daqiqa")
    print(f"\n   Tarkibi:")
    print(f"   - Boshlang'ich: {calc['breakdown']['base_fare']:,} so'm")
    print(f"   - Masofa: {calc['breakdown']['distance_cost']:,} so'm")
    print(f"   - Vaqt: {calc['breakdown']['time_cost']:,} so'm")
    print(f"\n   Umumiy: {calc['total_fare']:,} so'm")
    print(f"   Komissiya: {calc['commission_amount']:,} so'm ({calc['commission_rate'] * 100}%)")
    print(f"   Haydovchi daromadi: {calc['driver_earnings']:,} so'm")
    print(f"\n   Formula: {calc['formula']}")
    
    # Step 4: Update pricing (optional)
    print("\n4️⃣  Narxlarni yangilash (ixtiyoriy)...")
    update = input("\nNarxlarni yangilamoqchimisiz? (y/n): ").strip().lower()
    
    if update == 'y':
        vehicle_type = input("Mashina turi (economy/comfort/business): ").strip().lower()
        base_fare = float(input("Boshlang'ich narx (so'm): ").strip())
        per_km_rate = float(input("Har km narxi (so'm): ").strip())
        per_minute_rate = float(input("Har daqiqa narxi (so'm): ").strip())
        
        response = requests.put(
            f"{BASE_URL}/admin/pricing/{vehicle_type}",
            headers=headers,
            json={
                "vehicle_type": vehicle_type,
                "base_fare": base_fare,
                "per_km_rate": per_km_rate,
                "per_minute_rate": per_minute_rate
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Xato: {response.json()}")
            return
        
        result = response.json()
        print(f"\n✅ {result['message']}")
        print(f"   Yangi narxlar:")
        print(f"   - Boshlang'ich: {result['pricing']['base_fare']:,} so'm")
        print(f"   - Har km: {result['pricing']['per_km_rate']:,} so'm")
        print(f"   - Har daqiqa: {result['pricing']['per_minute_rate']:,} so'm")
    
    print("\n" + "=" * 60)
    print("✅ Test Yakunlandi!")
    print("=" * 60)

if __name__ == "__main__":
    test_admin_pricing()
