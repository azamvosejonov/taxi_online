"""
Authentication routes for Royal Taxi API
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from database import get_db
from models import User
from schemas import UserCreate, UserResponse, Token, UserLogin
from utils.helpers import verify_password, create_access_token, validate_email_domain, hash_password
from config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
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
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register")
async def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    """Register a new user and return access token"""
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # Check if phone number already exists
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    # Validate email domain (basic check)
    if not validate_email_domain(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create new user with default values for required fields
    user_dict = user_data.dict(exclude_unset=True)
    
    # Set default values for required fields
    user_dict.update({
        'password': hashed_password,
        'current_balance': 0.0,
        'required_deposit': 0.0,
        'is_active': True,
        'current_location': None,
        'city': None,
        'rating': 5.0,
        'total_rides': 0
    })
    
    # Handle language field safely
    if 'language' in user_dict and hasattr(user_dict['language'], 'value'):
        user_dict['language'] = user_dict['language'].value
    
    # Handle vehicle_type field safely
    if 'vehicle_type' in user_dict and user_dict['vehicle_type'] is not None:
        if hasattr(user_dict['vehicle_type'], 'value'):
            user_dict['vehicle_type'] = user_dict['vehicle_type'].value
    
    # Create the user
    db_user = User(**user_dict)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create access token with longer expiration for better UX
        access_token = create_access_token(
            data={"sub": db_user.email},
            expires_delta=timedelta(days=7)  # 7 days for better UX
        )
        # Set HttpOnly cookie so Swagger requests are authorized even if header missing
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=7 * 24 * 60 * 60,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/",
        )
        
        # Return token with OAuth2 format for Swagger UI auto-authorization
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 604800,
            "user": {
                "id": db_user.id,
                "email": db_user.email,
                "full_name": db_user.full_name,
                "is_driver": db_user.is_driver,
                "is_admin": db_user.is_admin
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
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login")
async def login(
    user_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login with email/phone and password - returns token for auto-authorization
    """
    # Find user by email or phone
    user = db.query(User).filter(
        (User.email == user_data.username) | (User.phone == user_data.username)
    ).first()

    # Check if user exists and password is correct
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive. Please contact support."
        )

    # Create access token with longer expiration
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(days=7)
    )
    # Set HttpOnly cookie so Swagger requests are authorized even if header missing
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )

    # Return token with OAuth2 format for Swagger UI auto-authorization
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 604800,  # 7 days in seconds
        "user": {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "full_name": user.full_name,
            "is_driver": user.is_driver,
            "is_admin": user.is_admin,
            "language": user.language,
            "current_balance": user.current_balance,
            "rating": user.rating
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
            "email": current_user.email,
            "full_name": current_user.full_name
        }
    }
