"""
Admin router - Administrative functionality for Royal Taxi API
"""
import calendar
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func, extract, and_
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Ride, Payment, SystemConfig, Notification
from schemas import UserResponse, SystemStats, DailyAnalytics, WeeklyAnalytics, MonthlyAnalytics, YearlyAnalytics, IncomeStats, AdminNotifyRequest
from routers.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    users = db.query(User).all()
    # Convert None boolean values to False for each user
    for user in users:
        if user.is_admin is None:
            user.is_admin = False
        if user.is_dispatcher is None:
            user.is_dispatcher = False
        if user.is_driver is None:
            user.is_driver = False
        if user.is_active is None:
            user.is_active = True
        if user.is_approved is None:
            user.is_approved = False
    return users


@router.get("/stats")
async def get_system_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    total_users = db.query(User).count()
    total_drivers = db.query(User).filter(User.is_driver == True).count()
    total_rides = db.query(Ride).count()
    completed_rides = db.query(Ride).filter(Ride.status == "completed").count()
    total_revenue = db.query(Payment).filter(
        Payment.status == "completed"
    ).with_entities(func.sum(Payment.amount)).scalar() or 0

    return {
        "total_users": total_users,
        "total_drivers": total_drivers,
        "total_rides": total_rides,
        "completed_rides": completed_rides,
        "total_revenue": total_revenue
    }


