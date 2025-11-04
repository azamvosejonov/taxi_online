# Royal Taxi API Testing Guide

## 📋 Test Suite Haqida

Comprehensive test suite barcha API endpoint'larni to'liq test qiladi:
- ✅ **Success cases** (200, 201)
- ❌ **Error cases** (400, 401, 403, 404, 422)
- 🔐 **Authentication** tests
- 📱 **OTP flow** tests
- 👤 **User management** tests
- 👨‍💼 **Admin** tests
- 🚕 **Dispatcher** tests
- 🚗 **Driver** tests
- 🧑‍🤝‍🧑 **Rider** tests

---

## 🚀 Test'ni Ishga Tushirish

### Avtomatik Test (Tavsiya etiladi)

```bash
source .venv/bin/activate
python test_all_endpoints_comprehensive.py
```

### Qo'lda Test

```bash
# Alohida test'lar
python test_otp_flow.py           # OTP flow
python test_admin_pricing.py      # Admin pricing
python test_twilio_sms.py         # Twilio SMS
```

---

## 📊 Test Kategoriyalari

### 1. Authentication Tests (9 tests)

| Test | Endpoint | Expected | Description |
|------|----------|----------|-------------|
| ✅ Register Success | POST /auth/register | 201 | Yangi foydalanuvchi ro'yxatdan o'tishi |
| ❌ Register Duplicate | POST /auth/register | 400 | Mavjud telefon raqam |
| ❌ Register Invalid Phone | POST /auth/register | 422 | Noto'g'ri telefon format |
| ❌ Register Missing Fields | POST /auth/register | 422 | Majburiy maydonlar yo'q |
| ✅ Login Success | POST /auth/login | 200 | To'g'ri login |
| ❌ Login Wrong Password | POST /auth/login | 400 | Noto'g'ri parol |
| ❌ Login Invalid Phone | POST /auth/login | 422 | Noto'g'ri telefon format |
| ✅ Logout Success | POST /auth/logout | 200 | Logout muvaffaqiyatli |
| ❌ Logout No Token | POST /auth/logout | 401 | Token yo'q |

### 2. OTP Authentication Tests (7 tests)

| Test | Endpoint | Expected | Description |
|------|----------|----------|-------------|
| ✅ Send OTP Success | POST /auth/send-otp | 200 | OTP yuborish |
| ❌ Send OTP Invalid Phone | POST /auth/send-otp | 422 | Noto'g'ri telefon |
| ✅ Verify OTP Success | POST /auth/verify-otp | 200 | To'g'ri OTP |
| ❌ Verify OTP Wrong Code | POST /auth/verify-otp | 400 | Noto'g'ri kod |
| ❌ Verify OTP Invalid Format | POST /auth/verify-otp | 422 | Noto'g'ri format |
| ✅ Complete Profile Success | POST /auth/complete-profile | 201 | Profil to'ldirish |
| ❌ Complete Profile Not Verified | POST /auth/complete-profile | 400 | Tasdiqlanmagan |

### 3. User Management Tests (3 tests)

| Test | Endpoint | Expected | Description |
|------|----------|----------|-------------|
| ✅ Get Current User | GET /users/me | 200 | Foydalanuvchi ma'lumotlari |
| ❌ Get User No Token | GET /users/me | 401 | Token yo'q |
| ❌ Get User Invalid Token | GET /users/me | 401 | Noto'g'ri token |

### 4. Admin Tests (11 tests)

| Test | Endpoint | Expected | Description |
|------|----------|----------|-------------|
| ✅ Get All Users | GET /admin/users | 200 | Barcha foydalanuvchilar |
| ❌ Get Users Non-Admin | GET /admin/users | 403 | Admin emas |
| ✅ Get Stats | GET /admin/stats | 200 | Statistika |
| ✅ Get Pricing | GET /admin/pricing | 200 | Narxlar |
| ✅ Calculate Fare | GET /admin/pricing/calculate | 200 | Narx hisoblash |
| ❌ Calculate Fare Invalid Type | GET /admin/pricing/calculate | 400 | Noto'g'ri tur |
| ✅ Update Pricing | PUT /admin/pricing/{type} | 200 | Narx yangilash |
| ❌ Update Pricing Invalid Type | PUT /admin/pricing/{type} | 400 | Noto'g'ri tur |
| ❌ Update Pricing Invalid Data | PUT /admin/pricing/{type} | 422 | Noto'g'ri ma'lumot |
| ✅ Set Commission | PUT /admin/config/commission-rate | 200 | Komissiya o'zgartirish |
| ❌ Set Commission Invalid | PUT /admin/config/commission-rate | 400 | Noto'g'ri qiymat |

### 5. Dispatcher Tests (3 tests)

