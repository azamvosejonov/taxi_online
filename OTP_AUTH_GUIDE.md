# OTP Authentication Flow - Royal Taxi API

## Umumiy ma'lumot

Royal Taxi API uchun telefon raqam orqali OTP (One-Time Password) autentifikatsiya tizimi joriy etildi. Bu tizim 3 bosqichdan ibarат:

1. **Telefon raqamga OTP yuborish** - `/api/v1/auth/send-otp`
2. **OTP kodni tasdiqlash** - `/api/v1/auth/verify-otp`
3. **Foydalanuvchi ma'lumotlarini to'ldirish** - `/api/v1/auth/complete-profile`

---

## API Endpoints

### 1. OTP Yuborish

**Endpoint:** `POST /api/v1/auth/send-otp`

**Tavsif:** Telefon raqamga 6 raqamli tasdiqlash kodini yuboradi. Kod 5 daqiqa davomida amal qiladi.

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
  "otp_code": "123456"  // Faqat development muhitida
}
```

**Muhim eslatmalar:**
- `otp_code` maydoni faqat development muhitida qaytariladi
- Production muhitida kod SMS orqali yuboriladi (Eskiz.uz, Playmobile)
- Eski tasdiqlanmagan kodlar avtomatik o'chiriladi

---

### 2. OTP Tasdiqlash

**Endpoint:** `POST /api/v1/auth/verify-otp`

**Tavsif:** Telefon raqamga yuborilgan 6 raqamli kodni tekshiradi.

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

**Xatoliklar:**
- `404` - Tasdiqlash kodi topilmadi
- `400` - Kod muddati tugagan yoki noto'g'ri

**Muhim eslatmalar:**
- `needs_profile_completion: true` - yangi foydalanuvchi, profil to'ldirish kerak
- `needs_profile_completion: false` - mavjud foydalanuvchi
- Tasdiqlash 30 daqiqa davomida amal qiladi

---

### 3. Profil To'ldirish

**Endpoint:** `POST /api/v1/auth/complete-profile`

**Tavsif:** Telefon raqam tasdiqlanganidan keyin foydalanuvchi ma'lumotlarini to'ldiradi va JWT token qaytaradi.

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

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": 1,
    "phone": "+998901234567",
    "first_name": "Falonchi",
    "last_name": "Falonchiyev",
    "full_name": "Falonchi Falonchiyev",
    "gender": "Erkak",
    "date_of_birth": "1990-01-01T00:00:00",
    "vehicle_make": "Chevrolet",
    "vehicle_color": "Qora",
    "position": "Haydovchi",
    "license_plate": "01A123AA",
    "tech_passport": "AA1234567",
    "is_driver": true,
    "is_dispatcher": false,
    "is_admin": false,
    "is_approved": false,
    "current_balance": 0.0,
    "rating": 5.0,
    "total_rides": 0
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "security": {
    "Bearer": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "type": "bearer"
    }
  }
}
```

**Xatoliklar:**
- `400` - Telefon raqam tasdiqlanmagan
- `400` - Telefon raqam allaqachon ro'yxatdan o'tgan
- `400` - Davlat raqami yoki texpassport allaqachon mavjud
- `400` - Tasdiqlash muddati tugagan (30 daqiqadan ko'p vaqt o'tgan)

---

## To'liq Oqim (Flow)

```
1. Foydalanuvchi telefon raqamni kiritadi
   ↓
2. POST /api/v1/auth/send-otp
   → OTP kod yuboriladi (SMS orqali)
   ↓
3. Foydalanuvchi OTP kodni kiritadi
   ↓
4. POST /api/v1/auth/verify-otp
   → Kod tekshiriladi
   ↓
5. Agar needs_profile_completion: true
   ↓
6. Foydalanuvchi ma'lumotlarini to'ldiradi
   ↓
7. POST /api/v1/auth/complete-profile
   → JWT token qaytariladi
   ↓
8. Token bilan API'dan foydalanish
```

---

## Swagger UI Integration

Swagger UI avtomatik ravishda tokenni saqlaydi va barcha so'rovlarga qo'shadi:

