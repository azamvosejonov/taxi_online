#!/bin/bash

echo "🔧 Royal Taxi Database Rebuild Script"
echo "======================================"

# 1. Stop server (if running)
echo "1️⃣ Stopping server..."
pkill -f "uvicorn main:app" 2>/dev/null || true

# 2. Clean cache
echo "2️⃣ Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 3. Backup old database
echo "3️⃣ Backing up old database..."
if [ -f instance/royaltaxi.db ]; then
    mv instance/royaltaxi.db instance/royaltaxi.db.backup.$(date +%s)
    echo "   ✅ Backup created"
fi

# 4. Create new database
echo "4️⃣ Creating new database..."
source .venv/bin/activate
python << 'EOF'
from database import Base, engine
from models import *  # Import all models

# Create all tables
Base.metadata.create_all(bind=engine)

# Verify
import sqlite3
conn = sqlite3.connect('instance/royaltaxi.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
print(f"   ✅ Created {len(tables)} tables: {', '.join(tables)}")

# Check users table columns
cursor.execute("PRAGMA table_info(users);")
columns = cursor.fetchall()
print(f"   ✅ Users table has {len(columns)} columns")

# Check for is_on_duty
has_is_on_duty = any(col[1] == 'is_on_duty' for col in columns)
if has_is_on_duty:
    print("   ✅ is_on_duty column exists!")
else:
    print("   ❌ is_on_duty column missing!")
    exit(1)

conn.close()
EOF

if [ $? -ne 0 ]; then
    echo "❌ Database creation failed!"
    exit 1
fi

# 5. Create admin user
echo "5️⃣ Creating admin user..."
python create_admin_direct.py

echo ""
echo "======================================"
echo "✅ Database rebuild complete!"
echo ""
echo "Now start the server:"
echo "  uvicorn main:app --host 0.0.0.0 --port 8080 --reload"
echo ""
