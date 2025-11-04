"""
Utility functions for Royal Taxi backend
"""
import json
import random
import string
import math
import os
import requests
import aiofiles
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, BinaryIO
from pathlib import Path
from jose import jwt
from passlib.context import CryptContext
from fastapi import UploadFile, HTTPException
from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Generate password hash using bcrypt"""
    return pwd_context.hash(password)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371.0
    
    return c * r


def calculate_fare(distance: float, duration: int, vehicle_type: str = "economy") -> float:
    """
    Calculate ride fare based on distance, duration and vehicle type
    """
    vehicle_config = settings.vehicle_types.get(vehicle_type, settings.vehicle_types["economy"])

    base_fare = vehicle_config["base_fare"]
    per_km_rate = vehicle_config["per_km_rate"]
    per_minute_rate = vehicle_config["per_minute_rate"]

    distance_fare = distance * per_km_rate
    time_fare = duration * per_minute_rate

    return base_fare + distance_fare + time_fare


def estimate_duration(distance: float, average_speed: float = 30.0) -> int:
    """
    Estimate ride duration in minutes based on distance and average speed
    """
    if distance <= 0:
        return 15  # Minimum 15 minutes for short rides

    # Convert speed from km/h to km/min
    speed_km_per_min = average_speed / 60
    duration = distance / speed_km_per_min

    return max(15, int(duration))  # Minimum 15 minutes


def generate_transaction_id() -> str:
    """Generate a unique transaction ID"""
    timestamp = str(int(datetime.utcnow().timestamp()))
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TXN{timestamp}{random_part}"


def validate_phone_number(phone: str) -> bool:
    """Validate Uzbekistan phone number format"""
    import re
    pattern = r"^\+998\d{9}$"
    return bool(re.match(pattern, phone))


def validate_vehicle_number(vehicle_number: str) -> bool:
    """Validate vehicle number format"""
    import re
    # Uzbekistan vehicle number format: 01A123AA, 10B456BB, etc.
    pattern = r"^\d{2}[A-Z]\d{3}[A-Z]{2}$"
    return bool(re.match(pattern, vehicle_number.upper()))


def validate_license_number(license_number: str) -> bool:
    """Validate driver's license number"""
    import re
    # Uzbekistan license format: 1234567, 12345678, etc.
    pattern = r"^\d{7,8}$"
    return bool(re.match(pattern, license_number))


def calculate_commission(fare: float, rate: float = None) -> float:
    """Calculate commission amount from ride fare"""
    if rate is None:
        rate = settings.commission_rate
    return fare * rate


def format_currency(amount: float, currency: str = "UZS") -> str:
    """Format amount as currency string"""
    return f"{amount:,.0f} {currency}"


def generate_cache_key(prefix: str, *args) -> str:
    """Generate cache key with prefix and arguments"""
    key_parts = [str(arg) for arg in args]
    return f"{prefix}:{':'.join(key_parts)}"


def parse_location(location_str: str) -> Dict[str, Any]:
    """Parse location JSON string to dictionary"""
    try:
        return json.loads(location_str)
    except (json.JSONDecodeError, TypeError):
        return {}


def format_location(location_dict: Dict[str, Any]) -> str:
    """Format location dictionary to JSON string"""
    return json.dumps(location_dict, ensure_ascii=False)


def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate latitude and longitude coordinates"""
    return -90 <= lat <= 90 and -180 <= lng <= 180


def generate_otp(length: int = 6) -> str:
    """Generate one-time password"""
    return ''.join(random.choices(string.digits, k=length))


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    from jose import jwt
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


async def save_upload_file(upload_file: UploadFile, folder: str = "general") -> str:
    """Save uploaded file and return file path"""
    # Use configurable upload directory; default to project ./uploads for local dev/tests
    try:
        base_dir = getattr(settings, 'upload_dir', None)
    except Exception:
        base_dir = None
    upload_base_dir = Path(base_dir) if base_dir else Path("./uploads")
    upload_dir = upload_base_dir / folder

    # Ensure directory exists (should already exist, but just in case)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_extension = Path(upload_file.filename).suffix.lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.allowed_extensions)}"
        )

    # Check file size
    file_size = 0
    content = await upload_file.read()
    file_size = len(content)

    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_file_size / (1024*1024):.1f}MB"
        )

    # Generate unique filename
    unique_filename = f"{int(datetime.utcnow().timestamp())}_{random.randint(1000, 9999)}{file_extension}"
    file_path = upload_dir / unique_filename

    # Save file
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    return f"/uploads/{folder}/{unique_filename}"


def paginate_query(query, page: int = 1, size: int = 20):
    """Apply pagination to SQLAlchemy query"""
    offset = (page - 1) * size
    return query.offset(offset).limit(size)


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat()


def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime from ISO string"""
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))


def calculate_driver_rating(current_rating: float, new_rating: int, total_rides: int) -> float:
    """Calculate updated driver rating"""
    if total_rides == 0:
        return float(new_rating)

    # Weighted average: 70% current rating, 30% new rating
    return (current_rating * 0.7) + (new_rating * 0.3)


def validate_email_domain(email: str) -> bool:
    """Validate email domain (basic check)"""
    import re
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def generate_ride_quote_cache_key(ride_data: Dict[str, Any]) -> str:
    """Generate cache key for ride quote"""
    # Create a hash of the ride data for caching
    data_str = json.dumps(ride_data, sort_keys=True)
    import hashlib
    data_hash = hashlib.md5(data_str.encode()).hexdigest()
    return f"ride_quote:{data_hash}"


def simulate_payment_success(payment_method: str) -> Tuple[bool, str]:
    """Simulate payment processing with different success rates"""
    success_rates = {
        "card": 0.95,      # 95% success rate for cards
        "wallet": 0.90,    # 90% success rate for digital wallets
        "cash": 1.0        # 100% success rate for cash (always successful)
    }

    success_rate = success_rates.get(payment_method, 0.85)  # Default 85%
    is_successful = random.random() < success_rate

    if is_successful:
        transaction_id = generate_transaction_id()
        return True, transaction_id
    else:
        return False, None


def calculate_estimated_fare(pickup: Dict[str, float], dropoff: Dict[str, float],
                           vehicle_type: str = "economy") -> Dict[str, float]:
    """Calculate estimated fare for a ride"""
    distance = calculate_distance(pickup["lat"], pickup["lng"], dropoff["lat"], dropoff["lng"])
    duration = estimate_duration(distance)
    fare = calculate_fare(distance, duration, vehicle_type)

    return {
        "distance": round(distance, 2),
        "duration": duration,
        "fare": round(fare, 2),
        "currency": "UZS"
    }


def validate_ride_request(ride_data: Dict[str, Any]) -> bool:
    """Validate ride request data"""
    required_fields = ["pickup_location", "dropoff_location"]

    for field in required_fields:
        if field not in ride_data:
            return False

    # Validate coordinates
    pickup = ride_data["pickup_location"]
    dropoff = ride_data["dropoff_location"]

    if not validate_coordinates(pickup["lat"], pickup["lng"]):
        return False

    if not validate_coordinates(dropoff["lat"], dropoff["lng"]):
        return False

    # Check if pickup and dropoff are too close (less than 100m)
    distance = calculate_distance(pickup["lat"], pickup["lng"], dropoff["lat"], dropoff["lng"])
    if distance < 0.1:  # 100 meters
        return False

    return True


def format_user_display_name(user) -> str:
    """Format user display name for notifications"""
    if user.full_name:
        return user.full_name
    elif user.phone:
        return user.phone[-4:]  # Last 4 digits of phone
    else:
        return f"User {user.id}"


def calculate_distance_fee(distance: float) -> float:
    """Calculate distance-based fee"""
    return distance * 2000  # 2000 som per km


def calculate_time_fee(duration: int) -> float:
    """Calculate time-based fee"""
    return duration * 500  # 500 som per minute


def get_vehicle_display_name(vehicle_type: str) -> str:
    """Get display name for vehicle type"""
    vehicle_config = settings.vehicle_types.get(vehicle_type, {})
    return language in settings.supported_languages


def format_phone_for_display(phone: str) -> str:
    """Format phone number for display"""
    if phone.startswith("+998"):
        return f"{phone[:4]} {phone[4:6]} {phone[6:9]}-{phone[9:]}"
    return phone


def generate_notification_id() -> str:
    """Generate unique notification ID"""
    return f"notif_{int(datetime.utcnow().timestamp())}_{random.randint(1000, 9999)}"


def validate_payment_amount(amount: float, min_amount: float = 1000) -> bool:
    """Validate payment amount"""
    return amount >= min_amount and amount <= 10000000  # Max 10M som


