"""
Driver router - Driver duty status, ride acceptance, progress, and stats
"""
from typing import Optional, Dict, Any
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Ride, Transaction, Payment, SystemConfig, DriverStatus
from schemas import DriverStatusUpdate, CompleteRideRequest
from routers.auth import get_current_user
from utils.helpers import calculate_distance
from websocket import manager  # WebSocket manager import

router = APIRouter(prefix="/driver", tags=["Driver"])


def require_driver(user: User) -> User:
    if not user.is_driver:
        raise HTTPException(status_code=403, detail="Driver access required")
    return user


def get_commission_rate(db: Session) -> float:
    cfg = db.query(SystemConfig).filter(SystemConfig.key == "commission_rate").first()
    if cfg:
        try:
            return float(cfg.value)
        except Exception:
            pass
    # default fallback (10%)
    return 0.10


def ensure_can_accept(user: User, db: Session) -> None:
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="Driver not approved")
    # Must be on-duty
    ds = db.query(DriverStatus).filter(DriverStatus.driver_id == user.id).first()
    if not ds or not ds.is_on_duty:
        raise HTTPException(status_code=403, detail="Driver is not on-duty")
    # Must have positive deposit
    if (user.current_balance or 0) <= 0:
        raise HTTPException(status_code=403, detail="Insufficient deposit. Ask dispatcher to top up.")


@router.post("/status")
async def update_status(
    payload: DriverStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_driver(current_user)
    ds = db.query(DriverStatus).filter(DriverStatus.driver_id == current_user.id).first()
    if not ds:
        ds = DriverStatus(driver_id=current_user.id)
        db.add(ds)
    ds.is_on_duty = payload.is_on_duty
    if payload.lat is not None and payload.lng is not None:
        ds.last_lat = payload.lat
        ds.last_lng = payload.lng
        # Also mirror to User.current_location for legacy compatibility
        current_user.current_location = json.dumps({"lat": payload.lat, "lng": payload.lng})
    if payload.city:
        ds.city = payload.city
        current_user.city = payload.city
    db.commit()

    # Broadcast location update to dispatchers via WebSocket
    if payload.lat is not None and payload.lng is not None:
        location_update = {
            "type": "driver_location_update",
            "driver_id": current_user.id,
            "driver_name": current_user.full_name,
            "location": {
                "lat": payload.lat,
                "lng": payload.lng,
                "city": payload.city
            },
            "is_on_duty": payload.is_on_duty,
            "timestamp": datetime.utcnow().isoformat()
        }
        # Broadcast to all dispatchers
        await manager.broadcast(json.dumps(location_update), "dispatchers")

        # Also broadcast to riders if driver has active rides
        active_rides = db.query(Ride).filter(
            Ride.driver_id == current_user.id,
            Ride.status.in_(["accepted", "in_progress"])
        ).all()

        for ride in active_rides:
            rider_update = {
                "type": "driver_location_update",
                "ride_id": ride.id,
                "driver_location": {
                    "lat": payload.lat,
                    "lng": payload.lng,
                    "city": payload.city
                },
                "driver_status": "on_duty" if payload.is_on_duty else "off_duty",
                "timestamp": datetime.utcnow().isoformat()
            }
            await manager.broadcast(json.dumps(rider_update), "riders")

    return {"message": "Status updated", "is_on_duty": ds.is_on_duty}


@router.post("/rides/{ride_id}/accept")
async def accept_ride(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_driver(current_user)
    ensure_can_accept(current_user, db)

    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if ride.status not in ("pending",):
        raise HTTPException(status_code=400, detail=f"Ride not accept-able (status={ride.status})")

    ride.driver_id = current_user.id
    ride.status = "accepted"
    db.commit()
    return {"message": "Ride accepted"}


@router.post("/rides/{ride_id}/start")
async def start_ride(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_driver(current_user)

    ride = db.query(Ride).filter(Ride.id == ride_id, Ride.driver_id == current_user.id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found or not assigned to you")
    if ride.status not in ("accepted",):
        raise HTTPException(status_code=400, detail=f"Cannot start ride in status={ride.status}")

    ride.status = "in_progress"
    db.commit()

    # Notify rider via WebSocket
    rider_update = {
        "type": "ride_status_update",
        "ride_id": ride_id,
        "old_status": "accepted",
        "new_status": "in_progress",
        "message": "Haydovchi safarga chiqdi",
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(json.dumps(rider_update), "riders")

    return {"message": "Ride started"}


@router.post("/rides/{ride_id}/complete")
async def complete_ride(
    ride_id: int,
    payload: CompleteRideRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_driver(current_user)

    ride = db.query(Ride).filter(Ride.id == ride_id, Ride.driver_id == current_user.id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found or not assigned to you")
    if ride.status not in ("in_progress", "accepted"):
        raise HTTPException(status_code=400, detail=f"Cannot complete ride in status={ride.status}")

    # Optional override of dropoff and fare
    if payload.dropoff_location:
        ride.dropoff_location = json.dumps(payload.dropoff_location.dict())
    if payload.final_fare is not None:
        ride.fare = float(payload.final_fare)

    ride.status = "completed"

    # Payment (cash) and commission deduction
    final_fare = float(ride.fare or 0)
    commission_rate = get_commission_rate(db)
    commission = round(final_fare * commission_rate, 2)

    # Record payment row
    pay = Payment(
        ride_id=ride.id,
        amount=final_fare,
        currency="UZS",
        status="completed",
        payment_method="cash",
        transaction_id=None,
    )
    db.add(pay)
    db.commit()

    remaining = float(current_user.current_balance or 0)

    # Notify rider via WebSocket
    rider_update = {
        "type": "ride_completed",
        "ride_id": ride_id,
        "final_fare": final_fare,
        "message": f"Safar tugadi. Umumiy narx: {final_fare} UZS",
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(json.dumps(rider_update), "riders")

    return {
        "message": "Ride completed",
        "final_fare": final_fare,
        "commission_rate": commission_rate,
        "commission": commission,
        "remaining_deposit": remaining,
    }
@router.get("/stats")
async def driver_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_driver(current_user)

    # Aggregate simple stats
    total_completed = db.query(Ride).filter(Ride.driver_id == current_user.id, Ride.status == "completed").count()
    total_accepted = db.query(Ride).filter(Ride.driver_id == current_user.id).count()

    # Earnings are cash paid to driver; we consider commission deducted separately
    payments = db.query(Payment).join(Ride, Payment.ride_id == Ride.id).filter(
        Ride.driver_id == current_user.id,
        Payment.status == "completed"
    ).all()
    total_revenue = sum(p.amount or 0 for p in payments)

    # Distance sum from rides (derive from pickup/dropoff JSON)
    completed = db.query(Ride).filter(Ride.driver_id == current_user.id, Ride.status == "completed").all()
    total_km = 0.0
    for r in completed:
        try:
            p = json.loads(r.pickup_location) if r.pickup_location else None
            d = json.loads(r.dropoff_location) if r.dropoff_location else None
            if p and d and all(k in p for k in ("lat", "lng")) and all(k in d for k in ("lat", "lng")):
                total_km += calculate_distance(float(p["lat"]), float(p["lng"]), float(d["lat"]), float(d["lng"]))
        except Exception:
            continue

    return {
        "total_completed": total_completed,
        "total_accepted": total_accepted,
        "total_revenue": total_revenue,
        "total_km": total_km,
        "current_balance": float(current_user.current_balance or 0),
    }
