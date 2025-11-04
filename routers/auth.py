"""
Authentication routes for Royal Taxi API
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
import random
import string

import models
from database import get_db
from models import User, OTPVerification
from schemas import (
    UserRegister, UserResponse, Token, UserLogin,
    SendOTPRequest, VerifyOTPRequest, CompleteProfileRequest,
    OTPResponse, VerifyOTPResponse
)
from crud.user import get_user_by_phone
from utils.helpers import (
    verify_password,
    create_access_token,
    get_password_hash,
    validate_email_domain, hash_password,
)
from config import settings
from services.sms_service import sms_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    },
)

def _extract_bearer_token(request: Request) -> str:
    """Try to read JWT from Authorization header or cookies.
    Returns token string or raises 401 if missing.
    """
    # 1) Authorization header (case-insensitive)
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()

    # 2) Cookies: access_token or Authorization
    token_cookie = (
        request.cookies.get("access_token")
        or request.cookies.get("Authorization")
        or request.cookies.get("authorization")
    )
    if token_cookie:
        return token_cookie.split(" ", 1)[1].strip() if token_cookie.lower().startswith("bearer ") else token_cookie

    # 3) Query param fallback (helpful in debugging): ?token=...
    token_q = request.query_params.get("token")
    if token_q:
        return token_q

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current authenticated user from header/cookie token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = _extract_bearer_token(request)
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        phone: str = payload.get("sub")
        if phone is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.phone == phone).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Phone number already registered"},
        500: {"description": "Internal server error"}
    }
)
async def register(user_data: UserRegister, response: Response, db: Session = Depends(get_db)):
    """Register a new user with phone number and return access token"""
    # Check if phone number already exists
    existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user mapped to current model fields
    user_dict = user_data.dict(exclude_unset=True)
    user = models.User(
        phone=user_data.phone,
        password=hashed_password,
        full_name=f"{user_data.first_name} {user_data.last_name}",
        # Map legacy fields to current model
        vehicle_model=user_data.vehicle_make,
        vehicle_color=user_data.vehicle_color,
        vehicle_number=user_data.license_plate,
        license_number=user_data.tech_passport,
        is_driver=True,
        is_dispatcher=False,
        is_admin=False,
        is_approved=False,
        is_active=True,
        current_balance=0.0,
        required_deposit=0.0,
        rating=5.0,
        total_rides=0
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.phone})
    
    # Return token with basic user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 604800,  # 7 days in seconds
        "user": {
            "id": user.id,
            "phone": user.phone,
            "full_name": user.full_name,
            "vehicle_model": user.vehicle_model,
            "vehicle_color": user.vehicle_color,
            "vehicle_number": user.vehicle_number,
            "license_number": user.license_number,
            "is_driver": user.is_driver,
            "is_dispatcher": user.is_dispatcher,
            "is_admin": user.is_admin,
            "is_approved": user.is_approved,
            "needs_driver_info": False
        },
        "token": access_token,
        "accessToken": access_token,
        "authorization": f"Bearer {access_token}",
        "security": {
            "Bearer": {
                "token": access_token,
                "type": "bearer"
            }
        }
    }

@router.post("/login")
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with phone number and password - returns token for auto-authorization
    """
    # Find user by phone
    user = get_user_by_phone(db, phone=user_data.phone)
    
    # Check if user exists and password is correct
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Telefon raqami yoki parol noto'g'ri",
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Ushbu foydalanuvchi faol emas",
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.phone})
    
    # Return token with user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 604800,  # 7 days in seconds
        "user": {
            "id": user.id,
            "phone": user.phone,
            "full_name": user.full_name,
            "is_driver": user.is_driver,
            "is_dispatcher": user.is_dispatcher,
            "is_admin": user.is_admin,
            "is_approved": user.is_approved,
            "needs_driver_info": user.is_driver and (user.vehicle_model is None or user.vehicle_number is None),
            "vehicle_model": user.vehicle_model,
            "vehicle_color": user.vehicle_color,
            "vehicle_number": user.vehicle_number,
            "license_number": user.license_number,
            "rating": user.rating if hasattr(user, 'rating') else 0.0,
            "total_rides": user.total_rides if hasattr(user, 'total_rides') else 0,
            "current_balance": user.current_balance if hasattr(user, 'current_balance') else 0.0
        },
        "token": access_token,  # For Swagger UI compatibility
        "accessToken": access_token,  # Alternative for some Swagger UI versions
        "authorization": f"Bearer {access_token}",  # Direct authorization header
        "security": {
            "Bearer": {
                "token": access_token,
                "type": "bearer"
            }
        }
    }


