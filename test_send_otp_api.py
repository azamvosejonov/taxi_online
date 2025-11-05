"""
Test send-otp API endpoint with real SMS sending via Twilio
"""
import requests
import json

# API configuration
BASE_URL = "http://localhost:8080/api/v1"

def test_send_otp():
    """Test POST /api/v1/auth/send-otp endpoint"""
    
    print("=" * 70)
    print("📱 Testing SMS OTP Sending via API")
    print("=" * 70)
    print()
    
    # Get phone number from user
    phone_number = input("Telefon raqamingizni kiriting (masalan: +998901234567): ").strip()
    
    if not phone_number:
        print("❌ Telefon raqam kiritilmadi!")
        return
    
    if not phone_number.startswith("+"):
        print("⚠️  Telefon raqam + belgisidan boshlanishi kerak!")
        phone_number = "+" + phone_number
    
    print(f"\n📤 SMS yuborish so'rovi yuborilmoqda...")
    print(f"   Endpoint: {BASE_URL}/auth/send-otp")
    print(f"   Phone: {phone_number}")
    print()
    
    # Send OTP request
    try:
        response = requests.post(
            f"{BASE_URL}/auth/send-otp",
            json={"phone": phone_number},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Body:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        
        if response.status_code == 200:
            print("✅ SMS yuborish so'rovi muvaffaqiyatli!")
            print(f"💬 Iltimos, {phone_number} raqamiga kelgan SMS ni tekshiring.")
            print(f"⏰ Kod 5 daqiqa davomida amal qiladi.")
            print()
            
            # Test verification
            test_verify = input("Tasdiqlash kodini tekshirishni xohlaysizmi? (y/n): ").strip().lower()
            
            if test_verify == 'y':
                otp_code = input("\n🔑 SMS orqali kelgan 6 raqamli kodni kiriting: ").strip()
                
                if otp_code:
                    print(f"\n🔍 Tasdiqlash kodi tekshirilmoqda...")
                    
                    verify_response = requests.post(
                        f"{BASE_URL}/auth/verify-otp",
                        json={
                            "phone": phone_number,
                            "otp_code": otp_code
                        },
                        headers={"Content-Type": "application/json"}
                    )
                    
                    print(f"📊 Verify Response Status: {verify_response.status_code}")
                    print(f"📊 Verify Response Body:")
                    print(json.dumps(verify_response.json(), indent=2, ensure_ascii=False))
                    print()
                    
                    if verify_response.status_code == 200:
                        print("✅ Tasdiqlash kodi to'g'ri! Telefon raqam tasdiqlandi.")
                    else:
                        print("❌ Tasdiqlash kodi noto'g'ri yoki muddati tugagan.")
            
            return True
        else:
            print("❌ SMS yuborishda xatolik!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Servergasms ulanib bo'lmadi!")
        print("   Iltimos, API serverni ishga tushiring:")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False

def main():
    """Main function"""
    print()
    print("🚕 Royal Taxi - SMS OTP Test")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL.rsplit('/api/v1', 1)[0]}/docs", timeout=2)
        print("✅ API server ishlamoqda")
        print()
    except:
        print("⚠️  API server ishlamayotgan ko'rinadi")
        print("   Iltimos, serverni ishga tushiring:")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print()
        choice = input("Davom etishni xohlaysizmi? (y/n): ").strip().lower()
        if choice != 'y':
            return
        print()
    
    test_send_otp()

if __name__ == "__main__":
    main()
