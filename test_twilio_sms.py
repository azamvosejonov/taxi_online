"""
Test script for Twilio SMS integration
"""
import os
from services.sms_service import sms_service

def test_twilio_connection():
    """Test Twilio connection and configuration"""
    print("=" * 60)
    print("Twilio SMS Service Test")
    print("=" * 60)
    
    # Check if Twilio is enabled
    print(f"\n1. Twilio Enabled: {sms_service.enabled}")
    
    if not sms_service.enabled:
        print("\n⚠️  Twilio is disabled. Set TWILIO_ENABLED=true in .env file")
        print("\nTo enable Twilio:")
        print("1. Open .env file")
        print("2. Set TWILIO_ENABLED=true")
        print("3. Add your Twilio credentials:")
        print("   - TWILIO_ACCOUNT_SID")
        print("   - TWILIO_AUTH_TOKEN")
        print("   - TWILIO_PHONE_NUMBER")
        return
    
    # Check Twilio client
    if sms_service.client:
        print("✅ Twilio client initialized successfully")
        print(f"   From Number: {sms_service.from_number}")
    else:
        print("❌ Twilio client not initialized")
        return
    
    # Test sending SMS
    print("\n2. Testing SMS sending...")
    test_phone = input("Enter test phone number (e.g., +998901234567): ").strip()
    
    if not test_phone:
        print("❌ No phone number provided")
        return
    
    test_otp = "123456"
    
    print(f"\n   Sending OTP {test_otp} to {test_phone}...")
    success, message_sid = sms_service.send_otp(test_phone, test_otp)
    
    if success:
        print(f"\n✅ SMS sent successfully!")
        print(f"   Message SID: {message_sid}")
        print(f"\n   Check your phone {test_phone} for the SMS")
    else:
        print(f"\n❌ Failed to send SMS to {test_phone}")
        print("\n   Possible reasons:")
        print("   1. Invalid phone number format")
        print("   2. Phone number not verified (for trial accounts)")
        print("   3. Insufficient balance")
        print("   4. Invalid Twilio credentials")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_twilio_connection()