@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_active_user)):
    """
    Logout endpoint - invalidates the current session
    Note: Since we're using JWT tokens, the token will remain valid until expiration.
    The client should delete the token from storage.
    """
    # Clear auth cookie
    response.delete_cookie(key="access_token", path="/")
    return {
        "message": "Successfully logged out",
        "detail": "Token removed from client. Please delete the token from your storage.",
        "user": {
            "id": current_user.id,
            "phone": current_user.phone,
            "full_name": current_user.full_name
        }
    }


def generate_otp() -> str:
    """Generate a 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=6))


@router.post(
    "/send-otp",
    response_model=OTPResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "OTP sent successfully"},
        500: {"description": "Internal server error"}
    }
)
async def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """
    1-qadam: Telefon raqamga tasdiqlash kodini yuborish
    
    Telefon raqamga 6 raqamli tasdiqlash kodi yuboriladi.
    Kod 5 daqiqa davomida amal qiladi.
    """
    # Generate OTP code
    otp_code = generate_otp()
    
    # Set expiration time (5 minutes from now)
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # Delete any existing unverified OTPs for this phone
    db.query(OTPVerification).filter(
        OTPVerification.phone == request.phone,
        OTPVerification.is_verified == False
    ).delete()
    
    # Create new OTP record
    otp_record = OTPVerification(
        phone=request.phone,
        otp_code=otp_code,
        expires_at=expires_at,
        is_verified=False
    )
    
    db.add(otp_record)
    db.commit()
    
    # Send SMS via Twilio
    sms_sent = False
    if sms_service.enabled:
        success, message_sid = sms_service.send_otp(request.phone, otp_code)
        if success:
            sms_sent = True
            print(f"✅ SMS sent to {request.phone}. Message SID: {message_sid}")
        else:
            print(f"⚠️ Failed to send SMS to {request.phone}")
    else:
        # Development mode - log OTP to console
        print(f"📱 OTP for {request.phone}: {otp_code}")
    
    response_data = {
        "message": f"Tasdiqlash kodi {request.phone} raqamiga yuborildi. Kod 5 daqiqa davomida amal qiladi.",
        "phone": request.phone,
        "expires_in": 300,  # 5 minutes in seconds
    }
    
    # Only include OTP code in response if SMS was not sent (development mode)
    if not sms_sent:
        response_data["otp_code"] = otp_code  # DEVELOPMENT ONLY
    
    return response_data


@router.post(
    "/verify-otp",
    response_model=VerifyOTPResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "OTP verified successfully"},
        400: {"description": "Invalid or expired OTP"},
        404: {"description": "OTP not found"}
    }
)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    2-qadam: Tasdiqlash kodini tekshirish
    
    Telefon raqamga yuborilgan 6 raqamli kodni tekshiradi.
    Agar kod to'g'ri bo'lsa, foydalanuvchi ma'lumotlarini to'ldirish uchun tayyor bo'ladi.
    """
    # Find the latest OTP for this phone
    otp_record = db.query(OTPVerification).filter(
        OTPVerification.phone == request.phone,
        OTPVerification.is_verified == False
    ).order_by(OTPVerification.created_at.desc()).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tasdiqlash kodi topilmadi. Iltimos, qaytadan kod so'rang."
        )
    
    # Check if OTP is expired
    if datetime.utcnow() > otp_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tasdiqlash kodi muddati tugagan. Iltimos, qaytadan kod so'rang."
        )
    
    # Verify OTP code
    if otp_record.otp_code != request.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tasdiqlash kodi noto'g'ri. Iltimos, qaytadan urinib ko'ring."
        )
    
    # Mark OTP as verified
    otp_record.is_verified = True
    otp_record.verified_at = datetime.utcnow()
    db.commit()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.phone == request.phone).first()
    needs_profile = existing_user is None
    
    return {
        "message": "Telefon raqam muvaffaqiyatli tasdiqlandi!",
        "phone": request.phone,
        "verified": True,
        "needs_profile_completion": needs_profile
    }


