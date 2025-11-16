"""
Pydantic schemas for request/response models
"""
from datetime import date, datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

# Enums
class UserRole(str, Enum):
    RIDER = "rider"
    DRIVER = "driver"
    ADMIN = "admin"

class RideStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CARD = "card"
    WALLET = "wallet"
    CASH = "cash"

class VehicleType(str, Enum):
    ECONOMY = "economy"
    COMFORT = "comfort"
    BUSINESS = "business"
    VIP = "vip"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    COMMISSION = "commission"
    REFUND = "refund"

class Language(str, Enum):
    UZBEK = "uz"
    RUSSIAN = "ru"

# Location schema
class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    address: str = Field(..., min_length=1, max_length=100, description="Address string")
    city: Optional[str] = Field(None, description="City/Region name")

# First step of registration (basic info)
class UserRegister(BaseModel):
    """User registration request model"""
    phone: str = Field(
        ...,
        example="+998901234567",
        pattern=r"^\+998\d{9}$",
        description="O'zbekiston telefon raqami formati (+998XXXXXXXXX)"
    )
    first_name: str = Field(
        ...,
        example="Falonchi",
        min_length=2,
        max_length=50,
        description="Foydalanuvchi ismi"
    )
    last_name: str = Field(
        ...,
        example="Falonchiyev",
        min_length=2,
        max_length=50,
        description="Foydalanuvchi familiyasi"
    )
    password: str = Field(
        ...,
        example="strongpassword123",
        min_length=6,
        max_length=100,
        description="Parol (kamida 6 ta belgi)"
    )
    gender: str = Field(
        ...,
        example="Erkak",
        description="Jinsi (Erkak/Ayol)"
    )
    date_of_birth: date = Field(
        ...,
        example="1990-01-01",
        description="Tug'ilgan sana (YYYY-MM-DD)"
    )
    vehicle_make: str = Field(
        ...,
        example="Chevrolet",
        description="Avtomobil markasi"
    )
    vehicle_color: str = Field(
        ...,
        example="Qora",
        description="Avtomobil rangi"
    )
    position: str = Field(
        ...,
        example="Haydovchi",
        description="Pozitsiya"
    )
    license_plate: str = Field(
        ...,
        example="01A123AA",
        description="Davlat raqami"
    )
    tech_passport: str = Field(
        ...,
        example="AA1234567",
        description="Texpassport raqami"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+998901234567",
                "first_name": "Falonchi",
                "last_name": "Falonchiyev",
                "password": "strongpassword123",
                "gender": "Erkak",
                "date_of_birth": "1990-01-01",
                "vehicle_make": "Chevrolet",
                "vehicle_color": "Qora",
                "position": "Haydovchi",
                "license_plate": "01A123AA",
                "tech_passport": "AA1234567"
            }
        }

# Second step of registration (driver details)
class DriverDetails(BaseModel):
    vehicle_make: str = Field(..., description="Avtomobil markasi")
    vehicle_color: str = Field(..., description="Avtomobil rangi")
    position: str = Field(..., description="Pozitsiya")
    license_plate: str = Field(..., description="Davlat raqami")
    tech_passport: str = Field(..., description="Texpassport raqami")