1. `/api/v1/auth/send-otp` ni chaqiring
2. `/api/v1/auth/verify-otp` ni chaqiring
3. `/api/v1/auth/complete-profile` ni chaqiring
4. Token avtomatik saqlanadi va barcha keyingi so'rovlarga qo'shiladi

**Qo'lda Authorize tugmasini bosish shart emas!**

---

## Database Schema

### otp_verifications jadvali

```sql
CREATE TABLE otp_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone VARCHAR NOT NULL,
    otp_code VARCHAR NOT NULL,
    is_verified BOOLEAN DEFAULT 0,
    expires_at DATETIME NOT NULL,
    created_at DATETIME,
    verified_at DATETIME
);

CREATE INDEX ix_otp_verifications_phone ON otp_verifications(phone);
```

---

## Xavfsizlik

1. **OTP kod xavfsizligi:**
   - 6 raqamli tasodifiy kod
   - 5 daqiqa davomida amal qiladi
   - Bir marta ishlatiladi

2. **Tasdiqlash xavfsizligi:**
   - Tasdiqlash 30 daqiqa davomida amal qiladi
   - Eski tasdiqlanmagan kodlar avtomatik o'chiriladi

3. **JWT Token:**
   - 7 kun davomida amal qiladi
   - HS256 algoritmi bilan shifrlangan

---

## Production uchun Tavsiyalar

1. **SMS Gateway integratsiyasi:**
   
   **Twilio (Joriy):**
   - ✅ Integratsiya qilingan
   - `.env` faylida `TWILIO_ENABLED=true` qiling
   - Twilio credentials'ni kiriting
   - Batafsil: `TWILIO_SETUP_GUIDE.md`
   
   **Alternativalar:**
   - Eskiz.uz API (O'zbekiston uchun arzon)
   - Playmobile API
   - SMS.uz API

2. **OTP kod response'dan avtomatik olib tashlanadi:**
   - Agar `TWILIO_ENABLED=true` bo'lsa, `otp_code` response'da bo'lmaydi
   - Agar `TWILIO_ENABLED=false` bo'lsa, development uchun `otp_code` qaytariladi

3. **Rate Limiting:**
   - Bir telefon raqamga 1 daqiqada 1 ta OTP
   - Bir IP'dan 1 daqiqada 5 ta OTP

4. **Monitoring:**
   - OTP yuborish muvaffaqiyati
   - Tasdiqlash muvaffaqiyati
   - Noto'g'ri kodlar soni

---

## Test Qilish

Test skriptni ishga tushiring:

```bash
source .venv/bin/activate
python test_otp_flow.py
```

Yoki qo'lda test qiling:

```bash
# 1. OTP yuborish
curl -X POST http://localhost:8080/api/v1/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567"}'

# 2. OTP tasdiqlash
curl -X POST http://localhost:8080/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567", "otp_code": "123456"}'

# 3. Profil to'ldirish
curl -X POST http://localhost:8080/api/v1/auth/complete-profile \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+998901234567",
    "first_name": "Test",
    "last_name": "User",
    "gender": "Erkak",
    "date_of_birth": "1990-01-01",
    "vehicle_make": "Chevrolet",
    "vehicle_color": "Qora",
    "position": "Haydovchi",
    "license_plate": "01T999ST",
    "tech_passport": "TEST123456"
  }'
```

---

## Muammolarni Hal Qilish

### OTP kod kelmayapti
- SMS gateway sozlamalarini tekshiring
- Telefon raqam formatini tekshiring (+998XXXXXXXXX)
- Server loglarini tekshiring

### "Tasdiqlash kodi topilmadi" xatosi
- OTP yuborish so'rovini qayta yuboring
- 5 daqiqa ichida tasdiqlang

### "Telefon raqam allaqachon ro'yxatdan o'tgan" xatosi
- Bu foydalanuvchi mavjud
- Login endpoint'dan foydalaning (agar parol bor bo'lsa)
- Yoki yangi telefon raqam kiriting

---

## Qo'shimcha Ma'lumot

- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc
- **API versiyasi:** v1
- **Base URL:** http://localhost:8080/api/v1
