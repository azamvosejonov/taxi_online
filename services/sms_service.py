"""
SMS Service for sending OTP codes via Twilio
"""
import logging
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS messages via Twilio"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.enabled = settings.twilio_enabled
        
        if self.enabled:
            if not settings.twilio_account_sid or not settings.twilio_auth_token:
                logger.warning("Twilio credentials not configured. SMS sending disabled.")
                self.enabled = False
                self.client = None
            else:
                try:
                    self.client = Client(
                        settings.twilio_account_sid,
                        settings.twilio_auth_token
                    )
                    self.from_number = settings.twilio_phone_number
                    logger.info("✅ Twilio SMS service initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Twilio client: {e}")
                    self.enabled = False
                    self.client = None
        else:
            self.client = None
            logger.info("Twilio SMS service disabled (TWILIO_ENABLED=false)")
    
    def send_otp(self, phone: str, otp_code: str) -> tuple[bool, Optional[str]]:
        """
        Send OTP code to phone number via SMS
        
        Args:
            phone: Phone number in international format (+998XXXXXXXXX)
            otp_code: 6-digit OTP code
            
        Returns:
            tuple: (success: bool, message_sid: Optional[str])
        """
        if not self.enabled or not self.client:
            logger.warning(f"SMS sending disabled. OTP for {phone}: {otp_code}")
            return False, None
        
        try:
            # Create SMS message
            message_body = (
                f"Royal Taxi tasdiqlash kodi: {otp_code}\n"
                f"Kod 5 daqiqa davomida amal qiladi.\n"
                f"Agar siz bu kodni so'ramagan bo'lsangiz, bu xabarni e'tiborsiz qoldiring."
            )
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=phone
            )
            
            logger.info(f"✅ SMS sent successfully to {phone}. SID: {message.sid}")
            return True, message.sid
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {phone}: {e.msg} (Code: {e.code})")
            return False, None
            
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {phone}: {str(e)}")
            return False, None
    
    def send_custom_message(self, phone: str, message: str) -> tuple[bool, Optional[str]]:
        """
        Send custom SMS message
        
        Args:
            phone: Phone number in international format
            message: Message text
            
        Returns:
            tuple: (success: bool, message_sid: Optional[str])
        """
        if not self.enabled or not self.client:
            logger.warning(f"SMS sending disabled. Message for {phone}: {message}")
            return False, None
        
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone
            )
            
            logger.info(f"✅ Custom SMS sent to {phone}. SID: {msg.sid}")
            return True, msg.sid
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending custom SMS to {phone}: {e.msg}")
            return False, None
            
        except Exception as e:
            logger.error(f"Error sending custom SMS to {phone}: {str(e)}")
            return False, None


# Global SMS service instance
sms_service = SMSService()
