# 📚 ROYAL TAXI API - TO'LIQ DOKUMENTATSIYA

Barcha API endpoint'lar haqida batafsil ma'lumot

---

## 📊 UMUMIY MA'LUMOT

**Jami Endpoint'lar:** 75 ta

| Bo'lim | Endpoint'lar soni |
|--------|-------------------|
| 🔐 Autentifikatsiya | 5 ta |
| 👤 Foydalanuvchi | 6 ta |
| 👔 Admin | 24 ta |
| 📞 Dispetcher | 7 ta |
| 🚗 Haydovchi | 10 ta |
| 🧑‍💼 Yo'lovchi | 6 ta |
| 📁 Fayllar | 4 ta |
| 🛍️ Xizmatlar | 3 ta |
| 🔌 WebSocket | 3 ta |
| ✅ Health Check | 2 ta |

**Base URL:** `http://localhost:8000`

**API Versiya:** `v1`

**Authorization:** Bearer Token (JWT)

---

## 📋 MUNDARIJA

1. [Autentifikatsiya (Authentication)](#1-autentifikatsiya-authentication) - 5 endpoint
2. [Foydalanuvchi (Users)](#2-foydalanuvchi-users) - 6 endpoint
3. [Admin](#3-admin) - 24 endpoint
4. [Dispetcher (Dispatcher)](#4-dispetcher-dispatcher) - 7 endpoint
5. [Haydovchi (Driver)](#5-haydovchi-driver) - 10 endpoint
6. [Yo'lovchi (Rider)](#6-yolovchi-rider) - 6 endpoint
7. [Fayllar (Files)](#7-fayllar-files) - 4 endpoint
8. [Xizmatlar (Services)](#8-xizmatlar-services) - 3 endpoint
9. [WebSocket](#9-websocket) - 3 endpoint

---

## 🔐 1. AUTENTIFIKATSIYA (Authentication)

Base URL: `/api/v1/auth`

### 1.1. Kirish (Login)

**Endpoint:** `POST /api/v1/auth/login`

**Tavsif:** Telefon va parol bilan tizimga kirish

**Request Body:**
```json
{
  "phone": "+998901234567",
  "password": "strongpassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": 1,
    "phone": "+998901234567",
    "full_name": "Falonchi Falonchiyev",
    "is_driver": true,
    "is_dispatcher": false,
    "is_admin": false,
    "is_approved": true,
    "current_balance": 50000.0,
    "rating": 4.8
  }
}
```

---

### 1.3. Chiqish (Logout)

**Endpoint:** `POST /api/v1/auth/logout`

**Authorization:** Bearer Token kerak

**Response (200 OK):**
```json
{
  "message": "Successfully logged out",
  "detail": "Token removed from client. Please delete the token from your storage.",
  "user": {
    "id": 1,
    "phone": "+998901234567",
    "full_name": "Falonchi Falonchiyev"
  }
}
```

---

### 1.4. OTP yuborish (1-qadam)

**Endpoint:** `POST /api/v1/auth/send-otp`

**Tavsif:** Telefon raqamga 6 raqamli SMS kod yuboradi

**Request Body:**
```json
{
  "phone": "+998901234567"
}
```

**Response (200 OK):**
```json
{
  "message": "Tasdiqlash kodi +998901234567 raqamiga yuborildi. Kod 5 daqiqa davomida amal qiladi.",
  "phone": "+998901234567",
  "expires_in": 300,
  "otp_code": "123456"
}
```

*Eslatma: `otp_code` faqat development rejimida qaytariladi*

---

### 1.5. OTP tasdiqlash (2-qadam)

**Endpoint:** `POST /api/v1/auth/verify-otp`

**Tavsif:** SMS orqali kelgan kodni tekshiradi

**Request Body:**
```json
{
  "phone": "+998901234567",
  "otp_code": "123456"
}
```

**Response (200 OK):**
```json
{
  "message": "Telefon raqam muvaffaqiyatli tasdiqlandi!",
  "phone": "+998901234567",
  "verified": true,
  "needs_profile_completion": true
}
```

---

### 1.6. Profilni to'ldirish (3-qadam)

**Endpoint:** `POST /api/v1/auth/complete-profile`

**Tavsif:** OTP tasdiqlanganidan keyin profil ma'lumotlarini to'ldiradi

**Request Body:**
```json
{
  "phone": "+998901234567",
  "first_name": "Falonchi",
  "last_name": "Falonchiyev",
  "gender": "Erkak",
  "date_of_birth": "1990-01-01",
  "vehicle_make": "Chevrolet",
  "vehicle_color": "Qora",
  "position": "Haydovchi",
  "license_plate": "01A123AA",
  "tech_passport": "AA1234567"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": 1,
    "phone": "+998901234567",
    "full_name": "Falonchi Falonchiyev",
    "vehicle_model": "Chevrolet",
    "current_balance": 0.0,
    "rating": 5.0
  }
}
```

---

## 👤 2. FOYDALANUVCHI (Users)

Base URL: `/api/v1/users`

### 2.1. Profilni ko'rish

**Endpoint:** `GET /api/v1/users/profile`

**Authorization:** Bearer Token kerak

**Response (200 OK):**
```json
{
  "id": 1,
  "phone": "+998901234567",
  "full_name": "Falonchi Falonchiyev",
  "is_driver": true,
  "is_dispatcher": false,
  "is_admin": false,
  "is_active": true,
  "is_approved": true,
  "vehicle_model": "Chevrolet",
  "vehicle_color": "Qora",
  "vehicle_number": "01A123AA",
  "rating": 4.8,
  "total_rides": 150,
  "current_balance": 50000.0,
  "created_at": "2024-01-01T10:00:00"
}
```

---

### 2.2. Profilni yangilash

**Endpoint:** `PUT /api/v1/users/profile`

**Authorization:** Bearer Token kerak

**Request Body:**
```json
{
  "full_name": "Yangi Ism Familiya",
  "emergency_contact": "+998901111111",
  "vehicle_model": "Nexia",
  "vehicle_number": "01B456BB"
}
```

**Response (200 OK):** Yangilangan profil

---

### 2.3. Profil rasmini yuklash

**Endpoint:** `POST /api/v1/users/profile-picture`

**Authorization:** Bearer Token kerak

**Request:** multipart/form-data
- `file`: Rasm fayli (JPG, PNG)

**Response (200 OK):**
```json
{
  "message": "Profile picture uploaded successfully",
  "file_path": "/uploads/profiles/user_1_20240115.jpg"
}
```

---

### 2.4. Balansni ko'rish

**Endpoint:** `GET /api/v1/users/balance`

**Authorization:** Bearer Token kerak

**Response (200 OK):**
```json
{
  "current_balance": 50000.0,
  "required_deposit": 0.0,
  "is_approved": true
}
```

---

### 2.5. Safar tarixini ko'rish

**Endpoint:** `GET /api/v1/users/rides`

**Authorization:** Bearer Token kerak

**Response (200 OK):**
```json
{
  "message": "User rides endpoint - to be implemented"
}
```

---

### 2.6. Tranzaksiya tarixini ko'rish

**Endpoint:** `GET /api/v1/users/transactions`

**Authorization:** Bearer Token kerak

**Response (200 OK):**
```json
{
  "message": "User transactions endpoint - to be implemented"
}
```

---

## 👔 3. ADMIN

Base URL: `/api/v1/admin`

### 3.1. Barcha foydalanuvchilar

**Endpoint:** `GET /api/v1/admin/users`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "phone": "+998901234567",
    "full_name": "Haydovchi 1",
    "is_driver": true,
    "is_approved": true,
    "current_balance": 50000.0,
    "rating": 4.8
  },
  ...
]
```

---

### 3.2. Statistika

**Endpoint:** `GET /api/v1/admin/stats`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "total_users": 250,
  "total_drivers": 100,
  "total_rides": 5000,
  "completed_rides": 4500,
  "total_revenue": 25000000.0
}
```

---

### 3.3. Kunlik tahlil

**Endpoint:** `GET /api/v1/admin/analytics/daily?date=2024-01-15`

**Authorization:** Admin huquqi kerak

**Query Parameters:**
- `date` (optional): YYYY-MM-DD format, default: bugun

**Response (200 OK):**
```json
{
  "date": "2024-01-15",
  "total_rides": 120,
  "completed_rides": 110,
  "cancelled_rides": 10,
  "total_revenue": 5500000.0,
  "new_users": 15,
  "driver_approvals": 5,
  "average_ride_distance": 8.5,
  "average_ride_fare": 50000.0
}
```

---

### 3.4. Haftalik tahlil

**Endpoint:** `GET /api/v1/admin/analytics/weekly`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "total_rides": 850,
  "completed_rides": 800,
  "total_revenue": 40000000.0,
  "daily_breakdown": {
    "2024-01-15": {"rides": 120, "revenue": 6000000.0},
    "2024-01-16": {"rides": 125, "revenue": 6250000.0}
  }
}
```

---

### 3.5. Haydovchini tasdiqlash

**Endpoint:** `PUT /api/v1/admin/users/{user_id}/approve`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "message": "User approved",
  "user_id": 5
}
```

---

### 3.6. Haydovchini bloklash

**Endpoint:** `PUT /api/v1/admin/users/{user_id}/deactivate`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "message": "User deactivated successfully"
}
```

---

### 3.7. Haydovchini rad etish

**Endpoint:** `PUT /api/v1/admin/users/{user_id}/unapprove`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "message": "User unapproved",
  "user_id": 5
}
```

---

### 3.8. Dispetcher qilish

**Endpoint:** `PUT /api/v1/admin/users/{user_id}/set-dispatcher`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "message": "User set as dispatcher",
  "user_id": 3
}
```

---

### 3.9. Admin qilish

**Endpoint:** `PUT /api/v1/admin/users/{user_id}/set-admin`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "message": "User set as admin",
  "user_id": 2
}
```

---

### 3.10. Rollarni olib tashlash

**Endpoint:** `PUT /api/v1/admin/users/{user_id}/remove-roles`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "message": "User roles removed",
  "user_id": 7
}
```

---

### 3.11. Foydalanuvchini faollashtirish

**Endpoint:** `PUT /api/v1/admin/users/{user_id}/activate`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "message": "User activated successfully"
}
```

---

### 3.12. Daromad statistikasi

**Endpoint:** `GET /api/v1/admin/income/stats`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "total_revenue": 50000000.0,
  "today_revenue": 500000.0,
  "month_revenue": 15000000.0,
  "year_revenue": 48000000.0,
  "average_daily_revenue": 450000.0,
  "average_monthly_revenue": 4000000.0,
  "top_earning_days": [
    {"date": "2024-01-10", "revenue": 800000.0},
    {"date": "2024-01-05", "revenue": 750000.0}
  ],
  "revenue_trend": [
    {"date": "2024-01-01", "revenue": 400000.0},
    {"date": "2024-01-02", "revenue": 450000.0}
  ]
}
```

---

### 3.13. Oylik daromad

**Endpoint:** `GET /api/v1/admin/income/monthly/{year}/{month}`

**Authorization:** Admin huquqi kerak

**Path Parameters:**
- `year`: Yil (masalan, 2024)
- `month`: Oy (1-12)

**Response (200 OK):**
```json
{
  "month": "2024-01",
  "total_rides": 450,
  "completed_rides": 430,
  "total_revenue": 15000000.0,
  "average_daily_revenue": 500000.0,
  "new_users": 25,
  "driver_approvals": 8,
  "daily_breakdown": {
    "2024-01-01": {"revenue": 450000.0, "rides": 15},
    "2024-01-02": {"revenue": 480000.0, "rides": 16}
  }
}
```

---

### 3.14. Yillik daromad

**Endpoint:** `GET /api/v1/admin/income/yearly/{year}`

**Authorization:** Admin huquqi kerak

**Path Parameters:**
- `year`: Yil (masalan, 2024)

**Response (200 OK):**
```json
{
  "year": "2024",
  "total_rides": 5400,
  "completed_rides": 5100,
  "total_revenue": 180000000.0,
  "average_monthly_revenue": 15000000.0,
  "monthly_breakdown": {
    "January": {"revenue": 14000000.0, "rides": 420},
    "February": {"revenue": 15500000.0, "rides": 465}
  },
  "growth_rate": 25.5
}
```

---

### 3.15. Komissiya stavkasini ko'rish

**Endpoint:** `GET /api/v1/admin/config/commission-rate`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "commission_rate": 0.10
}
```

---

### 3.16. Komissiya stavkasini o'rnatish

**Endpoint:** `PUT /api/v1/admin/config/commission-rate?rate=0.10`

**Authorization:** Admin huquqi kerak

**Query Parameters:**
- `rate`: 0.0 dan 1.0 gacha (masalan, 0.10 = 10%)

**Response (200 OK):**
```json
{
  "message": "Commission rate updated",
  "commission_rate": 0.10
}
```

---

### 3.9. Narxlarni ko'rish

**Endpoint:** `GET /api/v1/admin/pricing`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "economy": {
    "base_fare": 10000,
    "per_km_rate": 2000,
    "per_minute_rate": 500
  },
  "comfort": {
    "base_fare": 15000,
    "per_km_rate": 3000,
    "per_minute_rate": 750
  },
  "business": {
    "base_fare": 25000,
    "per_km_rate": 5000,
    "per_minute_rate": 1000
  },
  "commission_rate": 0.10
}
```

---

### 3.10. Narxni yangilash

**Endpoint:** `PUT /api/v1/admin/pricing/{vehicle_type}`

**Authorization:** Admin huquqi kerak

**Path Parameters:**
- `vehicle_type`: economy, comfort, yoki business

**Request Body:**
```json
{
  "vehicle_type": "economy",
  "base_fare": 12000,
  "per_km_rate": 2500,
  "per_minute_rate": 600
}
```

**Response (200 OK):**
```json
{
  "message": "Economy narxlari yangilandi",
  "vehicle_type": "economy",
  "pricing": {
    "base_fare": 12000,
    "per_km_rate": 2500,
    "per_minute_rate": 600
  }
}
```

---

### 3.17. Barcha haydovchilarga xabar

**Endpoint:** `POST /api/v1/admin/notify/all`

**Authorization:** Admin huquqi kerak

**Request Body:**
```json
{
  "title": "Muhim xabar!",
  "body": "Ertaga tizim yangilanadi"
}
```

**Response (200 OK):**
```json
{
  "message": "Notifications sent",
  "count": 150
}
```

---

### 3.18. Haydovchiga xabar yuborish

**Endpoint:** `POST /api/v1/admin/notify/{driver_id}`

**Authorization:** Admin huquqi kerak

**Path Parameters:**
- `driver_id`: Haydovchi ID raqami

**Request Body:**
```json
{
  "title": "Shaxsiy xabar",
  "body": "Sizning hisobingiz tekshirilmoqda"
}
```

**Response (200 OK):**
```json
{
  "message": "Notification sent"
}
```

---

### 3.19. Narxni hisoblash (Preview)

**Endpoint:** `GET /api/v1/admin/pricing/calculate`

**Authorization:** Admin huquqi kerak

**Query Parameters:**
- `distance`: Masofa (km)
- `duration`: Vaqt (daqiqa)
- `vehicle_type`: economy, comfort, yoki business

**Misol:** `GET /api/v1/admin/pricing/calculate?distance=10&duration=20&vehicle_type=economy`

**Response (200 OK):**
```json
{
  "vehicle_type": "economy",
  "distance_km": 10.0,
  "duration_minutes": 20,
  "breakdown": {
    "base_fare": 10000,
    "distance_cost": 20000,
    "time_cost": 10000
  },
  "total_fare": 40000.0,
  "commission_rate": 0.10,
  "commission_amount": 4000.0,
  "driver_earnings": 36000.0,
  "formula": "10000 + (10 × 2000) + (20 × 500) = 40000.0 so'm"
}
```

---

### 3.20. Barcha xizmatlarni ko'rish

**Endpoint:** `GET /api/v1/admin/services`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "konditsioner",
    "name_uz": "Konditsioner",
    "name_ru": "Кондиционер",
    "icon": "❄️",
    "price": 5000.0,
    "is_active": true,
    "display_order": 1,
    "description": "Avtomobilni sovutish",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
  }
]
```

---

### 3.21. Xizmat yaratish

**Endpoint:** `POST /api/v1/admin/services`

**Authorization:** Admin huquqi kerak

**Request Body:**
```json
{
  "name": "yukkona",
  "name_uz": "Yukkona",
  "name_ru": "Багажник",
  "icon": "🧳",
  "price": 3000.0,
  "is_active": true,
  "display_order": 2,
  "description": "Katta yukkona"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "name": "yukkona",
  "name_uz": "Yukkona",
  "name_ru": "Багажник",
  "icon": "🧳",
  "price": 3000.0,
  "is_active": true,
  "display_order": 2,
  "description": "Katta yukkona",
  "created_at": "2024-01-15T11:00:00",
  "updated_at": "2024-01-15T11:00:00"
}
```

---

### 3.22. Xizmatni yangilash

**Endpoint:** `PUT /api/v1/admin/services/{service_id}`

**Authorization:** Admin huquqi kerak

**Request Body:**
```json
{
  "price": 6000.0,
  "is_active": false
}
```

**Response (200 OK):** Yangilangan xizmat

---

### 3.23. Xizmatni o'chirish

**Endpoint:** `DELETE /api/v1/admin/services/{service_id}`

**Authorization:** Admin huquqi kerak

**Response (200 OK):**
```json
{
  "message": "Service deleted successfully",
  "service_id": 2
}
```

---

### 3.24. Xizmatni faollashtirish/o'chirish

**Endpoint:** `PUT /api/v1/admin/services/{service_id}/toggle`

**Authorization:** Admin huquqi kerak

**Request Body:**
```json
{
  "is_active": true
}
```

**Response (200 OK):** Yangilangan xizmat

---

## 📞 4. DISPETCHER (Dispatcher)

Base URL: `/api/v1/dispatcher`

### 4.1. Buyurtma yaratish

**Endpoint:** `POST /api/v1/dispatcher/order`

**Authorization:** Dispetcher huquqi kerak

**Request Body:**
```json
{
  "customer_phone": "+998901234567",
  "customer_name": "Mijoz Ismi",
  "pickup_location": {
    "lat": 41.311151,
    "lng": 69.279737,
    "address": "Amir Temur ko'chasi 1",
    "city": "Toshkent"
  },
  "dropoff_location": {
    "lat": 41.326418,
    "lng": 69.228341,
    "address": "Chorsu bozori",
    "city": "Toshkent"
  },
  "vehicle_type": "economy"
}
```

**Response (200 OK):**
```json
{
  "ride": {
    "id": 101,
    "customer_id": 5,
    "status": "pending",
    "fare": 35000.0,
    "distance": 12.5,
    "duration": 20,
    "vehicle_type": "economy",
    "pickup_location": {...},
    "dropoff_location": {...},
    "created_at": "2024-01-15T10:00:00"
  },
  "broadcasted_to": 8
}
```

---

### 4.2. Qayta e'lon qilish

**Endpoint:** `POST /api/v1/dispatcher/order/{ride_id}/broadcast`

**Authorization:** Dispetcher huquqi kerak

**Request Body (optional):**
```json
{
  "radius_km": 5.0
}
```

**Response (200 OK):**
```json
{
  "message": "Broadcasted",
  "count": 12,
  "driver_ids": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
}
```

---

### 4.3. Depozit qo'shish

**Endpoint:** `POST /api/v1/dispatcher/deposit`

**Authorization:** Dispetcher huquqi kerak

**Request Body:**
```json
{
  "driver_id": 5,
  "amount": 100000.0
}
```

**Response (200 OK):**
```json
{
  "message": "Deposit added",
  "driver_id": 5,
  "new_balance": 150000.0
}
```

---

### 4.4. Haydovchini bloklash

**Endpoint:** `POST /api/v1/dispatcher/block/{driver_id}`

**Authorization:** Dispetcher huquqi kerak

**Response (200 OK):**
```json
{
  "message": "Driver blocked"
}
```

---

### 4.5. Haydovchini blokdan chiqarish

**Endpoint:** `POST /api/v1/dispatcher/unblock/{driver_id}`

**Authorization:** Dispetcher huquqi kerak

**Response (200 OK):**
```json
{
  "message": "Driver unblocked"
}
```

---

### 4.6. Haydovchilarning joylashuvlari

**Endpoint:** `GET /api/v1/dispatcher/drivers/locations`

**Authorization:** Dispetcher huquqi kerak

**Response (200 OK):**
```json
{
  "drivers": [
    {
      "id": 1,
      "full_name": "Haydovchi 1",
      "phone": "+998901234567",
      "vehicle_number": "01A123AA",
      "vehicle_model": "Chevrolet",
      "is_active": true,
      "is_approved": true,
      "current_balance": 50000.0,
      "location": {
        "lat": 41.311151,
        "lng": 69.279737
      }
    },
    ...
  ]
}
```

---

### 4.7. Buyurtmani bekor qilish

**Endpoint:** `POST /api/v1/dispatcher/cancel/{ride_id}`

**Authorization:** Dispetcher huquqi kerak

**Response (200 OK):**
```json
{
  "message": "Order cancelled"
}
```

---

## 🚗 5. HAYDOVCHI (Driver)

Base URL: `/api/v1/driver`

### 5.1. Xizmat holatini yangilash

**Endpoint:** `POST /api/v1/driver/status`

**Authorization:** Haydovchi huquqi kerak

**Request Body:**
```json
{
  "is_on_duty": true,
  "lat": 41.311151,
  "lng": 69.279737,
  "city": "Toshkent"
}
```

**Response (200 OK):**
```json
{
  "message": "Status updated",
  "is_on_duty": true
}
```

---

### 5.2. Buyurtmani qabul qilish

**Endpoint:** `POST /api/v1/driver/rides/{ride_id}/accept`

**Authorization:** Haydovchi huquqi kerak

**Shartlar:**
- Haydovchi tasdiqlangan bo'lishi kerak
- Xizmatda (on-duty) bo'lishi kerak
- Depozit ijobiy bo'lishi kerak

**Response (200 OK):**
```json
{
  "message": "Ride accepted"
}
```

---

### 5.3. Safarga chiqish

**Endpoint:** `POST /api/v1/driver/rides/{ride_id}/start`

**Authorization:** Haydovchi huquqi kerak

**Response (200 OK):**
```json
{
  "message": "Ride started"
}
```

---

### 5.4. Safarni yakunlash

**Endpoint:** `POST /api/v1/driver/rides/{ride_id}/complete`

**Authorization:** Haydovchi huquqi kerak

**Request Body (optional):**
```json
{
  "dropoff_location": {
    "lat": 41.326418,
    "lng": 69.228341,
    "address": "Chorsu bozori",
    "city": "Toshkent"
  },
  "final_fare": 40000.0
}
```

**Response (200 OK):**
```json
{
  "message": "Ride completed",
  "final_fare": 40000.0,
  "commission_rate": 0.10,
  "commission": 4000.0,
  "remaining_deposit": 46000.0
}
```

---

### 5.5. Statistika

**Endpoint:** `GET /api/v1/driver/stats`

**Authorization:** Haydovchi huquqi kerak

**Response (200 OK):**
```json
{
  "total_completed": 150,
  "total_accepted": 165,
  "total_revenue": 7500000.0,
  "total_km": 1250.5,
  "current_balance": 50000.0
}
```

---

### 5.6. Tariflarni ko'rish

**Endpoint:** `GET /api/v1/driver/pricing`

**Authorization:** Haydovchi huquqi kerak

**Response (200 OK):**
```json
{
  "economy": {
    "base_fare": 10000,
    "per_km_rate": 2000,
    "per_minute_rate": 500
  },
  "comfort": {
    "base_fare": 15000,
    "per_km_rate": 3000,
    "per_minute_rate": 750
  },
  "business": {
    "base_fare": 25000,
    "per_km_rate": 5000,
    "per_minute_rate": 1000
  },
  "commission_rate": 0.10
}
```

---

### 5.7. Safar tarixi

**Endpoint:** `GET /api/v1/driver/rides/history?page=1&limit=20`

**Authorization:** Haydovchi huquqi kerak

**Query Parameters:**
- `page`: Sahifa raqami (default: 1)
- `limit`: Har sahifada nechta (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "rides": [
    {
      "id": 101,
      "customer_id": 5,
      "status": "completed",
      "fare": 35000.0,
      "duration": 20,
      "vehicle_type": "economy",
      "pickup_location": {...},
      "dropoff_location": {...},
      "created_at": "2024-01-15T10:00:00",
      "completed_at": "2024-01-15T10:20:00"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

---

### 5.8. Taxometer - Narxni hisoblash

**Endpoint:** `GET /api/v1/driver/calculate-fare`

**Authorization:** Haydovchi huquqi kerak

**Query Parameters:**
- `distance`: Masofa (km)
- `duration`: Vaqt (daqiqa)
- `vehicle_type`: economy, comfort, yoki business (default: economy)

**Misol:** `GET /api/v1/driver/calculate-fare?distance=10&duration=20&vehicle_type=economy`

**Response (200 OK):**
```json
{
  "vehicle_type": "economy",
  "distance_km": 10.0,
  "duration_minutes": 20,
  "breakdown": {
    "base_fare": 10000,
    "distance_cost": 20000,
    "time_cost": 10000
  },
  "total_fare": 40000.0,
  "commission_rate": 0.10,
  "commission_amount": 4000.0,
  "driver_earnings": 36000.0,
  "formula": "10000 + (10 × 2000) + (20 × 500) = 40000.0 so'm"
}
```

---

### 5.9. Xabarlar tarixi

**Endpoint:** `GET /api/v1/driver/notifications?page=1&limit=20`

**Authorization:** Haydovchi huquqi kerak

**Query Parameters:**
- `page`: Sahifa raqami (default: 1)
- `limit`: Har sahifada nechta (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "notifications": [
    {
      "id": 1,
      "title": "Yangi narxlar!",
      "body": "Ertaga tizim yangilanadi",
      "notification_type": "promo",
      "is_read": false,
      "created_at": "2024-01-15T10:00:00"
    },
    {
      "id": 2,
      "title": "ASSALOMU ALAYKUM",
      "body": "ERTAGA 1-SENTIYABR 2025-YIL SANASIDA...",
      "notification_type": "emergency",
      "is_read": true,
      "created_at": "2024-08-31T16:49:00"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

---

### 5.10. Batafsil statistika

**Endpoint:** `GET /api/v1/driver/stats/detailed?period=daily&date=2025-10-12`

**Authorization:** Haydovchi huquqi kerak

**Query Parameters:**
- `period`: all, daily, weekly, monthly (default: all)
- `date`: YYYY-MM-DD format (optional, period uchun zarur)

**Response (200 OK):**
```json
{
  "period": "daily",
  "date": "2025-10-12",
  "total_rides": 5,
  "completed_rides": 4,
  "cancelled_rides": 1,
  "total_revenue": 200000.0,
  "total_commission": 20000.0,
  "driver_earnings": 180000.0,
  "total_km": 45.5,
  "current_balance": 50000.0,
  "commission_rate": 0.10
}
```

**Misol so'rovlar:**
- Kunlik: `GET /api/v1/driver/stats/detailed?period=daily&date=2025-10-12`
- Haftalik: `GET /api/v1/driver/stats/detailed?period=weekly&date=2025-10-12`
- Oylik: `GET /api/v1/driver/stats/detailed?period=monthly&date=2025-10-01`
- Barchasi: `GET /api/v1/driver/stats/detailed?period=all`

---

## 🧑‍💼 6. YO'LOVCHI (Rider)

Base URL: `/api/v1/rider`

### 6.1. Hozirgi safarni ko'rish

**Endpoint:** `GET /api/v1/rider/current-ride`

**Authorization:** Bearer Token kerak

**Response (200 OK):**
```json
{
  "id": 101,
  "customer_id": 5,
  "rider_id": 1,
  "driver_id": 3,
  "status": "in_progress",
  "fare": 35000.0,
  "distance": 12.5,
  "duration": 20,
  "vehicle_type": "economy",
  "pickup_location": {...},
  "dropoff_location": {...},
  "created_at": "2024-01-15T10:00:00"
}
```

---

### 6.2. Safar ma'lumotlarini ko'rish

**Endpoint:** `GET /api/v1/rider/ride/{ride_id}`

**Authorization:** Bearer Token kerak

**Response (200 OK):**
```json
{
  "id": 101,
  "customer_id": 5,
  "rider_id": 1,
  "driver_id": 3,
  "status": "in_progress",
  "fare": 35000.0,
  "distance": 12.5,
  "duration": 20,
  "vehicle_type": "economy",
  "pickup_location": {...},
  "dropoff_location": {...},
  "created_at": "2024-01-15T10:00:00"
}
```

---

### 6.3. Safar holatini kuzatish

**Endpoint:** `GET /api/v1/rider/ride/{ride_id}/status`

**Authorization:** Bearer Token kerak

**Response (200 OK):**
```json
{
  "ride_id": 101,
  "status": "in_progress",
  "driver_id": 3,
  "driver_location": {
    "lat": 41.315000,
    "lng": 69.275000
  },
  "driver_status": "on_duty",
  "current_fare": 35000.0,
  "estimated_remaining_cost": 15000.0,
  "distance_traveled": 8.2,
  "time_remaining_minutes": 8,
  "updated_at": "2024-01-15T10:15:00"
}
```

---

### 6.4. Haydovchi joylashuvini olish

**Endpoint:** `GET /api/v1/rider/ride/{ride_id}/location`

**Authorization:** Bearer Token kerak

**Response (200 OK):**
```json
{
  "driver_id": 3,
  "driver_name": "Haydovchi 3",
  "vehicle_number": "01C789CC",
  "vehicle_model": "Nexia",
  "location": {
    "lat": 41.315000,
    "lng": 69.275000
  },
  "last_updated": "2024-01-15T10:15:00"
}
```

---

### 6.5. Safar tarixini ko'rish

**Endpoint:** `GET /api/v1/rider/rides/history?page=1&limit=20`

**Authorization:** Bearer Token kerak

**Query Parameters:**
- `page`: Sahifa raqami (default: 1)
- `limit`: Har sahifada nechta (default: 20)

**Response (200 OK):**
```json
{
  "rides": [...],
  "total": 50,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

---

### 6.6. Safarni bekor qilish

**Endpoint:** `POST /api/v1/rider/ride/{ride_id}/cancel`

**Authorization:** Bearer Token kerak

**Shart:** Faqat "pending" yoki "accepted" holatlarda bekor qilish mumkin

**Response (200 OK):**
```json
{
  "message": "Ride cancelled successfully",
  "ride_id": 101
}
```

---

## 📁 7. FAYLLAR (Files)

Base URL: `/api/v1/files`

### 7.1. Profil rasmini yuklash

**Endpoint:** `POST /api/v1/files/profile-picture`

**Authorization:** Bearer Token kerak

**Request:** multipart/form-data
- `file`: Rasm fayli (JPG, PNG)

**Response (200 OK):**
```json
{
  "message": "Profile picture uploaded successfully",
  "file_path": "/uploads/profiles/user_1_20240115.jpg"
}
```

---

### 7.2. Hujjatlarni yuklash

**Endpoint:** `POST /api/v1/files/driver-documents`

**Authorization:** Haydovchi huquqi kerak

**Request:** multipart/form-data
- `license_file`: Haydovchilik guvohnomasi
- `insurance_file`: Sug'urta
- `vehicle_file`: Texpassport

**Response (200 OK):**
```json
{
  "message": "Documents uploaded successfully",
  "uploaded_files": {
    "license": "/uploads/driver_docs/license_user_1.pdf",
    "insurance": "/uploads/driver_docs/insurance_user_1.pdf",
    "vehicle": "/uploads/driver_docs/vehicle_user_1.pdf"
  }
}
```

---

### 7.3. Fayl yuklash (umumiy)

**Endpoint:** `POST /api/v1/files/upload/{folder}`

**Authorization:** Bearer Token kerak

**Path Parameters:**
- `folder`: Papka nomi (masalan: profiles, documents, invoices)

**Request:** multipart/form-data
- `file`: Yuklash uchun fayl

**Response (200 OK):**
```json
{
  "message": "File uploaded successfully",
  "file_path": "/uploads/documents/file_20240115.pdf",
  "folder": "documents"
}
```

---

### 7.4. Faylni ko'rish

**Endpoint:** `GET /api/v1/files/uploads/{folder}/{filename}`

**Authorization:** Bearer Token kerak

**Path Parameters:**
- `folder`: Papka nomi
- `filename`: Fayl nomi

**Response (200 OK):**
```json
{
  "message": "File serving endpoint",
  "file_path": "/uploads/documents/file_20240115.pdf",
  "note": "Implement actual file serving based on your needs"
}
```

---

## 🛍️ 8. XIZMATLAR (Services)

Base URL: `/api/v1/services`

### 8.1. Mavjud xizmatlar

**Endpoint:** `GET /api/v1/services/available`

**Authorization:** Yo'q (ochiq endpoint)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "konditsioner",
    "name_uz": "Konditsioner",
    "name_ru": "Кондиционер",
    "icon": "❄️",
    "price": 5000.0,
    "is_active": true,
    "display_order": 1,
    "description": "Avtomobilni sovutish",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
  },
  {
    "id": 2,
    "name": "yukkona",
    "name_uz": "Yukkona",
    "name_ru": "Багажник",
    "icon": "🧳",
    "price": 3000.0,
    "is_active": true,
    "display_order": 2,
    "description": "Katta yukkona",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
  }
]
```

---

### 8.2. Barcha xizmatlar

**Endpoint:** `GET /api/v1/services/all`

**Authorization:** Yo'q (ochiq endpoint)

**Response (200 OK):** Barcha xizmatlar (faol va faol emas)

---

### 8.3. Xizmat ma'lumotlarini olish

**Endpoint:** `GET /api/v1/services/{service_id}`

**Authorization:** Yo'q (ochiq endpoint)

**Response (200 OK):** Bitta xizmat ma'lumotlari

---

## 🔌 9. WEBSOCKET

Real-time xabarlar uchun WebSocket ulanishlar

### 9.1. Haydovchi WebSocket

**URL:** `ws://localhost:8000/ws/drivers/{driver_id}`

**Yuboradigan ma'lumot:**
```json
{
  "lat": 41.311151,
  "lng": 69.279737,
  "timestamp": "2024-01-15T10:00:00"
}
```

**Qabul qiladigan ma'lumot:**
- Yangi buyurtmalar
- Dispetcher buyruqlari

---

### 9.2. Dispetcher WebSocket

**URL:** `ws://localhost:8000/ws/dispatchers/{dispatcher_id}`

**Qabul qiladigan ma'lumot:**
- Haydovchilar joylashuvi
- Safar yangilanishlari

---

### 9.3. Yo'lovchi WebSocket

**URL:** `ws://localhost:8000/ws/riders/{ride_id}`

**Qabul qiladigan ma'lumot:**
```json
{
  "type": "driver_location_update",
  "ride_id": 101,
  "driver_location": {
    "lat": 41.315000,
    "lng": 69.275000
  },
  "timestamp": "2024-01-15T10:15:00"
}
```

---

## 🔑 AUTHORIZATION

Barcha himoyalangan endpoint'lar uchun Authorization header kerak:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Swagger UI `/docs` da login qilganingizdan keyin avtomatik qo'shiladi.

---

## ⚠️ XATO KODLARI

- **400 Bad Request** - Noto'g'ri so'rov ma'lumotlari
- **401 Unauthorized** - Token yo'q yoki yaroqsiz
- **403 Forbidden** - Ruxsat yo'q
- **404 Not Found** - Topilmadi
- **500 Internal Server Error** - Server xatosi

---

## 📝 ESLATMALAR

1. Barcha telefon raqamlar `+998XXXXXXXXX` formatida bo'lishi kerak
2. Token 7 kun (604800 soniya) amal qiladi
3. Swagger UI: `http://localhost:8000/docs` - Bu yerda login qilganingizdan keyin avtomatik Authorization qo'shiladi
4. Redoc: `http://localhost:8000/redoc`
5. Swagger UI'da login/register qilganingizdan keyin token avtomatik saqlanadi va boshqa API'larga avtomatik qo'shiladi

---

## 🚀 TEZKOR MA'LUMOTNOMA

### Authentication Endpoints
- `POST /api/v1/auth/login` - Kirish
- `POST /api/v1/auth/logout` - Chiqish
- `POST /api/v1/auth/send-otp` - OTP yuborish
- `POST /api/v1/auth/verify-otp` - OTP tasdiqlash
- `POST /api/v1/auth/complete-profile` - Profilni to'ldirish

### Users Endpoints
- `GET /api/v1/users/profile` - Profilni ko'rish
- `PUT /api/v1/users/profile` - Profilni yangilash
- `POST /api/v1/users/profile-picture` - Rasm yuklash
- `GET /api/v1/users/balance` - Balans
- `GET /api/v1/users/rides` - Safar tarixi
- `GET /api/v1/users/transactions` - Tranzaksiyalar

### Admin Endpoints (19 ta)
- User boshqaruvi (approve, deactivate, activate, unapprove, set-dispatcher, set-admin, remove-roles)
- Statistika va tahlil (stats, daily, weekly, income/stats, income/monthly, income/yearly)
- Narx boshqaruvi (pricing, pricing/calculate)
- Komissiya (commission-rate)
- Xabarlar (notify/all, notify/{driver_id})

### Dispatcher Endpoints
- `POST /api/v1/dispatcher/order` - Buyurtma yaratish
- `POST /api/v1/dispatcher/order/{ride_id}/broadcast` - E'lon qilish
- `POST /api/v1/dispatcher/deposit` - Depozit qo'shish
- `POST /api/v1/dispatcher/block/{driver_id}` - Bloklash
- `POST /api/v1/dispatcher/unblock/{driver_id}` - Blokdan chiqarish
- `GET /api/v1/dispatcher/drivers/locations` - Joylashuvlar
- `POST /api/v1/dispatcher/cancel/{ride_id}` - Bekor qilish

### Driver Endpoints
- `POST /api/v1/driver/status` - Holat yangilash
- `POST /api/v1/driver/rides/{ride_id}/accept` - Qabul qilish
- `POST /api/v1/driver/rides/{ride_id}/start` - Boshlash
- `POST /api/v1/driver/rides/{ride_id}/complete` - Yakunlash
- `GET /api/v1/driver/stats` - Statistika
- `GET /api/v1/driver/pricing` - Tariflarni ko'rish
- `GET /api/v1/driver/rides/history` - Safar tarixi
- `GET /api/v1/driver/calculate-fare` - Taxometer (narx hisoblash)
- `GET /api/v1/driver/notifications` - Xabarlar tarixi
- `GET /api/v1/driver/stats/detailed` - Batafsil statistika (kunlik, haftalik, oylik)

### Rider Endpoints
- `GET /api/v1/rider/current-ride` - Hozirgi safar
- `GET /api/v1/rider/ride/{ride_id}` - Safar ma'lumotlari
- `GET /api/v1/rider/ride/{ride_id}/status` - Holat
- `GET /api/v1/rider/ride/{ride_id}/location` - Joylashuv
- `GET /api/v1/rider/rides/history` - Tarix
- `POST /api/v1/rider/ride/{ride_id}/cancel` - Bekor qilish

### Files Endpoints
- `POST /api/v1/files/profile-picture` - Profil rasmi
- `POST /api/v1/files/driver-documents` - Hujjatlar
- `POST /api/v1/files/upload/{folder}` - Umumiy yuklash
- `GET /api/v1/files/uploads/{folder}/{filename}` - Faylni ko'rish

### Services Endpoints
- `GET /api/v1/services/available` - Mavjud xizmatlar
- `GET /api/v1/services/all` - Barcha xizmatlar
- `GET /api/v1/services/{service_id}` - Xizmat ma'lumotlari

### Admin Services Endpoints
- `GET /api/v1/admin/services` - Barcha xizmatlarni ko'rish
- `POST /api/v1/admin/services` - Xizmat yaratish
- `PUT /api/v1/admin/services/{service_id}` - Xizmatni yangilash
- `DELETE /api/v1/admin/services/{service_id}` - Xizmatni o'chirish
- `PUT /api/v1/admin/services/{service_id}/toggle` - Faollashtirish/O'chirish

### WebSocket Endpoints
- `ws://localhost:8000/ws/drivers/{driver_id}` - Haydovchi
- `ws://localhost:8000/ws/dispatchers/{dispatcher_id}` - Dispetcher
- `ws://localhost:8000/ws/riders/{ride_id}` - Yo'lovchi

---

**Muallif:** Royal Taxi Development Team  
**Oxirgi yangilanish:** 2025-11-05  
**Versiya:** 2.0  
**Jami Endpoint'lar:** 62 ta
