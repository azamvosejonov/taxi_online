#!/usr/bin/env python3
"""
Database initialization script for Royal Taxi
"""
from database import engine, Base
from models import *

def init_database():
    """Initialize database tables"""
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("Available tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    init_database()
