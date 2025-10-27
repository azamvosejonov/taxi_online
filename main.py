"""
Royal Taxi API - Main application file
Clean, organized FastAPI application with proper structure
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from firebase_admin import credentials
from starlette.types import Lifespan
import os

from config import settings
from swagger_config import setup_swagger_ui
from database import engine, Base
from routers import (
    auth_router as auth,
    users_router as users,
    admin_router as admin,
)
from routers.dispatcher import router as dispatcher_router
from routers.driver import router as driver_router

# Import models for table creation
from models import *  # noqa

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database tables created successfully for {settings.api_title}")

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
        if hasattr(settings, 'firebase_credentials_path') and settings.firebase_credentials_path:
            import firebase_admin
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized for push notifications")
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
    """Custom Swagger UI with automatic token authorization"""
    html_path = os.path.join(os.path.dirname(__file__), "swagger_ui_custom.html")
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
app.include_router(dispatcher_router, prefix="/api/v1")
app.include_router(driver_router, prefix="/api/v1")

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
        "redis": "connected" if 'redis_client' in globals() and redis_client is not None else "disabled"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )