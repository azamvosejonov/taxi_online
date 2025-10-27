"""
Dispatcher router - Implements dispatcher-first order flow
"""
from typing import List, Optional, Tuple
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Ride, Customer, Transaction, Notification, DriverStatus
from schemas import (
    DispatchOrderCreate, DispatchOrderResponse, RideResponse,
    DepositRequest, BroadcastRequest
)
from routers.auth import get_current_user
from utils.helpers import (
    calculate_distance, estimate_duration, calculate_fare
)
from config import settings

router = APIRouter(prefix="/dispatcher", tags=["Dispatcher"])


def require_dispatcher(user: User) -> User:
    if not (user.is_dispatcher or user.is_admin):
        raise HTTPException(status_code=403, detail="Dispatcher access required")
    return user


def _get_or_create_customer(db: Session, phone: str, name: Optional[str]) -> Customer:
    cust = db.query(Customer).filter(Customer.phone == phone).first()
    if cust:
        return cust
    first_name = None
    last_name = None
    if name:
        parts = name.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else None
    cust = Customer(phone=phone, first_name=first_name, last_name=last_name)
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return cust


def _broadcast_to_nearby_drivers(
    db: Session,
    pickup_lat: float,
    pickup_lng: float,
    radius_km: float = 3.0,
) -> List[int]:
    """Return list of driver IDs within radius and active.
    NOTE: Actual push notifications are out of scope; we persist Notification rows.
    """
    # Get on-duty drivers
    on_duty_driver_ids = {
        ds.driver_id for ds in db.query(DriverStatus).filter(DriverStatus.is_on_duty == True).all()
    }
    drivers = db.query(User).filter(
        User.is_driver == True,
        User.is_active == True,
        User.is_approved == True,
        User.current_location.isnot(None),
        User.id.in_(on_duty_driver_ids if on_duty_driver_ids else [0])
    ).all()

    nearby_driver_ids: List[int] = []
    for d in drivers:
        try:
            loc = json.loads(d.current_location)
            dlat, dlng = float(loc.get("lat")), float(loc.get("lng"))
            if dlat is None or dlng is None:
                continue
            dist = calculate_distance(pickup_lat, pickup_lng, dlat, dlng)
            if dist <= radius_km:
                nearby_driver_ids.append(d.id)
        except Exception:
            continue

    # Save notifications for drivers (simple DB row; real-time push can be added later)
    for driver_id in nearby_driver_ids:
        note = Notification(
            user_id=driver_id,
            title="Yangi buyurtma",
            body="Yaqin atrofda yangi buyurtma mavjud",
            notification_type="ride_update",
        )
        db.add(note)
    db.commit()

    return nearby_driver_ids


@router.post("/order", response_model=DispatchOrderResponse)
async def create_order(
    order: DispatchOrderCreate,
    broadcast: BroadcastRequest = BroadcastRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dispatcher creates an order, calculates estimate, and broadcasts to nearby drivers."""
    require_dispatcher(current_user)

    # Ensure customer exists
    customer = _get_or_create_customer(db, order.customer_phone, order.customer_name)

    # Calculate estimate
    distance = calculate_distance(
        order.pickup_location.lat, order.pickup_location.lng,
        order.dropoff_location.lat, order.dropoff_location.lng
    )
    duration = estimate_duration(distance)
    fare = calculate_fare(distance, duration, order.vehicle_type.value)

    # Create ride
    ride = Ride(
        customer_id=customer.id,
        rider_id=current_user.id,
        pickup_location=json.dumps(order.pickup_location.dict()),
        dropoff_location=json.dumps(order.dropoff_location.dict()),
        status="pending",
        fare=fare,
        duration=duration,
        vehicle_type=order.vehicle_type.value,
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)

    # Broadcast to nearby drivers
    driver_ids = _broadcast_to_nearby_drivers(
        db,
        order.pickup_location.lat,
        order.pickup_location.lng,
        radius_km=broadcast.radius_km or 3.0,
    )

    # Prepare response
    resp = DispatchOrderResponse(
        ride=RideResponse(
            id=ride.id,
            customer_id=ride.customer_id,
            rider_id=ride.rider_id,
            driver_id=ride.driver_id,
            customer=None,
            pickup_location=json.loads(ride.pickup_location),
            dropoff_location=json.loads(ride.dropoff_location),
            current_location=json.loads(ride.current_location) if ride.current_location else None,
            status=ride.status,
            fare=ride.fare or 0,
            distance=distance,
            duration=duration,
            vehicle_type=ride.vehicle_type,
            created_at=ride.created_at,
            completed_at=ride.completed_at,
        ),
        broadcasted_to=len(driver_ids)
    )
    return resp


@router.post("/order/{ride_id}/broadcast")
async def broadcast_order(
    ride_id: int,
    params: BroadcastRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Re-broadcast existing order (e.g., widen search)."""
    require_dispatcher(current_user)

    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    pickup = json.loads(ride.pickup_location)
    driver_ids = _broadcast_to_nearby_drivers(
        db, float(pickup.get("lat")), float(pickup.get("lng")), radius_km=params.radius_km or 3.0
    )
    return {"message": "Broadcasted", "count": len(driver_ids), "driver_ids": driver_ids}


@router.post("/deposit")
async def add_deposit(
    payload: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dispatcher tops up driver's deposit (balance)."""
    require_dispatcher(current_user)

    driver = db.query(User).filter(User.id == payload.driver_id, User.is_driver == True).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.current_balance = (driver.current_balance or 0) + float(payload.amount)

    tx = Transaction(
        user_id=driver.id,
        amount=float(payload.amount),
        transaction_type="deposit",
        description="Dispatcher deposit"
    )
    db.add(tx)
    db.commit()

    return {"message": "Deposit added", "driver_id": driver.id, "new_balance": driver.current_balance}


@router.post("/block/{driver_id}")
async def block_driver(
    driver_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_dispatcher(current_user)
    driver = db.query(User).filter(User.id == driver_id, User.is_driver == True).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_active = False
    db.commit()

    db.add(Notification(user_id=driver.id, title="Account blocked", body="Siz vaqtincha bloklandingiz", notification_type="emergency"))
    db.commit()
    return {"message": "Driver blocked"}


@router.post("/unblock/{driver_id}")
async def unblock_driver(
    driver_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_dispatcher(current_user)
    driver = db.query(User).filter(User.id == driver_id, User.is_driver == True).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_active = True
    db.commit()
    return {"message": "Driver unblocked"}


@router.get("/drivers/locations")
async def list_driver_locations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_dispatcher(current_user)
    drivers = db.query(User).filter(User.is_driver == True).all()
    items = []
    for d in drivers:
        loc = None
        if d.current_location:
            try:
                loc = json.loads(d.current_location)
            except Exception:
                loc = None
        items.append({
            "id": d.id,
            "full_name": d.full_name,
            "phone": d.phone,
            "vehicle_number": d.vehicle_number,
            "vehicle_model": d.vehicle_model,
            "is_active": d.is_active,
            "is_approved": d.is_approved,
            "current_balance": d.current_balance,
            "location": loc,
        })
    return {"drivers": items}


@router.post("/cancel/{ride_id}")
async def cancel_order(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_dispatcher(current_user)
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if ride.status in ("completed",):
        raise HTTPException(status_code=400, detail="Cannot cancel completed ride")
    ride.status = "cancelled"
    db.commit()
    return {"message": "Order cancelled"}
