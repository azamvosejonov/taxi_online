"""
Test SMS sending with Twilio
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.sms_service import sms_service

def test_sms():
    """Test SMS sending"""
    print("=" * 60)
    print("Testing Twilio SMS Service")
    print("=" * 60)
    
    # Check if SMS service is enabled
    if not sms_service.enabled:
        print("❌ SMS service is DISABLED")
        print("   Please check your .env file:")
        print("   - TWILIO_ENABLED should be 'true'")
        print("   - TWILIO_ACCOUNT_SID should be set")
        print("   - TWILIO_AUTH_TOKEN should be set")
        print("   - TWILIO_PHONE_NUMBER should be set")
        return False
    
    print(f"✅ SMS service is ENABLED")
    print(f"   From number: {sms_service.from_number}")
    print()
    
    # Test sending OTP
    test_phone = "+998901234567"  # Replace with your test number
    test_otp = "123456"
    
    print(f"📱 Sending test OTP to {test_phone}...")
    success, message_sid = sms_service.send_otp(test_phone, test_otp)
    
    if success:
        print(f"✅ SMS sent successfully!")
        print(f"   Message SID: {message_sid}")
        print(f"   OTP Code: {test_otp}")
        return True
    else:
        print(f"❌ Failed to send SMS")
        print(f"   Check Twilio dashboard for errors")
        return False

if __name__ == "__main__":
    test_sms()
