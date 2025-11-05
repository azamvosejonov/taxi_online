"""
Qo'shimcha xizmatlar (Additional Services) API endpoint'lari
Barcha foydalanuvchilar uchun ochiq
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import AdditionalService
from schemas import AdditionalServiceResponse

router = APIRouter(
    prefix="/api/v1/services",
    tags=["Services"]
)

@router.get("/available", response_model=List[AdditionalServiceResponse])
def get_available_services(
    db: Session = Depends(get_db)
):
    """
    Mavjud (faol) qo'shimcha xizmatlar ro'yxati
    
    **Kimlar ishlatadi:** Barcha foydalanuvchilar (Dispatcher, Rider, Driver)
    
    **Returns:**
    - Faol xizmatlar ro'yxati (display_order bo'yicha tartiblangan)
    """
    services = db.query(AdditionalService).filter(
        AdditionalService.is_active == True
    ).order_by(AdditionalService.display_order).all()
    
    return services

@router.get("/all", response_model=List[AdditionalServiceResponse])
def get_all_services(
    db: Session = Depends(get_db)
):
    """
    Barcha qo'shimcha xizmatlar (faol va faol emas)
    
    **Kimlar ishlatadi:** Barcha foydalanuvchilar
    
    **Returns:**
    - Barcha xizmatlar ro'yxati
    """
    services = db.query(AdditionalService).order_by(
        AdditionalService.display_order
    ).all()
    
    return services

@router.get("/{service_id}", response_model=AdditionalServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Xizmat ma'lumotlarini olish
    
    **Parameters:**
    - service_id: Xizmat ID raqami
    
    **Returns:**
    - Xizmat ma'lumotlari
    """
    service = db.query(AdditionalService).filter(
        AdditionalService.id == service_id
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return service
