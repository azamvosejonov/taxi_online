# Royal Taxi Test Suite

Bu loyihada FastAPI ilovasining to'liq test to'plami mavjud.

## Test fayllari

### 1. `conftest.py`
Test konfiguratsiyasi va fixture fayli. Test uchun:
- Test ma'lumotlar bazasi
- Test client
- Test foydalanuvchilari (user, driver, admin)
- Authentication headers

### 2. `test_models.py`
Ma'lumotlar modeli testlari:
- User modeli
- Ride modeli
- Payment modeli
- Transaction modeli
- Vehicle modeli
- PromoCode modeli

### 3. `test_auth.py`
Autentifikatsiya testlari:
- Parol hashing va tekshirish
- JWT token yaratish
- Token muddati tugashi
- Noto'g'ri tokenlar

### 4. `test_business_logic.py`
Biznes logika testlari:
- Masofa hisoblash (Haversine formulasi)
- Narx hisoblash (iqtisodiy va komfort)
- Chegaraviy holatlar

### 5. `test_api.py`
API endpoint testlari:
- User registration va login
- Ride booking va boshqarish
- Payment processing
- Admin funksiyalari
- Promo code tizimi
- Authentication va authorization

## Testlarni ishga tushirish

### Barcha testlarni ishga tushirish:
```bash
pytest
```

### Muayyan test faylini ishga tushirish:
```bash
pytest test_models.py
pytest test_auth.py
pytest test_business_logic.py
pytest test_api.py
```

### Verbose mode:
```bash
pytest -v
```

### Coverage report bilan:
```bash
pytest --cov=main --cov=models --cov=auth --cov-report=html
```

### Test dependencies o'rnatish:
```bash
pip install -r test-requirements.txt
```

## Test struktura

Har bir test faylida:
- Class-based test tuzilmasi
- Descriptive test nomlari
- Assertions va validations
- Database rollback har bir testdan keyin
- Authentication va authorization testlar

## Test ma'lumotlari

Testlar quyidagi ma'lumotlardan foydalanadi:
- Test database: `test_royaltaxi.db`
- Test users:
  - Regular user: `test@example.com`
  - Driver: `driver@example.com`
  - Admin: `admin@example.com`
- Barcha parollar: `testpassword`

## Test qoplami

Testlar quyidagi funksiyalarni qoplaydi:
- ✅ Model CRUD operations
- ✅ Authentication va authorization
- ✅ API endpoints
- ✅ Business logic
- ✅ Error handling
- ✅ Database relationships
- ✅ Edge cases

## Continuous Integration

Testlar CI/CD pipeline da avtomatik ishga tushishi uchun:
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r test-requirements.txt
      - name: Run tests
        run: pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

Bu test to'plami kod sifatini ta'minlaydi va regression testlar sifatida xizmat qiladi.