class UserBase(BaseModel):
    phone: str = Field(..., pattern=r"^\+998\d{9}$", description="O'zbekiston telefon raqami formati")
    first_name: str = Field(..., min_length=2, max_length=50, description="Ism")
    last_name: str = Field(..., min_length=2, max_length=50, description="Familiya")
    gender: Optional[str] = Field(None, description="Jinsi")
    date_of_birth: Optional[date] = Field(None, description="Tug'ilgan sanasi (YYYY-MM-DD)")
    language: Language = Language.UZBEK
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    is_driver: bool = False
    is_admin: bool = False
    emergency_contact: Optional[str] = None
    
    # Driver-specific fields
    vehicle_type: Optional[VehicleType] = None
    vehicle_make: Optional[str] = Field(None, description="Avtomobil markasi")
    vehicle_model: Optional[str] = Field(None, description="Avtomobil modeli")
    vehicle_color: Optional[str] = Field(None, description="Avtomobil rangi")
    license_plate: Optional[str] = Field(None, description="Davlat raqami")
    tech_passport: Optional[str] = Field(None, description="Texpassport raqami")
    license_number: Optional[str] = Field(None, description="Haydovchilik guvohnomasi raqami")
    position: Optional[str] = Field(None, description="Pozitsiya")

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+998\d{9}$")
    language: Optional[Language] = None
    emergency_contact: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    vehicle_number: Optional[str] = None
    license_number: Optional[str] = None
    vehicle_model: Optional[str] = None
    profile_photo: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    phone: str
    full_name: str
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    profile_photo: Optional[str] = None
    is_driver: bool
    is_dispatcher: bool = False
    is_admin: bool = False
    is_active: bool
    language: str = "uz"
    emergency_contact: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    license_plate: Optional[str] = None
    tech_passport: Optional[str] = None
    license_number: Optional[str] = None
    position: Optional[str] = None
    rating: Optional[float]
    total_rides: int
    current_balance: float
    required_deposit: float
    is_approved: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime] = None
    current_location: Optional[Dict[str, float]] = None
    city: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        
    def __init__(self, **data):
        # Handle legacy data where first_name and last_name might be provided
        if 'full_name' not in data and 'first_name' in data and 'last_name' in data:
            data['full_name'] = f"{data['first_name']} {data['last_name']}"
        
        # Map legacy output fields from new model attributes if present
        if 'vehicle_make' not in data and 'vehicle_model' in data and data.get('vehicle_make') is None:
            data['vehicle_make'] = data.get('vehicle_model')
        if 'license_plate' not in data and 'vehicle_number' in data and data.get('license_plate') is None:
            data['license_plate'] = data.get('vehicle_number')
        if 'tech_passport' not in data and 'license_number' in data and data.get('tech_passport') is None:
            data['tech_passport'] = data.get('license_number')

        # Convert None boolean values to False
        for field in ['is_driver', 'is_dispatcher', 'is_admin', 'is_active', 'is_approved']:
            if field in data and data[field] is None:
                data[field] = False
        
        super().__init__(**data)

# Ride schemas
class RideCreate(BaseModel):
    customer_phone: str = Field(..., pattern=r"^\+998\d{9}$", description="Customer's phone number")
    customer_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Customer's name")
    pickup_location: Location
    dropoff_location: Location
    vehicle_type: VehicleType = VehicleType.ECONOMY
    estimated_distance: Optional[float] = None
    estimated_duration: Optional[int] = None

class RideUpdate(BaseModel):
    status: RideStatus

class LocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class RideResponse(BaseModel):
    id: int
    customer_id: int
    rider_id: Optional[int]
    driver_id: Optional[int]
    customer: Optional['CustomerResponse'] = None  # Using string literal to avoid circular import
    pickup_location: Dict[str, Any]
    dropoff_location: Dict[str, Any]
    current_location: Optional[Dict[str, Any]]
    status: str
    fare: float
    distance: float
    duration: int
    vehicle_type: str
    route_geometry: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime]

# Payment schemas
class PaymentCreate(BaseModel):
    payment_method: PaymentMethod

class PaymentResponse(BaseModel):
    id: int
    ride_id: int
    amount: float
    currency: str
    status: str
    payment_method: str
    transaction_id: Optional[str]
    created_at: datetime

# Transaction schemas
class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    transaction_type: str
    description: str
    ride_id: Optional[int]
    created_at: datetime

# Message schemas
class MessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

class MessageResponse(BaseModel):
    id: int
    ride_id: int
    sender_id: int
    message: str
    is_read: bool
    created_at: datetime

# Rating schemas
class ReviewCreate(BaseModel):
    ride_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=500, description="Optional review text")
    review_type: str = Field(..., description="driver_review or passenger_review")

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Updated rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=500, description="Updated review text")
    is_helpful: Optional[bool] = Field(None, description="Mark if the review was helpful")

class ReviewResponse(BaseModel):
    id: int
    ride_id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    review_text: Optional[str]
    review_type: str
    is_helpful: int
    created_at: datetime

class RatingCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = None

# Dispatcher/Driver flow schemas
class DriverStatusUpdate(BaseModel):
    is_on_duty: bool
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    city: Optional[str] = None

class DispatchOrderCreate(BaseModel):
    customer_phone: str = Field(..., pattern=r"^\+998\d{9}$")
    customer_name: Optional[str] = Field(None, min_length=1, max_length=100)
    pickup_location: Location
    dropoff_location: Location
    vehicle_type: VehicleType = VehicleType.ECONOMY

class DispatchOrderResponse(BaseModel):
    ride: RideResponse
    broadcasted_to: int

class DepositRequest(BaseModel):
    driver_id: int
    amount: float = Field(..., gt=0)

