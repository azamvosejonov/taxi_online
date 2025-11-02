"""
Authentication routes for Royal Taxi API
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import get_db
from models import User
from schemas import UserRegister, UserResponse, Token, UserLogin
from crud.user import get_user_by_phone
from utils.helpers import (
    verify_password,
    create_access_token,
    get_password_hash,
    validate_email_domain, hash_password,
)
from config import settings

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

    # Create new user with default values for required fields
    user_dict = user_data.dict(exclude_unset=True)
    
    # Set default values for required fields
    # Create user with basic info
    user = models.User(
        phone=user_data.phone,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        gender=user_data.gender,
        date_of_birth=user_data.date_of_birth,
        hashed_password=hashed_password,
        full_name=f"{user_data.first_name} {user_data.last_name}",
        vehicle_make=user_data.vehicle_make,
        vehicle_color=user_data.vehicle_color,
        position=user_data.position,
        license_plate=user_data.license_plate,
        tech_passport=user_data.tech_passport,
        is_driver=True,  # All users are drivers by default
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
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "gender": user.gender,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "vehicle_make": user.vehicle_make,
            "vehicle_color": user.vehicle_color,
            "position": user.position,
            "license_plate": user.license_plate,
            "tech_passport": user.tech_passport,
            "is_driver": user.is_driver,
            "is_dispatcher": user.is_dispatcher,
            "is_admin": user.is_admin,
            "is_approved": user.is_approved,
            "needs_driver_info": False  # Vehicle info already provided
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
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_driver": user.is_driver,
            "is_dispatcher": user.is_dispatcher,
            "is_admin": user.is_admin,
            "is_approved": user.is_approved,
            "needs_driver_info": user.is_driver and (user.vehicle_make is None or user.license_plate is None),  # Check if driver needs to complete vehicle info
            "vehicle_make": user.vehicle_make,
            "vehicle_color": user.vehicle_color,
            "position": user.position,
            "license_plate": user.license_plate,
            "rating": user.rating if hasattr(user, 'rating') else 0.0,
            "total_rides": user.total_rides if hasattr(user, 'total_rides') else 0,
            "current_balance": user.current_balance if hasattr(user, 'current_balance') else 0.0,
            "tech_passport": user.tech_passport
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
