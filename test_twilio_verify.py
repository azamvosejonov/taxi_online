"""
Test Twilio Verify service for OTP
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.sms_service import sms_service

def test_twilio_verify():
    """Test Twilio Verify service"""
    print("=" * 60)
    print("Testing Twilio Verify Service")
    print("=" * 60)
    
    # Check if SMS service is enabled
    if not sms_service.enabled:
        print("❌ SMS service is DISABLED")
        print("   Please check your .env file:")
        print("   - TWILIO_ENABLED should be 'true'")
        print("   - TWILIO_ACCOUNT_SID should be set")
        print("   - TWILIO_AUTH_TOKEN should be set")
        return False
    
    print(f"✅ SMS service is ENABLED")
    
    # Check if Verify mode is enabled
    if not sms_service.use_verify:
        print("❌ Twilio Verify mode is DISABLED")
        print("   Set TWILIO_USE_VERIFY=true in .env file")
        return False
    
    print(f"✅ Twilio Verify mode is ENABLED")
    print(f"   Verify Service SID: {sms_service.verify_service_sid}")
    print()
    
    # Test sending OTP via Verify
    test_phone = input("Enter phone number to test (e.g., +998901234567): ").strip()
    if not test_phone:
        test_phone = "+998901234567"
    
    print(f"\n📱 Sending OTP via Twilio Verify to {test_phone}...")
    success, info = sms_service.send_otp_via_verify(test_phone)
    
    if success:
        print(f"✅ OTP sent successfully via Twilio Verify!")
        print(f"   Status: {info}")
        print(f"\n🔐 Check your phone for the OTP code")
        
        # Test verification
        otp_code = input("\nEnter the OTP code received: ").strip()
        if otp_code:
            print(f"\n🔍 Verifying OTP code...")
            approved, status = sms_service.verify_code_via_verify(test_phone, otp_code)
            
            if approved:
                print(f"✅ OTP verified successfully!")
                print(f"   Status: {status}")
                return True
            else:
                print(f"❌ OTP verification failed")
                print(f"   Status: {status}")
                return False
    else:
        print(f"❌ Failed to send OTP via Twilio Verify")
        print(f"   Check Twilio dashboard for errors")
        print(f"\n💡 Common issues:")
        print(f"   - Verify Service SID might be incorrect")
        print(f"   - Phone number format must be E.164 (e.g., +998901234567)")
        print(f"   - Twilio account may need verification or credits")
        return False

if __name__ == "__main__":
    test_twilio_verify()