@router.get("/analytics/daily")
async def get_daily_analytics(
    date: str = None,  # YYYY-MM-DD format
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily analytics (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if not date:
        today = datetime.now().date()
        date = today.isoformat()

    # Daily ride statistics
    daily_rides = db.query(Ride).filter(
        func.date(Ride.created_at) == date
    ).all()

    completed_rides = [r for r in daily_rides if r.status == "completed"]
    total_revenue = sum(r.fare for r in completed_rides if r.fare)

    # Daily user registrations
    daily_users = db.query(User).filter(
        func.date(User.created_at) == date
    ).count()

    # Daily driver approvals
    daily_approvals = db.query(User).filter(
        func.date(User.approved_at) == date,
        User.is_approved == True
    ).count()

    return {
        "date": date,
        "total_rides": len(daily_rides),
        "completed_rides": len(completed_rides),
        "cancelled_rides": len([r for r in daily_rides if r.status == "cancelled"]),
        "total_revenue": total_revenue,
        "new_users": daily_users,
        "driver_approvals": daily_approvals,
        "average_ride_distance": sum(r.distance for r in completed_rides) / len(completed_rides) if completed_rides else 0,
        "average_ride_fare": total_revenue / len(completed_rides) if completed_rides else 0
    }


@router.get("/analytics/weekly")
async def get_weekly_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly analytics (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    weekly_rides = db.query(Ride).filter(
        Ride.created_at >= week_ago
    ).all()

    completed_rides = [r for r in weekly_rides if r.status == "completed"]
    total_revenue = sum(r.fare for r in completed_rides if r.fare)

    # Group by day
    daily_breakdown = {}
    for ride in weekly_rides:
        day = ride.created_at.date().isoformat()
        if day not in daily_breakdown:
            daily_breakdown[day] = {"rides": 0, "revenue": 0}

        daily_breakdown[day]["rides"] += 1
        if ride.status == "completed":
            daily_breakdown[day]["revenue"] += ride.fare or 0

    return {
        "total_rides": len(weekly_rides),
        "completed_rides": len(completed_rides),
        "total_revenue": total_revenue,
        "daily_breakdown": daily_breakdown
    }


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate user account (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    db.commit()

@router.put("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a driver (allow to accept orders)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_approved = True
    user.approved_at = datetime.utcnow()
    user.approved_by = current_user.id
    db.commit()

    return {"message": "User approved", "user_id": user.id}

@router.put("/users/{user_id}/unapprove")
async def unapprove_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_approved = False
    db.commit()

    return {"message": "User unapproved", "user_id": user.id}

    return {"message": "User deactivated successfully"}


@router.put("/users/{user_id}/set-dispatcher")
async def set_user_as_dispatcher(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set user as dispatcher (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_dispatcher = True
    user.is_admin = False  # Remove admin role if they were admin
    db.commit()

    return {"message": "User set as dispatcher", "user_id": user.id}


@router.put("/users/{user_id}/set-admin")
async def set_user_as_admin(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set user as admin (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_admin = True
    user.is_dispatcher = False  # Remove dispatcher role if they were dispatcher
    db.commit()

    return {"message": "User set as admin", "user_id": user.id}


@router.put("/users/{user_id}/remove-roles")
async def remove_user_roles(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove dispatcher/admin roles from user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_dispatcher = False
    user.is_admin = False
    db.commit()

    return {"message": "User roles removed", "user_id": user.id}


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate user account (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()


@router.get("/income/stats")
async def get_income_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive income statistics (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Get today's date
    today = datetime.utcnow().date()
    current_month = today.replace(day=1)
    current_year = today.replace(month=1, day=1)

    # Calculate total revenue
    total_revenue_result = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "completed"
    ).scalar()
    total_revenue = float(total_revenue_result) if total_revenue_result else 0.0

    # Calculate today's revenue
    today_revenue_result = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == "completed",
            func.date(Payment.created_at) == today
        )
    ).scalar()
    today_revenue = float(today_revenue_result) if today_revenue_result else 0.0

    # Calculate current month's revenue
    month_revenue_result = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == "completed",
            extract('year', Payment.created_at) == current_month.year,
            extract('month', Payment.created_at) == current_month.month
        )
    ).scalar()
    month_revenue = float(month_revenue_result) if month_revenue_result else 0.0

    # Calculate current year's revenue
    year_revenue_result = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == "completed",
            extract('year', Payment.created_at) == current_year.year
        )
    ).scalar()
    year_revenue = float(year_revenue_result) if year_revenue_result else 0.0

    # Calculate average daily revenue (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    daily_sums = db.query(
        func.sum(Payment.amount).label('daily_sum')
    ).filter(
        and_(
            Payment.status == "completed",
            Payment.created_at >= thirty_days_ago
        )
    ).group_by(func.date(Payment.created_at)).all()
    
    # Calculate average in Python
    if daily_sums:
        total_daily = sum(float(daily[0]) for daily in daily_sums if daily[0] is not None)
        average_daily_revenue = total_daily / len(daily_sums)
    else:
        average_daily_revenue = 0.0

    # Calculate average monthly revenue (last 12 months)
    twelve_months_ago = today.replace(year=today.year - 1)
    avg_monthly_query = db.query(
        func.avg(month_revenue_result)
    ).filter(
        and_(
            Payment.status == "completed",
            Payment.created_at >= twelve_months_ago
        )
    ).scalar()
    average_monthly_revenue = float(avg_monthly_query) if avg_monthly_query else 0.0

    # Get top earning days (last 30 days)
    top_days_query = db.query(
        func.date(Payment.created_at).label('date'),
        func.sum(Payment.amount).label('revenue')
    ).filter(
        and_(
            Payment.status == "completed",
            Payment.created_at >= thirty_days_ago
        )
    ).group_by(func.date(Payment.created_at)).order_by(
        func.sum(Payment.amount).desc()
    ).limit(10).all()

    top_earning_days = [
        {"date": str(day[0]), "revenue": float(day[1] or 0)}
        for day in top_days_query
    ]

    # Get revenue trend (last 30 days)
    trend_query = db.query(
        func.date(Payment.created_at).label('date'),
        func.sum(Payment.amount).label('revenue')
    ).filter(
        and_(
            Payment.status == "completed",
            Payment.created_at >= thirty_days_ago
        )
    ).group_by(func.date(Payment.created_at)).order_by(func.date(Payment.created_at)).all()

    revenue_trend = [
        {"date": str(day[0]), "revenue": float(day[1] or 0)}
        for day in trend_query
    ]

    return IncomeStats(
        total_revenue=total_revenue,
        today_revenue=today_revenue,
        month_revenue=month_revenue,
        year_revenue=year_revenue,
        average_daily_revenue=average_daily_revenue,
        average_monthly_revenue=average_monthly_revenue,
        top_earning_days=top_earning_days,
        revenue_trend=revenue_trend
    )

@router.get("/income/monthly/{year}/{month}")
async def get_monthly_income(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly income breakdown (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Validate month
    if not (1 <= month <= 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid month. Must be between 1 and 12"
        )

    # Calculate revenue for the month
    month_revenue_result = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == "completed",
            extract('year', Payment.created_at) == year,
            extract('month', Payment.created_at) == month
        )
    ).scalar()
    total_revenue = float(month_revenue_result) if month_revenue_result else 0.0

    # Get daily breakdown
    daily_query = db.query(
        func.date(Payment.created_at).label('date'),
        func.sum(Payment.amount).label('revenue'),
        func.count(Payment.id).label('rides')
    ).filter(
        and_(
            Payment.status == "completed",
            extract('year', Payment.created_at) == year,
            extract('month', Payment.created_at) == month
        )
    ).group_by(func.date(Payment.created_at)).order_by(func.date(Payment.created_at)).all()

    # Convert to dictionary with dates as keys
    daily_breakdown = {
        str(day[0]): {
            "revenue": float(day[1] or 0),
            "rides": day[2] or 0
        }
        for day in daily_query
    }

    # Calculate additional metrics
    total_rides = sum(day[2] or 0 for day in daily_query)
    completed_rides = total_rides  # Since we're only looking at completed payments
    average_daily_revenue = total_revenue / len(daily_query) if daily_query else 0.0

    # Get new users and driver approvals for the month
    new_users = db.query(User).filter(
        and_(
            extract('year', User.created_at) == year,
            extract('month', User.created_at) == month
        )
    ).count()

    driver_approvals = db.query(User).filter(
        and_(
            User.is_driver == True,
            User.is_approved == True,
            extract('year', User.approved_at) == year,
            extract('month', User.approved_at) == month
        )
    ).count()

    return MonthlyAnalytics(
        month=f"{year}-{month:02d}",
        total_rides=total_rides,
        completed_rides=completed_rides,
        total_revenue=total_revenue,
        average_daily_revenue=average_daily_revenue,
        new_users=new_users,
        driver_approvals=driver_approvals,
        daily_breakdown=daily_breakdown
    )

@router.get("/income/yearly/{year}")
async def get_yearly_income(
    year: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get yearly income breakdown (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Calculate total revenue for the year
    year_revenue_result = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == "completed",
            extract('year', Payment.created_at) == year
        )
    ).scalar()
    total_revenue = float(year_revenue_result) if year_revenue_result else 0.0

    # Get monthly breakdown
    monthly_query = db.query(
        extract('month', Payment.created_at).label('month'),
        func.sum(Payment.amount).label('revenue'),
        func.count(Payment.id).label('rides')
    ).filter(
        and_(
            Payment.status == "completed",
            extract('year', Payment.created_at) == year
        )
    ).group_by(extract('month', Payment.created_at)).order_by(
        extract('month', Payment.created_at)
    ).all()

    monthly_breakdown = {}
    total_rides = 0
    for month_data in monthly_query:
        month_name = calendar.month_name[month_data.month]
        monthly_breakdown[month_name] = {
            "revenue": float(month_data.revenue),
            "rides": month_data.rides
        }
        total_rides += month_data.rides

    completed_rides = total_rides
    average_monthly_revenue = total_revenue / 12 if total_revenue > 0 else 0.0

    # Calculate growth rate (compared to previous year)
    prev_year_revenue_result = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == "completed",
            extract('year', Payment.created_at) == year - 1
        )
    ).scalar()
    prev_year_revenue = float(prev_year_revenue_result) if prev_year_revenue_result else 0.0

    if prev_year_revenue > 0:
        growth_rate = ((total_revenue - prev_year_revenue) / prev_year_revenue) * 100
    else:
        growth_rate = 0.0 if total_revenue == 0 else 100.0

    return YearlyAnalytics(
        year=str(year),
        total_rides=total_rides,
        completed_rides=completed_rides,
        total_revenue=total_revenue,
        average_monthly_revenue=average_monthly_revenue,
        monthly_breakdown=monthly_breakdown,
        growth_rate=growth_rate
    )


# --- Config management ---
@router.get("/config/commission-rate")
async def get_commission_rate(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    cfg = db.query(SystemConfig).filter(SystemConfig.key == "commission_rate").first()
    value = float(cfg.value) if cfg else 0.10
    return {"commission_rate": value}


@router.put("/config/commission-rate")
async def set_commission_rate(
    rate: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    if rate < 0 or rate > 1:
        raise HTTPException(status_code=400, detail="Rate must be between 0 and 1 (e.g., 0.10 for 10%)")
    cfg = db.query(SystemConfig).filter(SystemConfig.key == "commission_rate").first()
    if not cfg:
        cfg = SystemConfig(key="commission_rate", value=str(rate))
        db.add(cfg)
    else:
        cfg.value = str(rate)
    db.commit()
    return {"message": "Commission rate updated", "commission_rate": rate}


# --- Notifications ---
@router.post("/notify/all")
async def notify_all_drivers(
    payload: AdminNotifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    drivers = db.query(User).filter(User.is_driver == True, User.is_active == True).all()
    count = 0
    for d in drivers:
        db.add(Notification(user_id=d.id, title=payload.title, body=payload.body, notification_type="promo"))
        count += 1
    db.commit()
    return {"message": "Notifications sent", "count": count}


@router.post("/notify/{driver_id}")
async def notify_driver(
    driver_id: int,
    payload: AdminNotifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    driver = db.query(User).filter(User.id == driver_id, User.is_driver == True).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    db.add(Notification(user_id=driver.id, title=payload.title, body=payload.body, notification_type="promo"))
    db.commit()
    return {"message": "Notification sent"}
