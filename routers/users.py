"""
Users router - User profile and settings management for Royal Taxi API
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any

from database import get_db
from models import User
from schemas import UserResponse, UserUpdate
from routers.auth import get_current_user
from utils.helpers import save_upload_file

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Update only provided fields
    update_data = profile_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    # Save file
    file_path = await save_upload_file(file, "profiles")

    # Update user profile
    current_user.profile_photo = file_path
    db.commit()

    return {
        "message": "Profile picture uploaded successfully",
        "file_path": file_path
    }


@router.get("/balance")
async def get_balance(current_user: User = Depends(get_current_user)):
    """Get user balance"""
    return {
        "current_balance": current_user.current_balance,
        "required_deposit": current_user.required_deposit,
        "is_approved": current_user.is_approved
    }


@router.get("/rides")
async def get_user_rides(current_user: User = Depends(get_current_user)):
    """Get user's ride history"""
    # This would typically be implemented with proper ride filtering
    return {"message": "User rides endpoint - to be implemented"}


@router.get("/transactions")
async def get_user_transactions(current_user: User = Depends(get_current_user)):
    """Get user's transaction history"""
    # This would typically be implemented with transaction model
    return {"message": "User transactions endpoint - to be implemented"}
