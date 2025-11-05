"""
Royal Taxi API - Main application file
Clean, organized FastAPI application with proper structure
"""
from contextlib import asynccontextmanager
import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
import json
from typing import Dict, List
from datetime import datetime
try:
    from firebase_admin import credentials
except ImportError:
    credentials = None
# from celery import Celery  # Commented out temporarily
from starlette.types import Lifespan
from starlette.middleware.trustedhost import TrustedHostMiddleware
import os

from config import settings
from database import engine, Base

from websocket import manager  # Import WebSocket manager
from swagger_config import setup_swagger_ui  # Import Swagger setup

from routers import (
    auth_router as auth,
    users_router as users,
    admin_router as admin,
    files_router as files,
)
from routers.dispatcher import router as dispatcher_router
from routers.driver import router as driver_router
from routers.rider import router as rider_router  # Rider tracking router
from routers.services import router as services_router  # Additional services

# Import models for table creation
from models import *  # noqa

# Configure Celery application (used by worker/beat/flower via main.celery_app)
# celery_app = Celery(
#     "royaltaxi",
#     broker=settings.redis_url,
#     backend=settings.redis_url
# )

# celery_app.conf.update(
#     task_serializer="json",
#     accept_content=["json"],
#     result_serializer="json",
#     timezone="UTC",
#     enable_utc=True
# )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database tables created successfully for {settings.api_title}")
    try:
        db_url = str(engine.url)
        print(f"🗄️  Database URL: {db_url}")
        if engine.url.get_backend_name() == "sqlite":
            db_path = engine.url.database
            print(f"📁 SQLite file: {db_path}")
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [t[0] for t in cur.fetchall()]
                print(f"📋 Tables present: {tables}")
                cur.execute("PRAGMA table_info(users);")
                cols = [r[1] for r in cur.fetchall()]
                print(f"👤 users columns: {cols}")
                print(f"🔎 has is_on_duty: {'is_on_duty' in cols}")
                conn.close()
            except Exception as e:
                print(f"⚠️ SQLite introspection failed: {e}")
    except Exception as e:
        print(f"⚠️ Could not print DB diagnostics: {e}")

    # Initialize Redis connection if available
    try:
        import redis
        redis_client = redis.from_url(settings.redis_url)
        print("✅ Redis connection established")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        redis_client = None

    # Initialize Firebase if credentials available
    try:
        if credentials and hasattr(settings, 'firebase_credentials_path') and settings.firebase_credentials_path:
            import firebase_admin
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized for push notifications")
        elif not credentials:
            print("⚠️ Firebase not available (firebase_admin not installed)")
    except Exception as e:
        print(f"⚠️ Firebase initialization failed: {e}")

    yield

    # Cleanup (if needed)
    print(" Application shutting down...")

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url=None,  # Custom Swagger UI handled by endpoint
    redoc_url="/redoc"
)

# Configure Swagger UI
app = setup_swagger_ui(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
    expose_headers=["*", "Authorization"]
)

# Add trusted host middleware for security (in production)
if not getattr(settings, 'testing', False):
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure for production
    )

# Custom Swagger UI endpoint with auto-token handling
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    """Simple Swagger UI that shows all APIs"""
    html_path = os.path.join(os.path.dirname(__file__), "swagger_ui_simple.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    # Fallback to default if custom HTML not found
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Royal Taxi API")

# Include routers (cleaned)
app.include_router(auth, prefix="/api/v1")
app.include_router(users, prefix="/api/v1")
app.include_router(admin, prefix="/api/v1")
app.include_router(files, prefix="/api/v1")
app.include_router(dispatcher_router, prefix="/api/v1")
app.include_router(driver_router, prefix="/api/v1")
app.include_router(rider_router, prefix="/api/v1")  # Rider tracking APIs
app.include_router(services_router)  # Additional services (already has /api/v1 prefix)

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": f"{settings.api_title} is running",
        "version": settings.api_version,
        "status": "healthy"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.api_version,
        "database": "connected",
        "redis": "connected" if 'redis_client' in globals() and redis_client is not None else "disabled",
        "websocket": "enabled"
    }

# WebSocket endpoints for real-time tracking
@app.websocket("/ws/drivers/{driver_id}")
async def driver_websocket_endpoint(websocket: WebSocket, driver_id: int):
    """WebSocket endpoint for driver location updates"""
    await manager.connect(websocket, "drivers")
    try:
        while True:
            data = await websocket.receive_text()
            # Parse location data and broadcast to dispatchers
            try:
                location_data = json.loads(data)
                message = {
                    "type": "driver_location",
                    "driver_id": driver_id,
                    "location": location_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.broadcast(json.dumps(message), "dispatchers")
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, "drivers")

@app.websocket("/ws/dispatchers/{dispatcher_id}")
async def dispatcher_websocket_endpoint(websocket: WebSocket, dispatcher_id: int):
    """WebSocket endpoint for dispatcher monitoring"""
    await manager.connect(websocket, "dispatchers")
    try:
        while True:
            data = await websocket.receive_text()
            # Dispatcher can send commands to drivers
            try:
                command_data = json.loads(data)
                if command_data.get("type") == "command":
                    await manager.broadcast(json.dumps(command_data), "drivers")
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dispatchers")

@app.websocket("/ws/riders/{ride_id}")
async def rider_websocket_endpoint(websocket: WebSocket, ride_id: int):
    """WebSocket endpoint for rider ride tracking with real-time updates"""
    await manager.connect(websocket, "riders")
    try:
        # Send initial ride status
        initial_update = {
            "type": "ride_update",
            "ride_id": ride_id,
            "message": "Connected to ride tracking",
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(initial_update))

        while True:
            # Riders can send requests for updates, but mainly receive updates
            data = await websocket.receive_text()
            try:
                request_data = json.loads(data)
                if request_data.get("type") == "status_request":
                    # Send current ride status
                    status_update = {
                        "type": "status_response",
                        "ride_id": ride_id,
                        "status": "connected",
                        "message": "Real-time tracking active",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send_text(json.dumps(status_update))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, "riders")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )