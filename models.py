from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class TimestampMixin(object):
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)  # Ism
    last_name = Column(String, nullable=False)   # Familiya
    full_name = Column(String, nullable=False)   # To'liq ism
    gender = Column(String, nullable=True)       # Jinsi
    date_of_birth = Column(DateTime, nullable=True)  # Tug'ilgan sana
    vehicle_make = Column(String, nullable=True)  # Avtomobil markasi
    vehicle_color = Column(String, nullable=True) # Avtomobil rangi
    position = Column(String, nullable=True)      # Pozitsiya
    license_plate = Column(String, nullable=True, unique=True)  # Davlat raqami
    tech_passport = Column(String, nullable=True, unique=True)  # Texpassport
    # System fields
    is_active = Column(Boolean, default=True)
    is_driver = Column(Boolean, default=True)  # All users are drivers by default
    is_dispatcher = Column(Boolean, default=False)  # Only set by admins
    is_admin = Column(Boolean, default=False)  # Only set by admins
    is_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # Admin who approved this user
    current_balance = Column(Float, default=0.0)  # Current wallet balance
    required_deposit = Column(Float, default=0.0)  # Required deposit for drivers
    rating = Column(Float, default=5.0)  # User rating
    total_rides = Column(Integer, default=0)  # Total number of rides
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Method to complete driver registration
    def complete_driver_registration(self, 
                                   vehicle_make: str, 
                                   vehicle_color: str, 
                                   position: str, 
                                   license_plate: str, 
                                   tech_passport: str):
        self.vehicle_make = vehicle_make
        self.vehicle_color = vehicle_color
        self.position = position
        self.license_plate = license_plate
        self.tech_passport = tech_passport
        self.is_driver = True
        self.updated_at = datetime.utcnow()
        
    # Relationships
    rides_as_rider = relationship("Ride", back_populates="rider", foreign_keys="Ride.rider_id")
    rides_as_driver = relationship("Ride", back_populates="driver", foreign_keys="Ride.driver_id")
    transactions = relationship("Transaction", back_populates="user")
    approved_admin = relationship("User", remote_side=[id], foreign_keys=[approved_by])
    notifications = relationship("Notification", back_populates="user")
    fcm_tokens = relationship("FCMToken", back_populates="user")
    promo_codes = relationship("PromoCode", back_populates="creator")
    promo_usages = relationship("PromoCodeUsage", back_populates="user")
    surge_pricings = relationship("SurgePricing", back_populates="creator")
    vehicles = relationship("Vehicle", back_populates="driver")
    reviews_given = relationship("Review", back_populates="reviewer", foreign_keys="Review.reviewer_id")
    reviews_received = relationship("Review", back_populates="reviewee", foreign_keys="Review.reviewee_id")
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_ride_at = Column(DateTime, nullable=True)
    total_rides = Column(Integer, default=0)
    
    # Relationships
    rides = relationship("Ride", back_populates="customer")

