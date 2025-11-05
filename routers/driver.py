"""
Driver router - Driver duty status, ride acceptance, progress, and stats
"""
from typing import Optional, Dict, Any
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Ride, Transaction, Payment, SystemConfig, DriverStatus, Notification
from schemas import DriverStatusUpdate, CompleteRideRequest, PricingConfigResponse
from routers.auth import get_current_user
from utils.helpers import calculate_distance
from sqlalchemy import func, extract
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


@router.get("/pricing", response_model=PricingConfigResponse)
async def get_driver_pricing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Haydovchi uchun narxlarni ko'rish (read-only)
    
    **Returns:**
    - Barcha transport turlari uchun narxlar
    - Komissiya stavkasi
    """
    require_driver(current_user)
    
    # Get all pricing configs
    economy_config = db.query(SystemConfig).filter(SystemConfig.key == "pricing_economy").first()
    comfort_config = db.query(SystemConfig).filter(SystemConfig.key == "pricing_comfort").first()
    business_config = db.query(SystemConfig).filter(SystemConfig.key == "pricing_business").first()
    commission_config = db.query(SystemConfig).filter(SystemConfig.key == "commission_rate").first()
    
    # Default values
    economy = {"base_fare": 10000, "per_km_rate": 2000, "per_minute_rate": 500}
    comfort = {"base_fare": 15000, "per_km_rate": 3000, "per_minute_rate": 750}
    business = {"base_fare": 25000, "per_km_rate": 5000, "per_minute_rate": 1000}
    commission_rate = 0.10
    
    # Parse from DB if exists
    if economy_config:
        try:
            economy = json.loads(economy_config.value)
        except:
            pass
    
    if comfort_config:
        try:
            comfort = json.loads(comfort_config.value)
        except:
            pass
    
    if business_config:
        try:
            business = json.loads(business_config.value)
        except:
            pass
    
    if commission_config:
        try:
            commission_rate = float(commission_config.value)
        except:
            pass
    
    return {
        "economy": economy,
        "comfort": comfort,
        "business": business,
        "commission_rate": commission_rate
    }


@router.get("/rides/history")
async def get_driver_ride_history(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Haydovchi safar tarixi
    
    **Query Parameters:**
    - page: Sahifa raqami (default: 1)
    - limit: Har sahifada nechta (default: 20, max: 100)
    
    **Returns:**
    - Haydovchi barcha safarlari ro'yxati (eng yangidan eskilariga)
    """
    require_driver(current_user)
    
    # Validate and limit
    if limit > 100:
        limit = 100
    if page < 1:
        page = 1
    
    offset = (page - 1) * limit
    
    # Get total count
    total = db.query(Ride).filter(Ride.driver_id == current_user.id).count()
    
    # Get rides with pagination (newest first)
    rides = db.query(Ride).filter(
        Ride.driver_id == current_user.id
    ).order_by(Ride.created_at.desc()).offset(offset).limit(limit).all()
    
    # Format rides
    rides_list = []
    for ride in rides:
        pickup = None
        dropoff = None
        
        try:
            if ride.pickup_location:
                pickup = json.loads(ride.pickup_location)
        except:
            pass
        
        try:
            if ride.dropoff_location:
                dropoff = json.loads(ride.dropoff_location)
        except:
            pass
        
        rides_list.append({
            "id": ride.id,
            "customer_id": ride.customer_id,
            "status": ride.status,
            "fare": ride.fare,
            "duration": ride.duration,
            "vehicle_type": ride.vehicle_type,
            "pickup_location": pickup,
            "dropoff_location": dropoff,
            "created_at": ride.created_at.isoformat() if ride.created_at else None,
            "completed_at": ride.completed_at.isoformat() if ride.completed_at else None
        })
    
    pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "rides": rides_list,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


