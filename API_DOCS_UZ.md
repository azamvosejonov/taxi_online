# ROYAL TAXI API Loyiha

Quyida loyihaning barcha API endpointlari haqida ma'lumotlar keltirilgan. Har bir endpoint uchun uning maqsadi, HTTP metodi va URL manzili ko'rsatilgan.

---

## Auth (Avtorizatsiya)

- **POST /api/v1/auth/register**
  - Foydalanuvchini ro'yxatdan o'tkazish

- **POST /api/v1/auth/login**
  - Foydalanuvchini tizimga kirish

- **POST /api/v1/auth/logout**
  - Tizimdan chiqish

---

## Users (Foydalanuvchilar)

- **GET /api/v1/users/profile**
  - Foydalanuvchi profilini olish

- **PUT /api/v1/users/profile**
  - Foydalanuvchi profilini yangilash

- **POST /api/v1/users/profile-picture**
  - Profil rasmini yuklash

- **GET /api/v1/users/balance**
  - Hisob balansini olish

- **GET /api/v1/users/rides**
  - Foydalanuvchining safarlarini olish

- **GET /api/v1/users/transactions**
  - Foydalanuvchi tranzaksiyalarini ko'rish

---

## Admin (Administrator)

- **GET /api/v1/admin/users**
  - Barcha foydalanuvchilar ro'yxatini olish

- **GET /api/v1/admin/stats**
  - Tizim statistikalarini olish

- **GET /api/v1/admin/analytics/daily**
  - Kundalik tahlillarni olish

- **GET /api/v1/admin/analytics/weekly**
  - Haftalik tahlillarni olish

- **PUT /api/v1/admin/users/{user_id}/deactivate**
  - Foydalanuvchini deaktivlashtirish

- **PUT /api/v1/admin/users/{user_id}/approve**
  - Foydalanuvchini tasdiqlash

- **PUT /api/v1/admin/users/{user_id}/unapprove**
  - Foydalanuvchini tasdiqlashni bekor qilish

- **PUT /api/v1/admin/users/{user_id}/activate**
  - Foydalanuvchini faollashtirish

- **GET /api/v1/admin/income/stats**
  - Daromad statistikalarini olish

- **GET /api/v1/admin/income/monthly/{year}/{month}**
  - Oyma-oy daromadni olish

- **GET /api/v1/admin/income/yearly/{year}**
  - Yil bo'yicha daromadni olish

- **GET /api/v1/admin/config/commission-rate**
  - Komissiya foizini olish

- **PUT /api/v1/admin/config/commission-rate**
  - Komissiya foizini o'rnatish

- **POST /api/v1/admin/notify/all**
  - Barcha haydovchilarga xabar yuborish

- **POST /api/v1/admin/notify/{driver_id}**
  - Muayyan haydovchiga xabar yuborish

---

## Dispatcher (Buyurtma boshqaruvchisi)

- **POST /api/v1/dispatcher/order**
  - Yangi buyurtma yaratish

- **POST /api/v1/dispatcher/order/{ride_id}/broadcast**
  - Buyurtmani barcha haydovchilarga e'lon qilish

- **POST /api/v1/dispatcher/deposit**
  - Hisobga depozit qo'shish

- **POST /api/v1/dispatcher/block/{driver_id}**
  - Haydovchini bloklash

- **POST /api/v1/dispatcher/unblock/{driver_id}**
  - Haydovchini blokdan chiqarish

- **GET /api/v1/dispatcher/drivers/locations**
  - Haydovchilarning joylashuvlarini ko'rsatish

- **POST /api/v1/dispatcher/cancel/{ride_id}**
  - Buyurtmani bekor qilish

---

## Driver (Haydovchi)

- **POST /api/v1/driver/status**
  - Haydovchi holatini yangilash

- **POST /api/v1/driver/rides/{ride_id}/accept**
  - Buyurtmani qabul qilish

- **POST /api/v1/driver/rides/{ride_id}/start**
  - Safarni boshlash

- **POST /api/v1/driver/rides/{ride_id}/complete**
  - Safarni yakunlash

- **GET /api/v1/driver/stats**
  - Haydovchi statistikalarini olish

---

# Izoh

Ushbu hujjat loyihaning barcha API endpointlarini o'zbek tilida qisqacha tushuntiradi. Agar qo'shimcha ma'lumot yoki namunaviy so'rovlar kerak bo'lsa, iltimos so'rang.