class BroadcastRequest(BaseModel):
    radius_km: Optional[float] = Field(3.0, gt=0, description="Search radius in km for nearby drivers")

class CompleteRideRequest(BaseModel):
    dropoff_location: Optional[Location] = None
    final_fare: Optional[float] = Field(None, gt=0)

class AdminNotifyRequest(BaseModel):
    title: str
    body: str

# Pricing schemas
class VehicleTypePrice(BaseModel):
    """Vehicle type pricing configuration"""
    vehicle_type: str = Field(..., description="Vehicle type: economy, comfort, business")
    base_fare: float = Field(..., gt=0, description="Boshlang'ich narx (so'm)")
    per_km_rate: float = Field(..., gt=0, description="Har km uchun narx (so'm)")
    per_minute_rate: float = Field(..., gt=0, description="Har daqiqa uchun narx (so'm)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_type": "economy",
                "base_fare": 10000,
                "per_km_rate": 2000,
                "per_minute_rate": 500
            }
        }

class PricingConfigResponse(BaseModel):
    """Response with all pricing configurations"""
    economy: Dict[str, Any]
    comfort: Dict[str, Any]
    business: Dict[str, Any]
    commission_rate: float

# Authentication schemas
class UserLogin(BaseModel):
    """Schema for user login"""
    phone: str = Field(..., pattern=r"^\+998\d{9}$", description="O'zbekiston telefon raqami formati")
    password: str = Field(..., min_length=6, description="Parol (kamida 6 ta belgi)")

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 604800  # 7 days in seconds
    user: Dict[str, Any]
    token: str  # Alias for access_token for backward compatibility
    accessToken: str  # Alias for access_token for mobile app compatibility
    authorization: str  # Full Authorization header value
    security: Dict[str, Dict[str, str]]  # For Swagger UI

class TokenData(BaseModel):
    """Schema for JWT token data"""
    email: Optional[str] = None

# Analytics schemas
class DailyAnalytics(BaseModel):
    date: str
    total_rides: int
    completed_rides: int
    cancelled_rides: int
    total_revenue: float
    new_users: int
    driver_approvals: int
    average_ride_distance: float
    average_ride_fare: float

class WeeklyAnalytics(BaseModel):
    total_rides: int
    completed_rides: int
    total_revenue: float
    daily_breakdown: Dict[str, Any]

class SystemStats(BaseModel):
    total_users: int
    total_drivers: int
    total_rides: int
    completed_rides: int
    total_revenue: float

# File upload schemas
class ProfilePictureUpload(BaseModel):
    file_path: str
    message: str

class DocumentUpload(BaseModel):
    uploaded_files: Dict[str, str]
    message: str

# Notification schemas
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    body: str
    notification_type: str
    data: Optional[str]
    is_read: bool
    created_at: datetime

# FCM Token schemas
class FCMTokenRegister(BaseModel):
    token: str
    device_type: str = "web"

class FCMTokenResponse(BaseModel):
    message: str

# Promo code schemas
class PromoCodeResponse(BaseModel):
    id: int
    code: str
    discount_type: str
    discount_value: float
    max_uses: int
    used_count: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    description: Optional[str]
    created_at: datetime

# Vehicle schemas
class VehicleResponse(BaseModel):
    id: int
    driver_id: int
    make: str
    model: str
    year: int
    color: str
    license_plate: str
    vehicle_type: str
    capacity: int
    has_air_conditioning: bool
    has_wifi: bool
    has_gps: bool
    has_child_seat: bool
    has_pet_friendly: bool
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

# WebSocket message schemas
class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]

class WSRideUpdate(WSMessage):
    ride_id: int
    old_status: Optional[str]
    new_status: str

class WSLocationUpdate(WSMessage):
    ride_id: int
    location: Dict[str, float]

class WSCommissionUpdate(WSMessage):
    ride_id: int
    commission: float
    remaining_balance: float

# Pagination schemas
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# Customer schemas
class CustomerBase(BaseModel):
    phone: str = Field(..., pattern=r"^\+998\d{9}$", description="Uzbekistan phone number format")
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)

class CustomerResponse(CustomerBase):
    id: int
    total_rides: int
    created_at: datetime
    last_ride_at: Optional[datetime]

    class Config:
        from_attributes = True

# OTP Authentication schemas
class SendOTPRequest(BaseModel):
    """Request to send OTP to phone number"""
    phone: str = Field(..., pattern=r"^\+998\d{9}$", description="O'zbekiston telefon raqami formati (+998XXXXXXXXX)")

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+998901234567"
            }
        }

