# 🚕 Royal Taxi API - Swagger Auto-Authorization Guide

## ✅ Yangi funksiyalar

### 1. **Avtomatik Token Saqlash**
- Login yoki Register qilganingizda token **avtomatik** saqlanadi
- Token `localStorage` da saqlanadi va sahifani yangilash ham yo'qolmaydi
- Barcha API so'rovlariga token **avtomatik** qo'shiladi

### 2. **401 Error Oldini Olish**
- Login/Register qilgandan keyin **401 error qaytmaydi**
- Token saqlanib turadi va har bir requestga avtomatik qo'shiladi
- Logout qilguncha hech qanday avtorizatsiya muammosi bo'lmaydi

### 3. **Logout Funksiyasi**
- O'ng yuqori burchakda **Logout tugmasi** bor
- Logout qilsangiz token o'chadi va yana **401 error qaytadi**
- Login/Register qilmagan foydalanuvchilar uchun doimo 401 error

### 4. **Auth Status Ko'rsatgichi**
- Ekranning o'ng yuqori burchagida statusingiz ko'rsatiladi:
  - 🟢 **Yashil**: Tizimga kirilgan
  - 🔴 **Qizil**: Tizimga kirilmagan

---

## 📝 Qanday Ishlatiladi

### 1. Swagger UI ni Oching
```
http://localhost:8000/docs
```

### 2. Register yoki Login Qiling

**Register uchun:**
- `/api/v1/auth/register` endpointini oching
- "Try it out" tugmasini bosing
- Ma'lumotlaringizni kiriting:
```json
{
  "email": "test@example.com",
  "password": "YourPassword123!",
  "full_name": "Test User",
  "phone": "+998901234567",
  "is_driver": false,
  "language": "uz"
}
```
- "Execute" tugmasini bosing

**Login uchun:**
- `/api/v1/auth/login` endpointini oching
- "Try it out" tugmasini bosing
- Username (email yoki telefon) va parol kiriting:
```json
{
  "username": "test@example.com",
  "password": "YourPassword123!"
}
```
- "Execute" tugmasini bosing

### 3. Token Avtomatik Saqlanadi ✅

Login/Register muvaffaqiyatli bo'lgandan keyin:
- ✅ Yashil banner paydo bo'ladi: "Avtomatik avtorizatsiya!"
- ✅ Token `localStorage` ga saqlanadi
- ✅ O'ng yuqoridagi status **yashil** rangga o'zgaradi
- ✅ Endi barcha himoyalangan endpointlar **401 error bermasdan** ishlaydi

### 4. Endpointlarni Sinab Ko'ring

Endi istalgan himoyalangan endpointni ishlatishingiz mumkin:
- `/api/v1/users/me` - o'z profilingizni ko'rish
- `/api/v2/rides/` - yo'lovchilarni boshqarish
- `/api/v1/payments/` - to'lovlarni ko'rish

**401 error CHIQMAYDI!** ✅

### 5. Sahifani Yangilash

Sahifani yangilasangiz (`F5` yoki `Ctrl+R`):
- ✅ Token saqlanib qoladi
- ✅ Avtorizatsiya davom etadi
- ✅ 401 error hali ham chiqmaydi

### 6. Logout Qilish

Tizimdan chiqish uchun:
- O'ng yuqoridagi **"Logout"** tugmasini bosing
- Yoki browser console da `performLogout()` yozing

Logout qilgandan keyin:
- 🔴 Token o'chadi
- 🔴 Status qizil rangga o'zgaradi
- 🔴 Himoyalangan endpointlar yana **401 error beradi**

---

## 🔍 Texnik Tafsilotlar

### Token Saqlanishi
```javascript
// Token localStorage da saqlanadi
localStorage.setItem('swagger_auth_token', 'your_jwt_token');

// Token har bir requestga avtomatik qo'shiladi
headers['Authorization'] = `Bearer ${token}`;
```

### Logout Jarayoni
```javascript
// Token o'chiriladi
localStorage.removeItem('swagger_auth_token');

// Sahifa qayta yuklanadi
location.reload();
```

### 401 Error Xabarlari

Agar 401 error chiqsa, console da quyidagi xabarlar ko'rinadi:
- `Token yo'q. Iltimos login/register qiling.` - token mavjud emas
- `Token eskirgan bo'lishi mumkin. Qaytadan login qiling.` - token muddati tugagan

---

## 🧪 Test Qilish

Test scriptini ishlatish:
```bash
python test_swagger_auth.py
```

Bu test quyidagilarni tekshiradi:
- ✅ Swagger UI yuklangan
- ✅ Register endpoint token qaytaradi
- ✅ Login endpoint token qaytaradi
- ✅ Token format to'g'ri (bearer)

---

## ❓ Ko'p So'raladigan Savollar

**Q: Token qachon o'chadi?**
A: Faqat Logout tugmasini bosganingizda yoki `performLogout()` chaqirganingizda.

**Q: Sahifani yangilasam token yo'qoladimi?**
A: Yo'q! Token `localStorage` da saqlanadi va saqlanib qoladi.

**Q: Bir necha tab ochsam nima bo'ladi?**
A: Barcha tablarda bir xil token ishlatiladi (localStorage global).

**Q: Login qilmagan foydalanuvchilar nima oladi?**
A: 401 Unauthorized error - bu to'g'ri xatti-harakat.

**Q: Token muddati tugasa nima bo'ladi?**
A: 401 error chiqadi va qaytadan login qilish kerak.

---

## 🎯 Xulosa

Bu yangi Swagger UI quyidagilarni ta'minlaydi:

1. ✅ **Avtomatik token saqlash** - login/register qilgandan keyin
2. ✅ **401 errorlarni oldini olish** - logout qilguncha
3. ✅ **Oson logout** - bir tugma bosish
4. ✅ **Token persistence** - sahifa yangilanishda ham
5. ✅ **Visual status** - har doim statusingizni ko'rishingiz mumkin
6. ✅ **Uzbekcha interface** - tushunish oson

**Endi Swagger UI bilan ishlash juda oson va qulay!** 🎉
