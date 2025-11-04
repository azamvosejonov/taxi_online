"""
Rider router - Passenger ride tracking and management
"""
from typing import Optional
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Ride, DriverStatus
from schemas import RideResponse
from routers.auth import get_current_user
from utils.helpers import calculate_distance

router = APIRouter(prefix="/rider", tags=["Rider"])


def require_rider(user: User) -> User:
    """Allow any authenticated active user to access rider views."""
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user


def _parse_location(loc) -> Optional[dict]:
    if isinstance(loc, dict):
        return loc
    if isinstance(loc, str) and loc:
        try:
            return json.loads(loc)
        except Exception:
            return None
    return None


def _ride_to_response(ride: Ride) -> RideResponse:
    pickup = _parse_location(ride.pickup_location) or {}
    dropoff = _parse_location(ride.dropoff_location) or {}
    current = _parse_location(ride.current_location)
    # Compute distance if possible
    dist = 0.0
    try:
        if all(k in pickup for k in ("lat", "lng")) and all(k in dropoff for k in ("lat", "lng")):
            dist = calculate_distance(float(pickup["lat"]), float(pickup["lng"]), float(dropoff["lat"]), float(dropoff["lng"]))
    except Exception:
        dist = 0.0

    return RideResponse(
        id=ride.id,
        customer_id=ride.customer_id,
        rider_id=ride.rider_id,
        driver_id=ride.driver_id,
        customer=None,
        pickup_location=pickup,
        dropoff_location=dropoff,
        current_location=current,
        status=ride.status,
        fare=float(ride.fare or 0),
        distance=float(dist),
        duration=int(ride.duration or 0),
        vehicle_type=ride.vehicle_type,
        created_at=ride.created_at,
        completed_at=ride.completed_at,
    )


@router.get("/current-ride", response_model=RideResponse)
async def get_current_ride(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current active ride for the rider"""
    require_rider(current_user)

    # Find current ride for this user by rider_id
    ride = db.query(Ride).filter(
        Ride.rider_id == current_user.id,
        Ride.status.in_(["pending", "accepted", "in_progress"])
    ).first()

    if not ride:
        raise HTTPException(status_code=404, detail="No active ride found")

    return _ride_to_response(ride)


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
        Ride.rider_id == current_user.id
    ).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    return _ride_to_response(ride)


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
        Ride.rider_id == current_user.id
    ).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    # Get driver current location if available
    driver_location = None
    driver_status = None
    if ride.driver_id:
        driver = db.query(User).filter(User.id == ride.driver_id).first()
        if driver and driver.current_location:
            try:
                driver_location = json.loads(driver.current_location) if isinstance(driver.current_location, str) else driver.current_location
            except Exception:
                driver_location = None

        # Get driver duty status
        ds = db.query(DriverStatus).filter(DriverStatus.driver_id == ride.driver_id).first()
        if ds:
            driver_status = "on_duty" if ds.is_on_duty else "off_duty"

    # Calculate estimated remaining cost (if in progress)
    estimated_remaining_cost = 0.0
    time_passed_minutes = 0
    if ride.created_at:
        time_passed_minutes = (datetime.utcnow() - ride.created_at).total_seconds() / 60
    progress_ratio = 0.0
    if ride.duration and time_passed_minutes > 0:
        progress_ratio = min(time_passed_minutes / max(ride.duration, 1), 1.0)
    if ride.status == "in_progress" and ride.fare:
        estimated_remaining_cost = float(ride.fare) * (1 - progress_ratio)

    # Compute total planned distance
    pickup = _parse_location(ride.pickup_location) or {}
    dropoff = _parse_location(ride.dropoff_location) or {}
    total_distance = 0.0
    try:
        if all(k in pickup for k in ("lat", "lng")) and all(k in dropoff for k in ("lat", "lng")):
            total_distance = calculate_distance(float(pickup["lat"]), float(pickup["lng"]), float(dropoff["lat"]), float(dropoff["lng"]))
    except Exception:
        total_distance = 0.0
    distance_traveled = total_distance * progress_ratio

    return {
        "ride_id": ride.id,
        "status": ride.status,
        "driver_id": ride.driver_id,
        "driver_location": driver_location,
        "driver_status": driver_status,
        "current_fare": float(ride.fare or 0),
        "estimated_remaining_cost": round(float(estimated_remaining_cost), 2),
        "estimated_total_cost": float(ride.fare or 0),
        "distance_traveled": round(float(distance_traveled), 2),
        "time_remaining_minutes": max(0, int(ride.duration or 0) - int(time_passed_minutes)) if ride.status == "in_progress" else int(ride.duration or 0),
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
        Ride.rider_id == current_user.id,
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
        location_data = json.loads(driver.current_location) if isinstance(driver.current_location, str) else driver.current_location
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
        Ride.rider_id == current_user.id
    ).order_by(Ride.created_at.desc()).offset(offset).limit(limit).all()

    total_rides = db.query(Ride).filter(Ride.rider_id == current_user.id).count()

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
        Ride.rider_id == current_user.id
    ).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    if ride.status not in ["pending", "accepted"]:
        raise HTTPException(status_code=400, detail="Cannot cancel ride in current status")

    ride.status = "cancelled"
    db.commit()

    return {"message": "Ride cancelled successfully", "ride_id": ride_id}
