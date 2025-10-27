"""
Files router - File upload and management for Royal Taxi API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session

from database import get_db
from models import User
from routers.auth import get_current_user
from utils.helpers import save_upload_file

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    responses={404: {"description": "Not found"}},
)


@router.post("/profile-picture")
async def upload_profile_picture(
    request: Request,
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


@router.post("/driver-documents")
async def upload_driver_documents(
    request: Request,
    license_file: UploadFile = File(None),
    insurance_file: UploadFile = File(None),
    vehicle_file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload driver documents"""
    if not current_user.is_driver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can upload documents"
        )

    uploaded_files = {}

    if license_file:
        license_path = await save_upload_file(license_file, "driver_docs")
        uploaded_files["license"] = license_path

    if insurance_file:
        insurance_path = await save_upload_file(insurance_file, "driver_docs")
        uploaded_files["insurance"] = insurance_path

    if vehicle_file:
        vehicle_path = await save_upload_file(vehicle_file, "driver_docs")
        uploaded_files["vehicle"] = vehicle_path

    if not uploaded_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded"
        )

    return {
        "message": "Documents uploaded successfully",
        "uploaded_files": uploaded_files
    }


@router.post("/upload/{folder}")
async def upload_file(
    folder: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload file to specific folder"""
    # Save file
    file_path = await save_upload_file(file, folder)

    return {
        "message": "File uploaded successfully",
        "file_path": file_path,
        "folder": folder
    }


@router.get("/uploads/{folder}/{filename}")
async def get_file(
    folder: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Get uploaded file (placeholder - implement actual file serving)"""
    return {
        "message": "File serving endpoint",
        "file_path": f"/uploads/{folder}/{filename}",
        "note": "Implement actual file serving based on your needs"
    }
