# 🚗 Royal Taxi Backend - Organized Structure

A clean, well-organized FastAPI backend for the Royal Taxi ride-sharing platform with proper separation of concerns.

## 📁 Project Structure

```
/home/azam/Desktop/yaratish/royaltaxi/
├── main_new.py              # Main application file (organized)
├── main_old.py              # Original main file (backup)
├── config.py                # Configuration management
├── database.py              # Database connection and session management
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic schemas for API
├── routers/                 # API endpoint routers
│   ├── __init__.py
│   ├── auth.py              # Authentication endpoints
│   ├── rides.py             # Ride management endpoints
│   ├── users.py             # User management endpoints
│   ├── admin.py             # Admin panel endpoints
│   ├── payments.py          # Payment processing endpoints
│   ├── files.py             # File upload endpoints
│   └── websocket.py         # WebSocket connections
├── utils/                   # Utility functions
│   ├── __init__.py
│   └── helpers.py           # Common helper functions
├── conftest.py              # Test configuration
├── requirements.txt         # Python dependencies
└── test files...           # Test files
```

## 🏗️ Architecture Overview

### **Clean Architecture Principles**
- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: FastAPI's dependency system for clean code
- **Configuration Management**: Centralized settings in `config.py`
- **Error Handling**: Global error handlers for consistent responses
- **Middleware**: Rate limiting, CORS, and security middleware

### **Module Responsibilities**

#### **Core Files**
- **`config.py`**: Application settings, database URLs, API configurations
- **`database.py`**: SQLAlchemy engine, session management, database connection
- **`models.py`**: Database models and relationships
- **`schemas.py`**: Pydantic models for request/response validation

#### **Router Modules**
- **`routers/auth.py`**: User registration, login, authentication
- **`routers/rides.py`**: Ride booking, tracking, management
- **`routers/users.py`**: User profile, settings, preferences
- **`routers/admin.py`**: Admin panel, analytics, user management
- **`routers/payments.py`**: Payment processing, transactions
- **`routers/files.py`**: File uploads, media management
- **`routers/websocket.py`**: Real-time communication

#### **Utility Modules**
- **`utils/helpers.py`**: Common functions, validators, calculators

## 🚀 Getting Started

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Run the Application**
```bash
# Development mode
python main_new.py

# Or with uvicorn
uvicorn main_new:app --reload --host 0.0.0.0 --port 8000
```

### **3. Test the Structure**
```bash
# Test if the organized structure loads correctly
python -c "from main_new import app; print('✅ Organized structure works!')"
```

## 📋 API Structure

### **Base URL**: `http://localhost:8000/api/v1`

### **Available Routers**:
- **Authentication**: `/auth/*` - Login, register, token management
- **Rides**: `/rides/*` - Book, track, manage rides
- **Users**: `/users/*` - Profile, settings, preferences
- **Admin**: `/admin/*` - Analytics, user management, system stats
- **Payments**: `/payments/*` - Payment processing, transactions
- **Files**: `/files/*` - Upload, download, media management
- **WebSocket**: `/ws/*` - Real-time communication

### **Health Endpoints**:
- `GET /` - API status
- `GET /health` - Detailed health check
- `GET /api/info` - API information

## ⚙️ Configuration

All configuration is centralized in `config.py`:

```python
# Database settings
DATABASE_URL = "sqlite:///./royaltaxi.db"
TESTING = False

# Security settings
SECRET_KEY = "your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60

# Vehicle types and pricing
VEHICLE_TYPES = {
    "economy": {"base_fare": 10000, "per_km_rate": 2000},
    "comfort": {"base_fare": 15000, "per_km_rate": 3000},
    "business": {"base_fare": 25000, "per_km_rate": 5000}
}
```

## 🛠️ Development Guidelines

### **Adding New Endpoints**
1. Create/update the appropriate router in `routers/`
2. Add request/response schemas in `schemas.py`
3. Update models if needed in `models.py`
4. Add tests in the appropriate test file

### **Database Changes**
1. Update models in `models.py`
2. Create new migrations if needed
3. Update schemas in `schemas.py`
4. Test database operations

### **Configuration Changes**
1. Update `config.py` with new settings
2. Update environment variables if needed
3. Test configuration loading

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest test_models.py     # Database models
pytest test_api.py       # API endpoints
pytest test_auth.py      # Authentication

# Run with coverage
pytest --cov=. --cov-report=html
```

## 🔒 Security Features

- **Rate Limiting**: Configurable request limits per minute
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic schema validation
- **Error Handling**: Global error handlers
- **Authentication**: JWT token-based auth
- **Trusted Hosts**: Configurable host validation

## 📊 Monitoring & Analytics

- **Health Checks**: Automated health monitoring
- **Request Logging**: Structured logging
- **Performance Metrics**: Response time tracking
- **Error Tracking**: Global error handling
- **Database Monitoring**: Connection pool monitoring

## 🚀 Production Deployment

### **Environment Variables**
```bash
export DATABASE_URL="postgresql://user:pass@host:port/db"
export SECRET_KEY="your-production-secret"
export REDIS_URL="redis://host:port"
export FIREBASE_CREDENTIALS_PATH="/path/to/credentials.json"
export CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

### **Docker Deployment**
```bash
# Build and run with Docker
docker build -t royal-taxi-backend .
docker run -p 8000:8000 royal-taxi-backend
```

## 📈 Future Enhancements

- [ ] **API Documentation**: Auto-generated OpenAPI/Swagger docs
- [ ] **Caching Layer**: Redis-based response caching
- [ ] **Background Jobs**: Celery for async tasks
- [ ] **Monitoring**: Prometheus metrics and Grafana dashboards
- [ ] **Logging**: Structured logging with ELK stack
- [ ] **API Versioning**: Multiple API versions support
- [ ] **WebSocket Enhancements**: Real-time ride tracking
- [ ] **Push Notifications**: Firebase integration

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Follow the established structure**
4. **Add tests for new features**
5. **Update documentation**
6. **Submit a pull request**

## 📞 Support

For questions or support:
- Check the organized structure documentation
- Review the configuration options in `config.py`
- Examine existing router patterns in `routers/`
- Check the utility functions in `utils/helpers.py`

---

**Royal Taxi Backend** - Clean, organized, and production-ready! 🚗✨
