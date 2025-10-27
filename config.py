"""
Configuration management for Royal Taxi backend
"""
import os
from typing import Optional

# Database configuration
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./royaltaxi.db")
TESTING: bool = os.getenv("TESTING", "false").lower() == "true"

if TESTING:
    DATABASE_URL = "sqlite:///./test_royaltaxi.db"

# Security settings
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# Redis configuration for caching and rate limiting
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

# Firebase configuration for push notifications
FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")

# File upload settings
UPLOAD_DIR: str = "uploads"
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".gif"]

# Rate limiting settings
RATE_LIMIT_REQUESTS: int = 100
RATE_LIMIT_WINDOW: int = 60  # seconds

# API settings
API_TITLE: str = "Royal Taxi API"
API_VERSION: str = "1.0.0"
API_DESCRIPTION: str = "Backend API for Royal Taxi ride-sharing platform"

# CORS settings
CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
if CORS_ORIGINS == ["*"]:
    CORS_ORIGINS = ["*"]

# Commission settings
COMMISSION_RATE: float = 0.1  # 10% commission from each ride

# Vehicle types and rates
VEHICLE_TYPES: dict = {
    "economy": {
        "display_name": "Economy",
        "base_fare": 10000,  # 10,000 som
        "per_km_rate": 2000,  # 2,000 som per km
        "per_minute_rate": 500,  # 500 som per minute
        "capacity": 4
    },
    "comfort": {
        "display_name": "Comfort",
        "base_fare": 15000,  # 15,000 som
        "per_km_rate": 3000,  # 3,000 som per km
        "per_minute_rate": 750,  # 750 som per minute
        "capacity": 4
    },
    "business": {
        "display_name": "Business",
        "base_fare": 25000,  # 25,000 som
        "per_km_rate": 5000,  # 5,000 som per km
        "per_minute_rate": 1000,  # 1,000 som per minute
        "capacity": 4
    }
}

# Payment methods
PAYMENT_METHODS: list = ["card", "wallet", "cash"]

# Supported languages
SUPPORTED_LANGUAGES: list = ["uz", "ru", "en"]

# Pagination settings
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100

class Settings:
    """Application settings singleton"""
    def __init__(self):
        self.database_url: str = DATABASE_URL
        self.testing: bool = TESTING
        self.secret_key: str = SECRET_KEY
        self.algorithm: str = ALGORITHM
        self.access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
        self.redis_url: str = REDIS_URL
        self.firebase_credentials_path: str = FIREBASE_CREDENTIALS_PATH
        self.upload_dir: str = UPLOAD_DIR
        self.max_file_size: int = MAX_FILE_SIZE
        self.allowed_extensions: list = ALLOWED_EXTENSIONS
        self.rate_limit_requests: int = RATE_LIMIT_REQUESTS
        self.rate_limit_window: int = RATE_LIMIT_WINDOW
        self.api_title: str = API_TITLE
        self.api_version: str = API_VERSION
        self.api_description: str = API_DESCRIPTION
        self.cors_origins: list = CORS_ORIGINS
        self.commission_rate: float = COMMISSION_RATE
        self.vehicle_types: dict = VEHICLE_TYPES
        self.payment_methods: list = PAYMENT_METHODS
        self.supported_languages: list = SUPPORTED_LANGUAGES
        self.default_page_size: int = DEFAULT_PAGE_SIZE
        self.max_page_size: int = MAX_PAGE_SIZE

# Global settings instance
settings = Settings()
