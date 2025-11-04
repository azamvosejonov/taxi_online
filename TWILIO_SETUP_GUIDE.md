# Twilio SMS Integration - Royal Taxi API

## Twilio Hisob Yaratish va Sozlash

### 1. Twilio Hisob Ochish

1. **Twilio saytiga kiring:** https://www.twilio.com/
2. **"Sign up" tugmasini bosing**
3. Ma'lumotlaringizni kiriting:
   - Email
   - Parol
   - Ism va Familiya
   - Telefon raqam (tasdiqlash uchun)

### 2. Telefon Raqamni Tasdiqlash

1. Twilio sizning telefon raqamingizga tasdiqlash kodi yuboradi
2. Kodni kiriting va tasdiqlang

### 3. Trial Account Sozlamalari

**Trial account bilan:**
- **$15.50 kredit** beriladi (bepul)
- Faqat **tasdiqlangan telefon raqamlarga** SMS yuborishingiz mumkin
- Har bir SMS **~$0.0075** turadi

### 4. Twilio Credentials Olish

1. **Twilio Console**ga kiring: https://console.twilio.com/
2. Dashboard'da quyidagilarni ko'rasiz:
   - **Account SID** - masalan: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Auth Token** - "Show" tugmasini bosing

### 5. Telefon Raqam Olish

1. Twilio Console'da **"Phone Numbers"** bo'limiga o'ting
2. **"Buy a number"** tugmasini bosing
3. **Country:** United States (yoki boshqa mamlakat)
4. **Capabilities:** SMS ni belgilang
5. **Search** tugmasini bosing
6. Raqamni tanlang va **"Buy"** tugmasini bosing
7. Sizning Twilio telefon raqamingiz: `+1234567890` formatida bo'ladi

### 6. Verified Caller IDs (Trial Account uchun)

Trial account bilan faqat tasdiqlangan raqamlarga SMS yuborishingiz mumkin:

1. **"Phone Numbers" → "Verified Caller IDs"** ga o'ting
2. **"Add a new Caller ID"** tugmasini bosing
3. Test qilmoqchi bo'lgan telefon raqamni kiriting
4. Twilio sizga tasdiqlash kodi yuboradi
5. Kodni kiriting va tasdiqlang

---

## Royal Taxi API'da Sozlash

### 1. .env Faylini Yangilash

`.env` faylini oching va quyidagi qatorlarni o'zgartiring:

```env
# Twilio SMS Configuration
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

**Muhim:**
- `TWILIO_ENABLED=true` - SMS yuborishni yoqish
- `TWILIO_ACCOUNT_SID` - Twilio Console'dan olingan Account SID
- `TWILIO_AUTH_TOKEN` - Twilio Console'dan olingan Auth Token
- `TWILIO_PHONE_NUMBER` - Twilio'dan sotib olingan telefon raqam

### 2. Serverni Qayta Ishga Tushirish

```bash
# Serverni to'xtatish
pkill -f "uvicorn main:app"

# Serverni ishga tushirish
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

---

## Test Qilish

### 1. OTP Yuborish (SMS orqali)

```bash
curl -X POST http://localhost:8080/api/v1/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567"}'
```

