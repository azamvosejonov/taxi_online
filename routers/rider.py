"""
Rider router - Passenger ride tracking and management
"""
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Ride, DriverStatus
from schemas import RideResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/rider", tags=["Rider"])


def require_rider(user: User) -> User:
    """Check if user is a regular rider (not driver/admin)"""
    if user.is_driver or user.is_admin:
        raise HTTPException(status_code=403, detail="Driver/Admin access not allowed")
    return user


@router.get("/current-ride", response_model=RideResponse)
async def get_current_ride(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current active ride for the rider"""
    require_rider(current_user)

    # Find current ride for this user
    ride = db.query(Ride).filter(
        Ride.customer_id == current_user.id,
        Ride.status.in_(["pending", "accepted", "in_progress"])
    ).first()

    if not ride:
        raise HTTPException(status_code=404, detail="No active ride found")

    return ride


@router.get("/ride/{ride_id}", response_model=RideResponse)
async def get_ride_details(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific ride details for the rider"""
    require_rider(current_user)

    ride = db.query(Ride).filter(
        Ride.id == ride_id,
        Ride.customer_id == current_user.id
    ).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    return ride


@router.get("/ride/{ride_id}/status")
async def get_ride_status(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time ride status with driver location and updated cost"""
    require_rider(current_user)

    ride = db.query(Ride).filter(
        Ride.id == ride_id,
        Ride.customer_id == current_user.id
    ).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    # Get driver current location if available
    driver_location = None
    driver_status = None
    if ride.driver_id:
        driver = db.query(User).filter(User.id == ride.driver_id).first()
        if driver and driver.current_location:
            driver_location = driver.current_location

        # Get driver duty status
        ds = db.query(DriverStatus).filter(DriverStatus.driver_id == ride.driver_id).first()
        if ds:
            driver_status = "on_duty" if ds.is_on_duty else "off_duty"

    # Calculate estimated remaining cost (if in progress)
    estimated_remaining_cost = 0
    if ride.status == "in_progress":
        # Simple estimation based on time passed
        if ride.created_at:
            time_passed_minutes = (datetime.utcnow() - ride.created_at).total_seconds() / 60
            if ride.duration and time_passed_minutes > 0:
                progress_ratio = min(time_passed_minutes / ride.duration, 1.0)
                estimated_remaining_cost = ride.fare * (1 - progress_ratio)

    return {
        "ride_id": ride.id,
        "status": ride.status,
        "driver_id": ride.driver_id,
        "driver_location": driver_location,
        "driver_status": driver_status,
        "current_fare": ride.fare or 0,
        "estimated_remaining_cost": round(estimated_remaining_cost, 2),
        "estimated_total_cost": ride.fare or 0,
        "distance_traveled": ride.distance or 0,
        "time_remaining_minutes": max(0, ride.duration - int(time_passed_minutes)) if ride.status == "in_progress" else ride.duration,
        "updated_at": datetime.utcnow().isoformat()
    }


@router.get("/ride/{ride_id}/location")
async def get_driver_location(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get driver's current location for ride tracking"""
    require_rider(current_user)

    ride = db.query(Ride).filter(
        Ride.id == ride_id,
        Ride.customer_id == current_user.id,
        Ride.status.in_(["accepted", "in_progress"])
    ).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Active ride not found")

    if not ride.driver_id:
        raise HTTPException(status_code=400, detail="No driver assigned yet")

    driver = db.query(User).filter(User.id == ride.driver_id).first()
    if not driver or not driver.current_location:
        raise HTTPException(status_code=404, detail="Driver location not available")

    # Parse location JSON
    try:
        location_data = eval(driver.current_location)  # Simple eval for JSON stored as string
        return {
            "driver_id": driver.id,
            "driver_name": driver.full_name,
            "vehicle_number": driver.vehicle_number,
            "vehicle_model": driver.vehicle_model,
            "location": location_data,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Error parsing driver location")


@router.get("/rides/history")
async def get_ride_history(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ride history for the rider"""
    require_rider(current_user)

    offset = (page - 1) * limit

    rides = db.query(Ride).filter(
        Ride.customer_id == current_user.id
    ).order_by(Ride.created_at.desc()).offset(offset).limit(limit).all()

    total_rides = db.query(Ride).filter(Ride.customer_id == current_user.id).count()

    return {
        "rides": rides,
        "total": total_rides,
        "page": page,
        "limit": limit,
        "pages": (total_rides + limit - 1) // limit
    }


@router.post("/ride/{ride_id}/cancel")
async def cancel_ride(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a ride (if not started yet)"""
    require_rider(current_user)

    ride = db.query(Ride).filter(
        Ride.id == ride_id,
        Ride.customer_id == current_user.id
    ).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    if ride.status not in ["pending", "accepted"]:
        raise HTTPException(status_code=400, detail="Cannot cancel ride in current status")

    ride.status = "cancelled"
    db.commit()

    return {"message": "Ride cancelled successfully", "ride_id": ride_id}