@router.get("/calculate-fare")
async def calculate_fare(
    distance: float,
    duration: int,
    vehicle_type: str = "economy",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Taxometer - Narxni hisoblash (Haydovchi uchun)
    
    **Query Parameters:**
    - distance: Masofa (km)
    - duration: Vaqt (daqiqa)
    - vehicle_type: economy, comfort, yoki business (default: economy)
    
    **Returns:**
    - Hisoblangan narx, komissiya, va haydovchi daromadi
    """
    require_driver(current_user)
    
    # Get pricing config
    config_key = f"pricing_{vehicle_type}"
    pricing_config = db.query(SystemConfig).filter(SystemConfig.key == config_key).first()
    
    # Default values
    base_fare = 10000
    per_km_rate = 2000
    per_minute_rate = 500
    
    if vehicle_type == "comfort":
        base_fare = 15000
        per_km_rate = 3000
        per_minute_rate = 750
    elif vehicle_type == "business":
        base_fare = 25000
        per_km_rate = 5000
        per_minute_rate = 1000
    
    # Override with DB config if exists
    if pricing_config:
        try:
            config_data = json.loads(pricing_config.value)
            base_fare = config_data.get("base_fare", base_fare)
            per_km_rate = config_data.get("per_km_rate", per_km_rate)
            per_minute_rate = config_data.get("per_minute_rate", per_minute_rate)
        except:
            pass
    
    # Calculate fare
    distance_cost = distance * per_km_rate
    time_cost = duration * per_minute_rate
    total_fare = base_fare + distance_cost + time_cost
    
    # Get commission rate
    commission_rate = get_commission_rate(db)
    commission_amount = round(total_fare * commission_rate, 2)
    driver_earnings = round(total_fare - commission_amount, 2)
    
    return {
        "vehicle_type": vehicle_type,
        "distance_km": distance,
        "duration_minutes": duration,
        "breakdown": {
            "base_fare": base_fare,
            "distance_cost": distance_cost,
            "time_cost": time_cost
        },
        "total_fare": round(total_fare, 2),
        "commission_rate": commission_rate,
        "commission_amount": commission_amount,
        "driver_earnings": driver_earnings,
        "formula": f"{base_fare} + ({distance} × {per_km_rate}) + ({duration} × {per_minute_rate}) = {round(total_fare, 2)} so'm"
    }


@router.get("/notifications")
async def get_driver_notifications(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Haydovchi xabarlari tarixi
    
    **Query Parameters:**
    - page: Sahifa raqami (default: 1)
    - limit: Har sahifada nechta (default: 20, max: 100)
    
    **Returns:**
    - Haydovchiga yuborilgan barcha xabarlar (eng yangidan eskilariga)
    """
    require_driver(current_user)
    
    # Validate and limit
    if limit > 100:
        limit = 100
    if page < 1:
        page = 1
    
    offset = (page - 1) * limit
    
    # Get total count
    total = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).count()
    
    # Get notifications with pagination (newest first)
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    # Format notifications
    notifications_list = []
    for notif in notifications:
        notifications_list.append({
            "id": notif.id,
            "title": notif.title,
            "body": notif.body,
            "notification_type": notif.notification_type,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat() if notif.created_at else None
        })
    
    pages = (total + limit - 1) // limit
    
    return {
        "notifications": notifications_list,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


@router.get("/stats/detailed")
async def driver_stats_detailed(
    period: str = "all",  # all, daily, weekly, monthly
    date: Optional[str] = None,  # YYYY-MM-DD format
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Haydovchi uchun batafsil statistika
    
    **Query Parameters:**
    - period: all, daily, weekly, monthly (default: all)
    - date: YYYY-MM-DD format (optional, for daily/weekly/monthly)
    
    **Returns:**
    - Tanlangan davr uchun batafsil statistika
    """
    require_driver(current_user)
    
    query = db.query(Ride).filter(Ride.driver_id == current_user.id)
    
    # Apply period filter
    if period == "daily" and date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(func.date(Ride.created_at) == target_date)
        except:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    elif period == "weekly" and date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            # Get week start (Monday)
            week_start = target_date - timedelta(days=target_date.weekday())
            week_end = week_start + timedelta(days=7)
            query = query.filter(Ride.created_at >= week_start, Ride.created_at < week_end)
        except:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    elif period == "monthly" and date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            query = query.filter(
                extract('year', Ride.created_at) == target_date.year,
                extract('month', Ride.created_at) == target_date.month
            )
        except:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Calculate stats
    total_rides = query.count()
    completed_rides = query.filter(Ride.status == "completed").count()
    cancelled_rides = query.filter(Ride.status == "cancelled").count()
    
    # Get payments
    completed = query.filter(Ride.status == "completed").all()
    total_revenue = 0.0
    total_km = 0.0
    total_commission = 0.0
    
    commission_rate = get_commission_rate(db)
    
    for ride in completed:
        fare = float(ride.fare or 0)
        total_revenue += fare
        total_commission += round(fare * commission_rate, 2)
        
        # Calculate distance
        try:
            p = json.loads(ride.pickup_location) if ride.pickup_location else None
            d = json.loads(ride.dropoff_location) if ride.dropoff_location else None
            if p and d and all(k in p for k in ("lat", "lng")) and all(k in d for k in ("lat", "lng")):
                total_km += calculate_distance(float(p["lat"]), float(p["lng"]), float(d["lat"]), float(d["lng"]))
        except Exception:
            continue
    
    driver_earnings = total_revenue - total_commission
    
    return {
        "period": period,
        "date": date,
        "total_rides": total_rides,
        "completed_rides": completed_rides,
        "cancelled_rides": cancelled_rides,
        "total_revenue": round(total_revenue, 2),
        "total_commission": round(total_commission, 2),
        "driver_earnings": round(driver_earnings, 2),
        "total_km": round(total_km, 2),
        "current_balance": float(current_user.current_balance or 0),
        "commission_rate": commission_rate
    }
