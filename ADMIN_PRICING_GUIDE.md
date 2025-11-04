# Admin Narxlarni Boshqarish - Royal Taxi API

## 📊 Umumiy Ma'lumot

Admin panel orqali taksi narxlarini to'liq boshqarish imkoniyati:
- **3 xil mashina turi** narxlarini sozlash
- **Narxlarni ko'rish** va tahrirlash
- **Narxni hisoblash** (preview)
- **Komissiya stavkasini** o'zgartirish

---

## 🚗 Mashina Turlari va Narxlar

### Hozirgi Narxlar (Default)

| Mashina Turi | Boshlang'ich | Har km | Har daqiqa | Sig'im |
|--------------|--------------|--------|------------|--------|
| **Economy** (Oddiy) | 10,000 so'm | 2,000 so'm | 500 so'm | 4 kishi |
| **Comfort** (Qulay) | 15,000 so'm | 3,000 so'm | 750 so'm | 4 kishi |
| **Business** (Biznes) | 25,000 so'm | 5,000 so'm | 1,000 so'm | 4 kishi |

### Narx Hisoblash Formulasi

```
Umumiy narx = Boshlang'ich narx + (Masofa × Km narxi) + (Vaqt × Daqiqa narxi)
```

**Misol (Economy):**
- Masofa: 10 km
- Vaqt: 20 daqiqa
- Narx = 10,000 + (10 × 2,000) + (20 × 500)
- Narx = 10,000 + 20,000 + 10,000 = **40,000 so'm**

**Komissiya (10%):**
- Umumiy narx: 40,000 so'm
- Komissiya: 4,000 so'm (10%)
- Haydovchi daromadi: 36,000 so'm

---

## 🔧 Admin API Endpoints

### 1. Narxlarni Ko'rish

**GET** `/api/v1/admin/pricing`

Barcha mashina turlari uchun hozirgi narxlarni ko'rish.

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "economy": {
    "display_name": "Economy",
    "base_fare": 10000,
    "per_km_rate": 2000,
    "per_minute_rate": 500,
    "capacity": 4
  },
  "comfort": {
    "display_name": "Comfort",
    "base_fare": 15000,
    "per_km_rate": 3000,
    "per_minute_rate": 750,
    "capacity": 4
  },
  "business": {
    "display_name": "Business",
    "base_fare": 25000,
    "per_km_rate": 5000,
    "per_minute_rate": 1000,
    "capacity": 4
  },
  "commission_rate": 0.1
}
```

---

### 2. Narxlarni Yangilash

**PUT** `/api/v1/admin/pricing/{vehicle_type}`

Mashina turi narxlarini yangilash.

**Path Parameters:**
- `vehicle_type`: `economy`, `comfort`, yoki `business`

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "vehicle_type": "economy",
  "base_fare": 12000,
  "per_km_rate": 2500,
  "per_minute_rate": 600
}
```

**Response:**
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

**cURL Misoli:**
```bash
curl -X PUT http://localhost:8080/api/v1/admin/pricing/economy \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_type": "economy",
    "base_fare": 12000,
    "per_km_rate": 2500,
    "per_minute_rate": 600
  }'
```

---

### 3. Narxni Hisoblash (Preview)

**GET** `/api/v1/admin/pricing/calculate`

Berilgan masofa va vaqt uchun narxni hisoblash.

**Query Parameters:**
- `distance`: Masofa (km) - majburiy
- `duration`: Vaqt (daqiqa) - majburiy
- `vehicle_type`: Mashina turi (default: economy)

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Request:**
```
GET /api/v1/admin/pricing/calculate?distance=10&duration=20&vehicle_type=economy
```

**Response:**
```json
{
  "vehicle_type": "economy",
  "distance_km": 10,
  "duration_minutes": 20,
  "breakdown": {
    "base_fare": 10000,
    "distance_cost": 20000,
    "time_cost": 10000
  },
  "total_fare": 40000,
  "commission_rate": 0.1,
  "commission_amount": 4000,
  "driver_earnings": 36000,
  "formula": "10000 + (10 × 2000) + (20 × 500) = 40000 so'm"
}
```

**cURL Misoli:**
```bash
curl -X GET "http://localhost:8080/api/v1/admin/pricing/calculate?distance=10&duration=20&vehicle_type=economy" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

### 4. Komissiya Stavkasini O'zgartirish

**PUT** `/api/v1/admin/config/commission-rate`

Komissiya stavkasini yangilash.

**Query Parameters:**
- `rate`: Komissiya stavkasi (0-1 oralig'ida, masalan 0.10 = 10%)

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Request:**
```
PUT /api/v1/admin/config/commission-rate?rate=0.15
```

**Response:**
```json
{
  "message": "Commission rate updated",
  "commission_rate": 0.15
}
```

**cURL Misoli:**
```bash
curl -X PUT "http://localhost:8080/api/v1/admin/config/commission-rate?rate=0.15" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 📱 Swagger UI'da Test Qilish

### 1. Admin Sifatida Login

```bash
POST /api/v1/auth/login
{
  "phone": "+998901234567",
  "password": "admin_password"
}
```