class Ride(Base):
    __tablename__ = "rides"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Keep rider_id for backward compatibility during migration
    rider_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    pickup_location = Column(Text)  # JSON: {"lat": float, "lng": float, "address": str}
    dropoff_location = Column(Text)  # JSON: {"lat": float, "lng": float, "address": str}
    current_location = Column(Text, nullable=True)  # JSON: {"lat": float, "lng": float}
    fare = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)  # in minutes
    vehicle_type = Column(String, default="economy")
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="rides")
    rider = relationship("User", foreign_keys=[rider_id], back_populates="rides_as_rider")
    driver = relationship("User", foreign_keys=[driver_id], back_populates="rides_as_driver")
    payments = relationship("Payment", back_populates="ride")
    messages = relationship("Message", back_populates="ride")
    gps_tracks = relationship("GPSTrack", back_populates="ride")
    routes = relationship("Route", back_populates="ride")
    reviews = relationship("Review", back_populates="ride")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    amount = Column(Float)
    currency = Column(String, default="UZS")
    status = Column(String, default="pending")  # pending, completed, failed, refunded
    payment_method = Column(String)  # card, wallet, cash
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ride = relationship("Ride", back_populates="payments")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)  # Positive for deposit, negative for commission
    transaction_type = Column(String)  # deposit, commission, refund
    description = Column(String)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=True)  # For commission transactions
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    ride = relationship("Ride", foreign_keys=[ride_id])

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ride = relationship("Ride", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

# Add messages relationship to Ride model
# (Already defined in the Ride class above)

class GPSTrack(Base):
    __tablename__ = "gps_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    accuracy = Column(Float, nullable=True)  # GPS accuracy in meters
    speed = Column(Float, nullable=True)  # Speed in km/h
    bearing = Column(Float, nullable=True)  # Direction in degrees
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ride = relationship("Ride", back_populates="gps_tracks")

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    route_data = Column(Text)  # JSON with route information
    distance = Column(Float)  # Route distance in km
    duration = Column(Integer)  # Estimated duration in minutes
    route_type = Column(String, default="fastest")  # fastest, shortest, eco_friendly
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ride = relationship("Ride", back_populates="routes")

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"))
    make = Column(String)  # Brand (Toyota, BMW, etc.)
    model = Column(String)  # Model (Camry, X5, etc.)
    year = Column(Integer)
    color = Column(String)
    license_plate = Column(String, unique=True, index=True)
    vehicle_type = Column(String, default="economy")  # economy, comfort, business, vip
    capacity = Column(Integer, default=4)  # Number of passengers
    
    # Vehicle features
    has_air_conditioning = Column(Boolean, default=True)
    has_wifi = Column(Boolean, default=False)
    has_gps = Column(Boolean, default=True)
    has_child_seat = Column(Boolean, default=False)
    has_pet_friendly = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    maintenance_due = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver = relationship("User", back_populates="vehicles")

class VehicleType(Base):
    __tablename__ = "vehicle_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # economy, comfort, business, vip
    display_name = Column(String)  # Economy, Comfort, Business, VIP
    base_fare = Column(Float, default=3000.0)
    per_km_rate = Column(Float, default=5.0)
    per_minute_rate = Column(Float, default=1.0)
    capacity = Column(Integer, default=4)
    is_active = Column(Boolean, default=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SurgePricing(Base):
    __tablename__ = "surge_pricing"
    
    id = Column(Integer, primary_key=True, index=True)
    area_name = Column(String)  # Geographic area name
    multiplier = Column(Float, default=1.0)  # Price multiplier
    is_active = Column(Boolean, default=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="surge_pricings")

class SurgeArea(Base):
    __tablename__ = "surge_areas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    center_lat = Column(Float)
    center_lng = Column(Float)
    radius_km = Column(Float, default=5.0)  # Radius in kilometers
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_type = Column(String)  # percentage, fixed
    discount_value = Column(Float)  # 10 for 10%, or 5000 for 5000 som
    max_uses = Column(Integer, default=1)  # How many times can be used
    used_count = Column(Integer, default=0)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="promo_codes")
    usages = relationship("PromoCodeUsage", back_populates="promo_code")

class PromoCodeUsage(Base):
    __tablename__ = "promo_code_usages"
    
    id = Column(Integer, primary_key=True, index=True)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=True)
    discount_amount = Column(Float)
    used_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    promo_code = relationship("PromoCode", back_populates="usages")
    user = relationship("User")
    ride = relationship("Ride")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    body = Column(Text)
    notification_type = Column(String)  # ride_update, emergency, promo, etc.
    data = Column(Text, nullable=True)  # JSON data for deep linking
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class FCMToken(Base):
    __tablename__ = "fcm_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    device_type = Column(String)  # ios, android, web
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with User
    user = relationship("User", back_populates="fcm_tokens")
    
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))  # Who gave the review
    reviewee_id = Column(Integer, ForeignKey("users.id"))  # Who received the review
    rating = Column(Integer)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    review_type = Column(String)  # driver_review, passenger_review
    is_helpful = Column(Integer, default=0)  # How many users found this helpful
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ride = relationship("Ride")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    reviewee = relationship("User", foreign_keys=[reviewee_id])

# New table: DriverStatus - keeps on-duty/rest state and last location without altering existing User schema
class DriverStatus(Base):
    __tablename__ = "driver_statuses"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    is_on_duty = Column(Boolean, default=False)  # True: accepts orders; False: resting
    last_lat = Column(Float, nullable=True)
    last_lng = Column(Float, nullable=True)
    city = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User (no backref to avoid cyclic imports elsewhere)
    driver = relationship("User")

class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
