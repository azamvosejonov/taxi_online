# Server Restart Yo'riqnomasi

## ❌ Muammo
SQLAlchemy eski model cache'ni ishlatmoqda. `is_on_duty` koloni database'da bor, lekin server uni ko'rmayapti.

## ✅ Yechim

### 1. Serverni To'liq To'xtating
Terminal'da **CTRL+C** bosing (bir necha marta kerak bo'lishi mumkin)

### 2. Python Cache'ni Tozalang
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
```

### 3. Serverni Qayta Ishga Tushiring
```bash
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. Test'ni Ishga Tushiring
Yangi terminal oching:
```bash
cd /home/azam/Desktop/yaratish/royaltaxi
source .venv/bin/activate
python test_all_apis_complete.py
```

## 🔍 Tekshirish

Database'da kolon borligini tekshirish:
```bash
sqlite3 instance/royaltaxi.db "PRAGMA table_info(users);" | grep is_on_duty
```

Natija:
```
28|is_on_duty|BOOLEAN|0|0|0
```

✅ Kolon mavjud!

## 📝 Eslatma

`--reload` rejimi ba'zan SQLAlchemy model cache'ni yangilamaydi. Agar muammo davom etsa:
1. CTRL+C bilan to'xtating
2. Cache tozalang
3. Qayta ishga tushiring