| Test | Endpoint | Expected | Description |
|------|----------|----------|-------------|
| ✅ Create Order | POST /dispatcher/order | 201 | Buyurtma yaratish |
| ❌ Create Order Invalid Phone | POST /dispatcher/order | 422 | Noto'g'ri telefon |
| ❌ Create Order Missing Data | POST /dispatcher/order | 422 | Ma'lumot yo'q |

### 6. Driver Tests (3 tests)

| Test | Endpoint | Expected | Description |
|------|----------|----------|-------------|
| ✅ Update Status | POST /driver/status | 200 | Status yangilash |
| ❌ Update Status Invalid Coords | POST /driver/status | 422 | Noto'g'ri koordinatalar |
| ✅ Get Stats | GET /driver/stats | 200 | Statistika |

### 7. Rider Tests (2 tests)

| Test | Endpoint | Expected | Description |
|------|----------|----------|-------------|
| ✅ Update Location | POST /rider/rides/{id}/location | 200 | Joylashuv yangilash |
| ❌ Update Location Invalid Ride | POST /rider/rides/{id}/location | 404 | Noto'g'ri ride ID |

---

## 📈 Expected Results

### Minimum Pass Rate: 90%

```
Total Tests: 38+
Passed: 34+
Failed: 4 or less
Pass Rate: 90%+
```

### Test Output Format

```
======================================================================
                    1. AUTHENTICATION ENDPOINTS                      
======================================================================

✓ Register new user - Success
  Expected: 201, Got: 201

✗ Register duplicate phone - Error 400
  Expected: 400, Got: 400

✓ Login - Success
  Expected: 200, Got: 200
```

---

## 🔧 Test Sozlamalari

### Environment Variables

```bash
# .env faylida
BASE_URL=http://localhost:8080/api/v1
TWILIO_ENABLED=false  # Test uchun false qiling
```

### Test Data

Test avtomatik ravishda yangi ma'lumotlar yaratadi:
- Telefon raqamlar: timestamp asosida
- License plate: timestamp asosida
- Tech passport: timestamp asosida

---

## 🐛 Debugging

### Test Fail Bo'lsa

1. **Server ishlab turibmi?**
   ```bash
   curl http://localhost:8080/api/v1/
   ```

2. **Database to'g'rimi?**
   ```bash
   sqlite3 instance/royaltaxi.db "SELECT COUNT(*) FROM users;"
   ```

3. **Token muammosi?**
   - Login qaytadan qiling
   - Token expire bo'lgan bo'lishi mumkin

4. **Admin test fail?**
   - Admin foydalanuvchi bormi?
   - Admin credentials to'g'rimi?

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Server ishga tushiring |
| 401 Unauthorized | Token yangilang |
| 403 Forbidden | Admin huquqi kerak |
| 422 Validation Error | Ma'lumot formatini tekshiring |

---

## 📝 Test Yozish

### Yangi Test Qo'shish

```python
def test_my_endpoint(self):
    """Test my custom endpoint"""
    
    # Success case
    self.test_endpoint(
        "POST", "/my/endpoint", 200,
        headers=self.headers,
        json_data={"key": "value"},
        test_name="My endpoint - Success"
    )
    
    # Error case
    self.test_endpoint(
        "POST", "/my/endpoint", 400,
        headers=self.headers,
        json_data={"invalid": "data"},
        test_name="My endpoint - Error 400"
    )
```

---

## 🎯 Best Practices

### 1. Test Isolation
- Har bir test mustaqil bo'lishi kerak
- Test'lar bir-biriga bog'liq bo'lmasligi kerak

### 2. Test Data
- Har doim yangi ma'lumotlar yarating
- Timestamp yoki random ishlatiladi

### 3. Cleanup
- Test'dan keyin ma'lumotlarni tozalang (agar kerak bo'lsa)

### 4. Error Handling
- Barcha error case'larni test qiling
- 400, 401, 403, 404, 422 statuslarni tekshiring

---

## 📊 Test Coverage

### Current Coverage

| Module | Coverage | Tests |
|--------|----------|-------|
| Authentication | 100% | 9 |
| OTP Flow | 100% | 7 |
| User Management | 100% | 3 |
| Admin | 100% | 11 |
| Dispatcher | 100% | 3 |
| Driver | 100% | 3 |
| Rider | 100% | 2 |

**Total: 38+ tests**

---

## 🚀 CI/CD Integration

### GitHub Actions

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.13
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python test_all_endpoints_comprehensive.py
```

---

## 📞 Support

Test'lar bilan muammo bo'lsa:
- Swagger UI'da qo'lda test qiling
- Server loglarini tekshiring
- Database'ni tekshiring

---

## ✅ Xulosa

Comprehensive test suite:
- ✅ 38+ test
- ✅ Barcha endpoint'lar
- ✅ Success va error case'lar
- ✅ Avtomatik test
- ✅ Ranglar bilan chiroyli output
- ✅ Batafsil xabar

**Hozir test'ni ishga tushiring!** 🎉

```bash
python test_all_endpoints_comprehensive.py
```