@router.post(
    "/complete-profile",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={
        201: {"description": "Profile completed successfully"},
        400: {"description": "Phone not verified or user already exists"},
        404: {"description": "Verification not found"}
    }
)
async def complete_profile(request: CompleteProfileRequest, db: Session = Depends(get_db)):
    """
    3-qadam: Foydalanuvchi ma'lumotlarini to'ldirish
    
    Telefon raqam tasdiqlanganidan keyin, foydalanuvchi shaxsiy ma'lumotlarini 
    va haydovchilik ma'lumotlarini to'ldiradi.
    """
    # Check if phone was verified
    otp_record = db.query(OTPVerification).filter(
        OTPVerification.phone == request.phone,
        OTPVerification.is_verified == True
    ).order_by(OTPVerification.verified_at.desc()).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telefon raqam tasdiqlanmagan. Iltimos, avval telefon raqamni tasdiqlang."
        )
    
    # Check if verification is still valid (within 30 minutes)
    if datetime.utcnow() > otp_record.verified_at + timedelta(minutes=30):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tasdiqlash muddati tugagan. Iltimos, qaytadan boshlang."
        )
    
    # Check if user already exists (idempotent profile completion)
    existing_user = db.query(User).filter(User.phone == request.phone).first()
    
    # Check if license plate (vehicle number) is already taken by another user
    if request.license_plate:
        q = db.query(User).filter(User.vehicle_number == request.license_plate)
        if existing_user:
            q = q.filter(User.id != existing_user.id)
        existing_plate = q.first()
        if existing_plate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu davlat raqami allaqachon ro'yxatdan o'tgan."
            )
    
    # Check if tech passport (license number) is already taken by another user
    if request.tech_passport:
        q = db.query(User).filter(User.license_number == request.tech_passport)
        if existing_user:
            q = q.filter(User.id != existing_user.id)
        existing_tech = q.first()
        if existing_tech:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu texpassport allaqachon ro'yxatdan o'tgan."
            )
    
    # Generate a random password since we're using OTP authentication
    random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    hashed_password = hash_password(random_password)

    if existing_user:
        # Update existing user profile (idempotent behavior)
        existing_user.password = hashed_password
        existing_user.full_name = f"{request.first_name} {request.last_name}"
        existing_user.vehicle_model = request.vehicle_make
        existing_user.vehicle_color = request.vehicle_color
        existing_user.vehicle_number = request.license_plate
        existing_user.license_number = request.tech_passport
        existing_user.is_driver = True
        existing_user.is_dispatcher = existing_user.is_dispatcher or False
        existing_user.is_admin = existing_user.is_admin or False
        existing_user.is_approved = existing_user.is_approved or False
        existing_user.is_active = True
        db.commit()
        db.refresh(existing_user)
        user = existing_user
    else:
        # Create new user with all information
        user = User(
            phone=request.phone,
            password=hashed_password,
            full_name=f"{request.first_name} {request.last_name}",
            vehicle_model=request.vehicle_make,
            vehicle_color=request.vehicle_color,
            vehicle_number=request.license_plate,
            license_number=request.tech_passport,
            is_driver=True,
            is_dispatcher=False,
            is_admin=False,
            is_approved=False,
            is_active=True,
            current_balance=0.0,
            required_deposit=0.0,
            rating=5.0,
            total_rides=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.phone})
    
    # Return token with user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 604800,  # 7 days in seconds
        "user": {
            "id": user.id,
            "phone": user.phone,
            "full_name": user.full_name,
            "vehicle_model": user.vehicle_model,
            "vehicle_color": user.vehicle_color,
            "vehicle_number": user.vehicle_number,
            "license_number": user.license_number,
            "is_driver": user.is_driver,
            "is_dispatcher": user.is_dispatcher,
            "is_admin": user.is_admin,
            "is_approved": user.is_approved,
            "current_balance": user.current_balance,
            "rating": user.rating,
            "total_rides": user.total_rides
        },
        "token": access_token,
        "accessToken": access_token,
        "authorization": f"Bearer {access_token}",
        "security": {
            "Bearer": {
                "token": access_token,
                "type": "bearer"
            }
        }
    }
