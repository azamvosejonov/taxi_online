"""
Debug Twilio configuration and test connection
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from twilio.rest import Client
from config import settings

def debug_twilio():
    """Debug Twilio configuration"""
    print("=" * 70)
    print("🔍 Twilio Konfiguratsiya Tekshiruvi")
    print("=" * 70)
    print()
    
    # Check if Twilio is enabled
    print(f"1️⃣  TWILIO_ENABLED: {settings.twilio_enabled}")
    print(f"2️⃣  TWILIO_USE_VERIFY: {settings.twilio_use_verify}")
    print()
    
    # Check credentials
    print("3️⃣  Twilio Credentials:")
    print(f"   Account SID: {settings.twilio_account_sid[:20]}..." if settings.twilio_account_sid else "   ❌ Account SID yo'q")
    print(f"   Auth Token: {settings.twilio_auth_token[:10]}..." if settings.twilio_auth_token else "   ❌ Auth Token yo'q")
    print(f"   Verify Service SID: {settings.twilio_verify_service_sid[:20]}..." if settings.twilio_verify_service_sid else "   ❌ Verify Service SID yo'q")
    print()
    
    if not settings.twilio_enabled:
        print("❌ Twilio o'chirilgan. .env faylda TWILIO_ENABLED=true qiling")
        return
    
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        print("❌ Twilio credentials to'liq emas")
        return
    
    # Test Twilio connection
    print("4️⃣  Twilio Server ga ulanish...")
    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        # Get account info
        account = client.api.accounts(settings.twilio_account_sid).fetch()
        print(f"   ✅ Ulanish muvaffaqiyatli!")
        print(f"   Account Name: {account.friendly_name}")
        print(f"   Account Status: {account.status}")
        print(f"   Account Type: {account.type}")
        print()
        
        # Check Verify Service
        if settings.twilio_use_verify:
            print("5️⃣  Twilio Verify Service tekshiruvi...")
            if not settings.twilio_verify_service_sid:
                print("   ❌ TWILIO_VERIFY_SERVICE_SID yo'q")
                return
            
            try:
                service = client.verify.v2.services(settings.twilio_verify_service_sid).fetch()
                print(f"   ✅ Verify Service topildi!")
                print(f"   Service Name: {service.friendly_name}")
                print(f"   Service SID: {service.sid}")
                print()
                
                # Test sending verification
                print("6️⃣  Test SMS yuborish...")
                test_phone = input("   Test telefon raqamingizni kiriting (+998...): ").strip()
                
                if test_phone:
                    print(f"   📤 {test_phone} ga SMS yuborilmoqda...")
                    try:
                        verification = client.verify.v2.services(
                            settings.twilio_verify_service_sid
                        ).verifications.create(
                            to=test_phone,
                            channel='sms'
                        )
                        print(f"   ✅ SMS yuborildi!")
                        print(f"   Status: {verification.status}")
                        print(f"   Valid: {verification.valid}")
                        print()
                        print("   📱 Telefoningizni tekshiring!")
                        print()
                        
                        # Test verification
                        otp = input("   Kelgan kodni kiriting: ").strip()
                        if otp:
                            check = client.verify.v2.services(
                                settings.twilio_verify_service_sid
                            ).verification_checks.create(
                                to=test_phone,
                                code=otp
                            )
                            print(f"   Verification Status: {check.status}")
                            if check.status == "approved":
                                print("   ✅ Kod to'g'ri!")
                            else:
                                print("   ❌ Kod noto'g'ri")
                        
                    except Exception as e:
                        print(f"   ❌ Xatolik: {e}")
                        print()
                        print("   💡 Mumkin bo'lgan sabablar:")
                        print("   - Twilio trial hisobda raqam tasdiqlanmagan")
                        print("   - Telefon raqam formati noto'g'ri (E.164: +998...)")
                        print("   - Twilio hisobda kredit yetarli emas")
                        print("   - Verify Service noto'g'ri sozlangan")
                        print()
                        print("   🔗 Twilio Console: https://console.twilio.com")
                        print("   📞 Verified Numbers: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
                        
            except Exception as e:
                print(f"   ❌ Verify Service topilmadi: {e}")
                print()
                print("   💡 Yechim:")
                print("   1. Twilio Console ga kiring: https://console.twilio.com")
                print("   2. Verify > Services ga o'ting")
                print("   3. Yangi Service yarating yoki mavjud Service SID ni ko'chiring")
                print("   4. .env faylda TWILIO_VERIFY_SERVICE_SID ni yangilang")
        else:
            print("5️⃣  Twilio Verify o'chirilgan")
            print("   .env faylda TWILIO_USE_VERIFY=true qiling")
        
    except Exception as e:
        print(f"   ❌ Ulanish xatosi: {e}")
        print()
        print("   💡 Mumkin bo'lgan sabablar:")
        print("   - Account SID yoki Auth Token noto'g'ri")
        print("   - Internet aloqasi yo'q")
        print("   - Twilio server muammosi")

if __name__ == "__main__":
    debug_twilio()
