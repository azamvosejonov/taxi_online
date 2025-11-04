# Database Schema Fix - Royal Taxi

## ❌ Muammo

`models.py` da `User` modeli `hashed_password` kolonini kutardi, lekin database'da `password` koloni bor edi.

```
sqlite3.OperationalError: no such column: users.hashed_password
```

## ✅ Yechim

`models.py` ni database schema'ga moslashtirdik:

### O'zgarishlar:

1. **`hashed_password` → `password`**
   - Database'dagi haqiqiy kolon nomi `password`
   - Backward compatibility uchun `@property` qo'shildi

2. **Qo'shilgan kolonlar:**
   - `email`
   - `profile_photo`
   - `vehicle_type`
   - `vehicle_number`
   - `license_number`
   - `vehicle_model`
   - `current_location`
   - `city`
   - `is_on_duty`
   - `language`
   - `emergency_contact`
   - `approved_at`

3. **O'chirilgan kolonlar:**
   - `first_name` (faqat `full_name` ishlatiladi)
   - `last_name` (faqat `full_name` ishlatiladi)
   - `gender`
   - `date_of_birth`
   - `vehicle_make`
   - `position`
   - `license_plate` → `vehicle_number`
   - `tech_passport` → `license_number`

## 🔧 Backward Compatibility

`hashed_password` property qo'shildi:

```python
@property
def hashed_password(self):
    return self.password

@hashed_password.setter
def hashed_password(self, value):
    self.password = value
```

Bu eski kod ishlab turishini ta'minlaydi.

## 🚀 Keyingi Qadamlar

1. **Server restart qiling:**
   ```bash
   # CTRL+C bosing
   source .venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

2. **Test'ni qayta ishga tushiring:**
   ```bash
   python test_all_endpoints_comprehensive.py
   ```

## ✅ Natija

Endi barcha endpoint'lar ishlashi kerak:
- ✅ Register
- ✅ Login
- ✅ OTP flow
- ✅ Admin endpoints
- ✅ Driver endpoints
- ✅ Dispatcher endpoints
