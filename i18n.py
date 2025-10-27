from babel import Locale
import json
from pathlib import Path

# Translation dictionary
translations = {
    "uz": {
        "welcome": "Xush kelibsiz",
        "ride_booked": "Sayohat buyurtma qilindi",
        "driver_assigned": "Haydovchi tayinlandi",
        "ride_completed": "Sayohat yakunlandi",
        "payment_successful": "To'lov muvaffaqiyatli",
        "profile_updated": "Profil yangilandi",
        "vehicle_registered": "Avtomobil ro'yxatdan o'tkazildi",
        "promo_applied": "Chegirma qo'llanildi",
        "notification_sent": "Bildirishnoma yuborildi"
    },
    "ru": {
        "welcome": "Добро пожаловать",
        "ride_booked": "Поездка забронирована",
        "driver_assigned": "Водитель назначен",
        "ride_completed": "Поездка завершена",
        "payment_successful": "Оплата прошла успешно",
        "profile_updated": "Профиль обновлен",
        "vehicle_registered": "Автомобиль зарегистрирован",
        "promo_applied": "Промокод применен",
        "notification_sent": "Уведомление отправлено"
    },
    "en": {
        "welcome": "Welcome",
        "ride_booked": "Ride booked",
        "driver_assigned": "Driver assigned",
        "ride_completed": "Ride completed",
        "payment_successful": "Payment successful",
        "profile_updated": "Profile updated",
        "vehicle_registered": "Vehicle registered",
        "promo_applied": "Promo code applied",
        "notification_sent": "Notification sent"
    }
}

def get_translation(key: str, language: str = "uz") -> str:
    """Get translation for a key in specified language"""
    return translations.get(language, translations["uz"]).get(key, key)

def get_user_language(user) -> str:
    """Get user's preferred language"""
    return getattr(user, 'language', 'uz') if user else 'uz'

# Enhanced notification function with translations
async def send_localized_push_notification(user_id: int, key: str, data: dict = None, fallback_language: str = "uz"):
    """Send push notification in user's preferred language"""
    try:
        # Get user's language preference
        user = db.query(models.User).filter(models.User.id == user_id).first()
        language = get_user_language(user)

        # Get translation
        title = get_translation(f"{key}_title", language)
        body = get_translation(f"{key}_body", language)

        # Send notification
        return await send_push_notification(user_id, title, body, key, data)

    except Exception as e:
        print(f"Error sending localized notification: {e}")
        return False

# Enhanced API responses with localization
def get_localized_response(key: str, language: str = "uz", **kwargs) -> dict:
    """Get localized API response"""
    base_response = {
        "success": True,
        "message": get_translation(key, language),
        "data": kwargs
    }
    return base_response

# Middleware for language detection
@app.middleware("http")
async def detect_language(request, call_next):
    """Middleware to detect and set user language"""
    # Try to get language from header or query parameter
    language = request.headers.get("Accept-Language", "uz")
    if "?" in str(request.url):
        query_params = str(request.url).split("?")[1]
        if "lang=" in query_params:
            language = query_params.split("lang=")[1].split("&")[0]

    # Store language in request state
    request.state.language = language[:2]  # Get first 2 characters

    response = await call_next(request)
    return response