def get_current_week_start() -> datetime:
    """Get start of current week (Monday)"""
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    return start.replace(hour=0, minute=0, second=0, microsecond=0)


def get_current_month_start() -> datetime:
    """Get start of current month"""
    today = datetime.now()
    return today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_city_from_coordinates(lat: float, lng: float) -> str:
    """
    Get city name from coordinates (simplified for Uzbekistan cities)
    In production, this should use a proper geocoding service
    """
    # Uzbekistan major cities coordinates (approximate)
    uzbekistan_cities = {
        "toshkent": {"lat": 41.2995, "lng": 69.2401, "radius": 20},
        "samarqand": {"lat": 39.6270, "lng": 66.9749, "radius": 15},
        "buxoro": {"lat": 39.7749, "lng": 64.4286, "radius": 15},
        "andijon": {"lat": 40.7833, "lng": 72.3333, "radius": 15},
        "aim": {"lat": 40.8102, "lng": 72.7272, "radius": 10},
        "namangan": {"lat": 40.9983, "lng": 71.6726, "radius": 15},
        "fergana": {"lat": 40.3894, "lng": 71.7864, "radius": 15},
        "nukus": {"lat": 42.4667, "lng": 59.6000, "radius": 15},
        "urgench": {"lat": 41.5500, "lng": 60.6333, "radius": 15},
        "qarshi": {"lat": 38.8667, "lng": 65.8000, "radius": 15},
        "termiz": {"lat": 37.2333, "lng": 67.2833, "radius": 15}
    }

    closest_city = None
    min_distance = float('inf')

    for city, coords in uzbekistan_cities.items():
        distance = calculate_distance(lat, lng, coords["lat"], coords["lng"])
        if distance <= coords["radius"] and distance < min_distance:
            min_distance = distance
            closest_city = city

    return closest_city if closest_city else "unknown"


def is_within_andijon_region(lat: float, lng: float) -> bool:
    """
    Check if coordinates are within Andijon viloyati boundaries
    Approximate boundaries for Andijon region
    """
    # Andijon viloyati taxminiy chegaralari
    # North: 41.0, South: 40.5, East: 72.8, West: 71.8
    return (40.5 <= lat <= 41.0) and (71.8 <= lng <= 72.8)


def calculate_route_to_andijon(from_lat: float, from_lng: float) -> Dict[str, Any]:
    """
    Calculate route from any location to Andijon viloyati (Andijon city center)
    Only works for locations within Andijon region
    """
    # Check if the location is within Andijon region
    if not is_within_andijon_region(from_lat, from_lng):
        return {
            "error": "Bu joylashuv Andijon viloyati tashqarisida",
            "message": "Faqat Andijon viloyati ichidagi joylar uchun yo'l hisoblanadi",
            "location": {"lat": from_lat, "lng": from_lng}
        }

    andijon_center = {"lat": 40.7833, "lng": 72.3333}

    # Masofani hisoblash (km)
    distance = calculate_distance(from_lat, from_lng, andijon_center["lat"], andijon_center["lng"])

    # Taxminiy vaqt hisoblash (daqiqa)
    # Andijon viloyati ichida tezlik: 40-60 km/soat
    avg_speed = 50  # km/soat
    time_minutes = (distance / avg_speed) * 60

    # Yo'l turi aniqlash
    if distance <= 10:
        route_type = "shahar_ichi"
        route_desc = "Andijon shahri ichida"
    elif distance <= 50:
        route_type = "viloyat_ichi"
        route_desc = "Andijon viloyati ichida"
    else:
        route_type = "uzoq_viloyat_ichi"
        route_desc = "Andijon viloyati ichidagi uzoq masofa"

    # Taxminiy yo'l haqiqatini hisoblash
    base_fare = 8000  # Minimal yo'l haqi (viloyat ichida arzonroq)
    per_km_rate = 1500  # Har km uchun

    if distance > 3:  # 3km dan ko'p bo'lsa
        estimated_fare = base_fare + (distance * per_km_rate)
    else:
        estimated_fare = base_fare

    return {
        "distance_km": round(distance, 2),
        "time_minutes": max(5, int(time_minutes)),  # Minimal 5 daqiqa
        "route_type": route_type,
        "route_description": route_desc,
        "estimated_fare_uzs": int(estimated_fare),
        "andijon_center": andijon_center,
        "from_location": {"lat": from_lat, "lng": from_lng}
    }