class VerifyOTPRequest(BaseModel):
    """Request to verify OTP code"""
    phone: str = Field(..., pattern=r"^\+998\d{9}$", description="O'zbekiston telefon raqami formati")
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$", description="6 raqamli tasdiqlash kodi")

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+998901234567",
                "otp_code": "123456"
            }
        }

class CompleteProfileRequest(BaseModel):
    """Request to complete user profile after OTP verification"""
    phone: str = Field(..., pattern=r"^\+998\d{9}$", description="O'zbekiston telefon raqami formati")
    password: str = Field(..., min_length=6, max_length=100, description="Parol (kamida 6 ta belgi)")
    first_name: str = Field(..., min_length=2, max_length=50, description="Ism")
    last_name: str = Field(..., min_length=2, max_length=50, description="Familiya")
    gender: str = Field(..., description="Jinsi (Erkak/Ayol)")
    date_of_birth: date = Field(..., description="Tug'ilgan sana (YYYY-MM-DD)")
    vehicle_make: str = Field(..., description="Avtomobil markasi")
    vehicle_color: str = Field(..., description="Avtomobil rangi")
    position: str = Field(..., description="Pozitsiya")
    license_plate: str = Field(..., description="Davlat raqami")
    tech_passport: str = Field(..., description="Texpassport raqami")

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+998901234567",
                "password": "parolim123",
                "first_name": "Falonchi",
                "last_name": "Falonchiyev",
                "gender": "Erkak",
                "date_of_birth": "1990-01-01",
                "vehicle_make": "Chevrolet",
                "vehicle_color": "Qora",
                "position": "Haydovchi",
                "license_plate": "01A123AA",
                "tech_passport": "AA1234567"
            }
        }

class OTPResponse(BaseModel):
    """Response after sending OTP"""
    message: str
    phone: str
    expires_in: int  # seconds
    otp_code: Optional[str] = None  # Only for development/testing

class VerifyOTPResponse(BaseModel):
    """Response after verifying OTP"""
    message: str
    phone: str
    verified: bool
    needs_profile_completion: bool

# Authentication schemas
class UserLogin(BaseModel):
    phone: str = Field(..., pattern=r"^\+998\d{9}$", description="Uzbekistan phone number format")
    password: str

class MonthlyAnalytics(BaseModel):
    month: str  # YYYY-MM format
    total_rides: int
    completed_rides: int
    average_daily_revenue: float
    new_users: int
    driver_approvals: int
    daily_breakdown: Dict[str, Any]

class YearlyAnalytics(BaseModel):
    year: str  # YYYY format
    total_rides: int
    completed_rides: int
    total_revenue: float
    average_monthly_revenue: float
    monthly_breakdown: Dict[str, Any]
    growth_rate: float  # Percentage growth from previous year

class IncomeStats(BaseModel):
    total_revenue: float
    today_revenue: float
    month_revenue: float
    year_revenue: float
    average_daily_revenue: float
    average_monthly_revenue: float
    top_earning_days: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]  # Last 30 days trend

# ============= ADDITIONAL SERVICES (Qo'shimcha xizmatlar) =============

class AdditionalServiceCreate(BaseModel):
    """Qo'shimcha xizmat yaratish"""
    name: str = Field(..., example="konditsioner", description="Xizmat nomi (unique)")
    name_uz: str = Field(..., example="Konditsioner", description="O'zbekcha nomi")
    name_ru: Optional[str] = Field(None, example="Кондиционер", description="Ruscha nomi")
    icon: Optional[str] = Field(None, example="❄️", description="Icon (emoji yoki URL)")
    price: float = Field(..., ge=0, example=5000.0, description="Narxi (UZS)")
    is_active: bool = Field(True, description="Faol/Faol emas")
    display_order: int = Field(0, ge=0, description="Ko'rsatish tartibi")
    description: Optional[str] = Field(None, example="Avtomobilni sovutish", description="Tavsif")

class AdditionalServiceUpdate(BaseModel):
    """Qo'shimcha xizmatni yangilash"""
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    icon: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None

class AdditionalServiceResponse(BaseModel):
    """Qo'shimcha xizmat response"""
    id: int
    name: str
    name_uz: str
    name_ru: Optional[str]
    icon: Optional[str]
    price: float
    is_active: bool
    display_order: int
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AdditionalServiceToggle(BaseModel):
    """Xizmatni faollashtirish/o'chirish"""
    is_active: bool = Field(..., description="Faol/Faol emas")
