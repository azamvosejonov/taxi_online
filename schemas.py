"""
Pydantic schemas for request/response models
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
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
    ENGLISH = "en"

# Location schema
class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    address: str = Field(..., min_length=1, description="Address string")
    city: Optional[str] = Field(None, description="City/Region name")

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+998\d{9}$", description="Uzbekistan phone number format")
    full_name: str = Field(..., min_length=2, max_length=100)
    language: Language = Language.UZBEK

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    is_driver: bool = False
    is_admin: bool = False
    emergency_contact: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    vehicle_number: Optional[str] = None
    license_number: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+998\d{9}$")
    language: Optional[Language] = None
    emergency_contact: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    vehicle_number: Optional[str] = None
    license_number: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    profile_photo: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    phone: str
    full_name: str
    profile_photo: Optional[str] = None
    is_driver: bool
    is_admin: bool
    is_active: bool
    language: str
    emergency_contact: Optional[str]
    rating: float
    total_rides: int
    current_balance: float
    required_deposit: float
    is_approved: bool
    vehicle_type: Optional[str]
    vehicle_number: Optional[str]
    license_number: Optional[str]
    vehicle_model: Optional[str]
    vehicle_color: Optional[str]
    created_at: datetime

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

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
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

# Authentication schemas
class UserLogin(BaseModel):
    username: str  # Can be email or phone
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
