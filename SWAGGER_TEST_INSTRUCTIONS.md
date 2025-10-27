# 🧪 Swagger UI - 401 Error Test Yo'riqnomasi

## ✅ Yangilanganlar

Token endi **to'g'ri formatda** yuboriladi va 401 error chiqmasligi kerak!

---

## 📋 Test Qilish Yo'riqnomasi

### 1. Swagger UI ni Oching

Browseringizda:
```
http://localhost:8000/docs
```

### 2. Browser Console ni Oching

- **Chrome/Edge**: `F12` yoki `Ctrl+Shift+I`
- **Firefox**: `F12`
- **Console** tab ni tanlang

### 3. Register yoki Login Qiling

**Register qilish:**
1. `/api/v1/auth/register` endpointini toping
2. "Try it out" ni bosing
3. Quyidagi ma'lumotlarni kiriting:

```json
{
  "email": "mytest@example.com",
  "password": "MyPassword123!",
  "full_name": "My Test User",
  "phone": "+998901234567",
  "is_driver": false,
  "language": "uz"
}
```

4. **Execute** tugmasini bosing
5. Console da quyidagi xabarlarni ko'rishingiz kerak:

```
✅ Token avtomatik saqlandi va avtorizatsiya qilindi!
💡 Token logout qilguncha saqlanadi va 401 error bermaydi
🔑 Token: eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...
```

6. Ekranning o'ng yuqorisida **yashil indikator** va "Tizimga kirilgan" yozuvi paydo bo'lishi kerak

### 4. Himoyalangan Endpointni Test Qiling

Endi istalgan himoyalangan endpointni sinab ko'ring, masalan:

**`/api/v2/customers/` (GET)**
1. Endpointni toping
2. "Try it out" ni bosing
3. **Execute** ni bosing

**Natija:**
- ✅ **200 OK** - Token ishlayapti!
- ❌ **401 Unauthorized** - Muammo bor (quyidagi debugging ga o'ting)

### 5. Console da Tekshirish

Har bir request uchun console da quyidagilarni ko'rishingiz kerak:

```javascript
📤 Request with token: http://localhost:8000/api/v2/customers/
```

Agar bu xabar chiqmasa, token yuborilmayapti demakdir.

---

## 🔍 Debugging - Agar 401 Hali Ham Chiqsa

### A. Token Saqlanganligini Tekshiring

Console da yozing:
```javascript
localStorage.getItem('swagger_auth_token')
```

**Natija:**
- Agar token ko'rsatsa: ✅ Token saqlangan
- Agar `null` bo'lsa: ❌ Token saqlanmagan - qaytadan login qiling

### B. Request Header ni Tekshiring

1. Browser DevTools da **Network** tabini oching
2. Biron endpoint ga request yuboring
3. Request ni tanlang
4. **Headers** bo'limida `Authorization` headerini qidiring

**Bo'lishi kerak:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Agar bu header YO'Q bo'lsa, requestInterceptor ishlamayapti demakdir.

### C. Manual Authorization

Agar avtomatik ishlamasa, qo'lda authorization qiling:

1. Swagger UI yuqori qismida **"Authorize"** yoki qulf belgisini bosing
2. `Bearer` oynasiga tokenni kiriting (faqat token, "Bearer" so'zisiz!)
3. **Authorize** ni bosing
4. **Close** ni bosing

Endi barcha requestlarda token qo'shilishi kerak.

---

## 🐛 Keng Tarqalgan Muammolar va Yechimlar

### Muammo 1: "Not authenticated" deb 401 chiqadi

**Sabab:** Token yuborilmayapti yoki noto'g'ri formatda

**Yechim:**
```javascript
// Console da tekshiring:
localStorage.getItem('swagger_auth_token')

// Agar token bor bo'lsa, manual qo'shing:
performLogout()  // Tozalash
// Keyin qaytadan login qiling
```

### Muammo 2: Token bor lekin 401 chiqaveradi

**Sabab:** Token muddati tugagan bo'lishi mumkin (7 kundan keyin)

**Yechim:**
```javascript
// Logout qiling va qaytadan login qiling
performLogout()
```

### Muammo 3: Ba'zi endpointlar ishlaydi, ba'zilari 401 beradi

**Sabab:** Ba'zi endpointlar mavjud emas (404) yoki to'g'ri configuratsiya qilinmagan

**Yechim:**
- 404 - Endpoint mavjud emas
- 401 - Token muammosi
- 403 - Ruxsat yo'q (admin kerak masalan)

### Muammo 4: Sahifani yangilasam token yo'qoladi

**Sabab:** localStorage ishlamayapti yoki browser private mode da

**Yechim:**
- Private/Incognito mode dan chiqing
- Cookie va localStorage ruxsat ekanligini tekshiring
- Browser console da xatolik borligini tekshiring

---

## ✅ Test Checklist

Quyidagilarni tekshiring:

- [ ] Swagger UI `/docs` ochiladi
- [ ] Register/Login endpoint ishlaydi va token qaytaradi
- [ ] Console da "Token avtomatik saqlandi" xabari chiqadi
- [ ] O'ng yuqorida yashil status ko'rsatiladi
- [ ] `localStorage.getItem('swagger_auth_token')` token qaytaradi
- [ ] Himoyalangan endpoint 200/404 beradi (401 EMAS!)
- [ ] Network tabda `Authorization: Bearer ...` headeri ko'rinadi
- [ ] Sahifani yangilasam ham token saqlanadi
- [ ] Logout tugmasi tokenni o'chiradi

---

## 🎯 Kutilgan Natija

**OLDIN (Muammo):**
```
POST /api/v1/auth/login → 200 OK (token olindi)
GET /api/v2/customers/ → 401 Unauthorized ❌
```

**HOZIR (To'g'rilandi):**
```
POST /api/v1/auth/login → 200 OK (token olindi)
✅ Token avtomatik saqlandi va avtorizatsiya qilindi!
GET /api/v2/customers/ → 200 OK ✅
GET /api/v2/customers/ → 200 OK (sahifa yangilandi ham) ✅
```

---

## 📞 Qo'shimcha Yordam

Agar hali ham muammo bo'lsa:

1. Backend loglarini tekshiring (terminal)
2. Browser console da xatolarni tekshiring
3. `test_401_fix.py` scriptini ishlatib API testini bajaring:
```bash
python test_401_fix.py
```

Bu script token to'g'ri ishlashini tekshiradi.

---

**Muvaffaqiyatli test qilishingizni tilaymiz!** 🎉