Token avtomatik saqlanadi (Swagger UI'da).

### 2. Narxlarni Ko'rish

```
GET /api/v1/admin/pricing
```

### 3. Narxlarni Yangilash

```
PUT /api/v1/admin/pricing/economy
{
  "vehicle_type": "economy",
  "base_fare": 12000,
  "per_km_rate": 2500,
  "per_minute_rate": 600
}
```

### 4. Narxni Hisoblash

```
GET /api/v1/admin/pricing/calculate?distance=10&duration=20&vehicle_type=economy
```

---

## 💡 Narxlarni O'zgartirish Misollari

### Misol 1: Economy Narxlarini Oshirish

**Hozirgi:**
- Boshlang'ich: 10,000 so'm
- Har km: 2,000 so'm
- Har daqiqa: 500 so'm

**Yangi (20% oshirish):**
- Boshlang'ich: 12,000 so'm
- Har km: 2,400 so'm
- Har daqiqa: 600 so'm

**Request:**
```json
{
  "vehicle_type": "economy",
  "base_fare": 12000,
  "per_km_rate": 2400,
  "per_minute_rate": 600
}
```

### Misol 2: Comfort Narxlarini Kamaytirish

**Hozirgi:**
- Boshlang'ich: 15,000 so'm
- Har km: 3,000 so'm
- Har daqiqa: 750 so'm

**Yangi (10% kamaytirish):**
- Boshlang'ich: 13,500 so'm
- Har km: 2,700 so'm
- Har daqiqa: 675 so'm

**Request:**
```json
{
  "vehicle_type": "comfort",
  "base_fare": 13500,
  "per_km_rate": 2700,
  "per_minute_rate": 675
}
```

### Misol 3: Business Narxlarini Maxsus Sozlash

**Yangi:**
- Boshlang'ich: 30,000 so'm
- Har km: 6,000 so'm
- Har daqiqa: 1,200 so'm

**Request:**
```json
{
  "vehicle_type": "business",
  "base_fare": 30000,
  "per_km_rate": 6000,
  "per_minute_rate": 1200
}
```

---

## 📊 Narx Tahlili

### Qisqa Masofa (1-5 km)

| Masofa | Vaqt | Economy | Comfort | Business |
|--------|------|---------|---------|----------|
| 1 km | 5 min | 14,500 | 21,750 | 36,000 |
| 3 km | 10 min | 21,000 | 30,500 | 50,000 |
| 5 km | 15 min | 27,500 | 39,250 | 64,000 |

### O'rta Masofa (5-15 km)

| Masofa | Vaqt | Economy | Comfort | Business |
|--------|------|---------|---------|----------|
| 5 km | 15 min | 27,500 | 39,250 | 64,000 |
| 10 km | 25 min | 42,500 | 60,750 | 98,000 |
| 15 km | 35 min | 57,500 | 82,250 | 132,000 |

### Uzoq Masofa (15+ km)

| Masofa | Vaqt | Economy | Comfort | Business |
|--------|------|---------|---------|----------|
| 20 km | 45 min | 72,500 | 103,750 | 166,000 |
| 30 km | 60 min | 100,000 | 145,000 | 230,000 |
| 50 km | 90 min | 155,000 | 227,500 | 358,000 |

---

## 🔐 Xavfsizlik

### Admin Huquqlari

Faqat `is_admin=true` bo'lgan foydalanuvchilar:
- Narxlarni ko'rishi mumkin
- Narxlarni o'zgartirishi mumkin
- Narxni hisoblashi mumkin
- Komissiya stavkasini o'zgartirishi mumkin

### Validatsiya

- **Boshlang'ich narx:** > 0
- **Km narxi:** > 0
- **Daqiqa narxi:** > 0
- **Mashina turi:** faqat economy, comfort, business
- **Komissiya stavkasi:** 0-1 oralig'ida (0% - 100%)

---

## 💾 Ma'lumotlar Saqlash

Narxlar **system_config** jadvalida saqlanadi:

```sql
INSERT INTO system_config (key, value) VALUES
('pricing_economy', '{"base_fare": 10000, "per_km_rate": 2000, "per_minute_rate": 500}'),
('pricing_comfort', '{"base_fare": 15000, "per_km_rate": 3000, "per_minute_rate": 750}'),
('pricing_business', '{"base_fare": 25000, "per_km_rate": 5000, "per_minute_rate": 1000}'),
('commission_rate', '0.1');
```

---

## 🚀 Qo'shimcha Imkoniyatlar

### 1. Vaqtga Bog'liq Narxlar (Kelajakda)

- **Tong** (06:00-10:00): +20%
- **Kunduzi** (10:00-18:00): Normal
- **Kechqurun** (18:00-22:00): +30%
- **Tunda** (22:00-06:00): +50%

### 2. Shahar Bo'yicha Narxlar

- **Toshkent:** Hozirgi narxlar
- **Samarqand:** -10%
- **Buxoro:** -15%
- **Andijon:** -20%

### 3. Maxsus Kunlar

- **Dam olish kunlari:** +15%
- **Bayramlar:** +25%
- **Yomg'ir/Qor:** +20%

---

## 📞 Qo'llab-quvvatlash

Savol yoki muammo bo'lsa:
- **Swagger UI:** http://localhost:8080/docs
- **Admin Panel:** Narxlarni boshqarish bo'limi
- **Dokumentatsiya:** Bu fayl

---

## ✅ Xulosa

Admin panel orqali narxlarni to'liq boshqarish:

✅ 3 xil mashina turi narxlari
✅ Narxlarni ko'rish va tahrirlash
✅ Narxni hisoblash (preview)
✅ Komissiya stavkasini o'zgartirish
✅ Real vaqtda yangilanadi
✅ Xavfsiz va oson

**Hozir ishlatishingiz mumkin!** 🎉