**Response (Twilio yoqilgan bo'lsa):**
```json
{
  "message": "Tasdiqlash kodi +998901234567 raqamiga yuborildi. Kod 5 daqiqa davomida amal qiladi.",
  "phone": "+998901234567",
  "expires_in": 300
}
```

**Eslatma:** `otp_code` maydoni response'da bo'lmaydi, chunki SMS yuborilgan.

**Response (Twilio o'chirilgan bo'lsa - development mode):**
```json
{
  "message": "Tasdiqlash kodi +998901234567 raqamiga yuborildi. Kod 5 daqiqa davomida amal qiladi.",
  "phone": "+998901234567",
  "expires_in": 300,
  "otp_code": "123456"
}
```

### 2. SMS Matnini Tekshirish

Telefon raqamingizga quyidagi matn keladi:

```
Royal Taxi tasdiqlash kodi: 123456
Kod 5 daqiqa davomida amal qiladi.
Agar siz bu kodni so'ramagan bo'lsangiz, bu xabarni e'tiborsiz qoldiring.
```

### 3. Server Loglarini Tekshirish

Server konsolida quyidagi xabarlarni ko'rasiz:

**SMS muvaffaqiyatli yuborilsa:**
```
✅ Twilio SMS service initialized successfully
✅ SMS sent to +998901234567. Message SID: SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**SMS yuborishda xatolik bo'lsa:**
```
⚠️ Failed to send SMS to +998901234567
```

**Twilio o'chirilgan bo'lsa:**
```
Twilio SMS service disabled (TWILIO_ENABLED=false)
📱 OTP for +998901234567: 123456
```

---

## Production uchun Tavsiyalar

### 1. Paid Account'ga O'tish

Trial account cheklangan:
- Faqat tasdiqlangan raqamlarga SMS
- Cheklangan kredit

**Paid account uchun:**
1. Twilio Console'da **"Upgrade"** tugmasini bosing
2. To'lov ma'lumotlarini kiriting
3. Kerakli miqdorda kredit qo'shing

### 2. SMS Narxlari

| Mamlakat | Narx (1 SMS) |
|----------|--------------|
| O'zbekiston | ~$0.0530 |
| Rossiya | ~$0.0117 |
| AQSH | ~$0.0079 |
| Turkiya | ~$0.0065 |

**Misol hisob:**
- 1000 ta SMS O'zbekistonga = ~$53.00
- 10,000 ta SMS O'zbekistonga = ~$530.00

### 3. Xavfsizlik

**Auth Token'ni himoya qiling:**
- `.env` faylini `.gitignore`ga qo'shing
- Environment variables'dan foydalaning
- Production serverda faqat environment variables

**Rate Limiting:**
```python
# Bir telefon raqamga 1 daqiqada 1 ta OTP
# Bir IP'dan 1 daqiqada 5 ta OTP
```

### 4. Monitoring

Twilio Console'da:
- **Logs** - barcha yuborilgan SMS'lar
- **Usage** - SMS statistikasi
- **Billing** - xarajatlar

---

## Muammolarni Hal Qilish

### SMS Kelmayapti

**1. Twilio sozlamalarini tekshiring:**
```bash
# .env faylida
TWILIO_ENABLED=true  # true ekanligini tekshiring
```

**2. Credentials to'g'riligini tekshiring:**
- Account SID to'g'rimi?
- Auth Token to'g'rimi?
- Phone Number to'g'rimi?

**3. Trial account uchun:**
- Telefon raqam Verified Caller IDs'da bormi?

**4. Server loglarini tekshiring:**
```bash
# Xatolik xabarlarini qidiring
grep -i "twilio" logs/app.log
```

### "Authentication Error" Xatosi

```
ERROR: Twilio error sending SMS: Unable to create record: Authenticate
```

**Yechim:**
- Account SID va Auth Token'ni qayta tekshiring
- Twilio Console'da credentials'ni yangilang

### "Invalid Phone Number" Xatosi

```
ERROR: Twilio error sending SMS: Invalid phone number
```

**Yechim:**
- Telefon raqam international formatda bo'lishi kerak: `+998901234567`
- Mamlakat kodi bilan boshlangan bo'lishi kerak: `+998`

### "Insufficient Balance" Xatosi

```
ERROR: Twilio error sending SMS: Insufficient balance
```

**Yechim:**
- Twilio hisobingizga kredit qo'shing
- Billing sahifasiga o'ting va to'lov qiling

---

## O'zbek Raqamlar uchun Maxsus Sozlamalar

O'zbekiston telefon raqamlari formati: `+998XXXXXXXXX`

**Misol raqamlar:**
- `+998901234567` - Beeline
- `+998931234567` - UMS
- `+998971234567` - Ucell
- `+998881234567` - Perfectum Mobile

**Regex pattern:**
```python
r"^\+998\d{9}$"
```

---

## Alternative SMS Gateway'lar (O'zbekiston uchun)

Agar Twilio qimmat bo'lsa, quyidagilardan foydalanishingiz mumkin:

### 1. Eskiz.uz
- **Narx:** ~50-100 so'm/SMS
- **Website:** https://eskiz.uz/
- **API:** REST API

### 2. Playmobile
- **Narx:** ~50-80 so'm/SMS
- **Website:** https://playmobile.uz/
- **API:** REST API

### 3. SMS.uz
- **Narx:** ~60-100 so'm/SMS
- **Website:** https://sms.uz/
- **API:** REST API

---

## Qo'shimcha Resurslar

- **Twilio Documentation:** https://www.twilio.com/docs/sms
- **Twilio Console:** https://console.twilio.com/
- **Twilio Pricing:** https://www.twilio.com/sms/pricing
- **Twilio Support:** https://support.twilio.com/

---

## Xulosa

Twilio integratsiyasi muvaffaqiyatli amalga oshirildi:

✅ SMS yuborish funksiyasi qo'shildi
✅ Development va Production rejimlar
✅ Xatoliklarni boshqarish
✅ Logging va monitoring
✅ O'zbek telefon raqamlari qo'llab-quvvatlanadi

**Keyingi qadamlar:**
1. Twilio hisob ochish
2. .env faylini sozlash
3. Test qilish
4. Production'ga o'tkazish
