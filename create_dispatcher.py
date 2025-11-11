"""
Dispatcher yaratish skripti
"""
import os
from sqlalchemy.orm import Session
from database import engine, get_db
from models import User
from utils.helpers import hash_password
from datetime import datetime

def create_dispatcher():
    """Dispatcher foydalanuvchi yaratish"""

    # Dispatcher ma'lumotlari
    dispatcher_phone = "+998901234569"
    dispatcher_password = "dispatcher123"

    print(f"Dispatcher yaratish...")
    print(f"Phone: {dispatcher_phone}")
    print(f"Password: {dispatcher_password}")

    # Database session
    db = next(get_db())

    try:
        # Dispatcher mavjudligini tekshirish
        existing_dispatcher = db.query(User).filter(User.phone == dispatcher_phone).first()

        if existing_dispatcher:
            print(f"✅ Dispatcher allaqachon mavjud: {dispatcher_phone}")
            # Dispatcher flaglarini yangilash
            existing_dispatcher.is_dispatcher = True
            existing_dispatcher.is_active = True
            existing_dispatcher.is_approved = True
            db.commit()
            print(f"✅ Dispatcher flaglari yangilandi")
            return existing_dispatcher

        # Yangi dispatcher yaratish
        hashed_password = hash_password(dispatcher_password)

        dispatcher = User(
            phone=dispatcher_phone,
            password=hashed_password,
            full_name="Dispatcher Operator",
            vehicle_type="dispatcher",
            vehicle_number="DISP001",
            license_number="DISP001",
            is_driver=False,
            is_dispatcher=True,
            is_admin=False,
            is_approved=True,
            is_active=True,
            current_balance=0.0,
            required_deposit=0.0,
            rating=5.0,
            total_rides=0,
            language="uz"
        )

        db.add(dispatcher)
        db.commit()
        db.refresh(dispatcher)

        print(f"✅ Dispatcher muvaffaqiyatli yaratildi!")
        print(f"   ID: {dispatcher.id}")
        print(f"   Phone: {dispatcher_phone}")
        print(f"   Password: {dispatcher_password}")

        return dispatcher

    except Exception as e:
        print(f"❌ Xatolik: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    create_dispatcher()
