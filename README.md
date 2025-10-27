# Royal Taxi Backend

A comprehensive backend system for a ride-hailing platform built with FastAPI, PostgreSQL, and Redis.

## Features

### 🚗 Core Features
- **User Management**: Registration, authentication, profile management
- **Ride Booking**: Real-time ride booking with location tracking
- **Driver Management**: Driver registration, vehicle management, approval system
- **Payment System**: Commission-based payment processing
- **Real-time Communication**: WebSocket-based chat and notifications
- **Admin Panel**: Complete administrative control

### 📱 Advanced Features
- **Push Notifications**: Firebase Cloud Messaging integration
- **File Upload**: Profile pictures and document management
- **Advanced Analytics**: Detailed reporting and metrics
- **Promo Codes**: Marketing and discount system
- **Surge Pricing**: Dynamic pricing based on demand
- **Vehicle Management**: Advanced vehicle features and types
- **Security & Performance**: Redis caching, rate limiting, security headers
- **Testing Infrastructure**: Comprehensive test suite

### 🛠 Technical Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL / SQLite
- **Cache & Rate Limiting**: Redis
- **Authentication**: JWT tokens
- **Real-time**: WebSockets
- **Push Notifications**: Firebase FCM
- **File Storage**: Local storage (configurable for cloud)
- **Testing**: pytest
- **Containerization**: Docker & Docker Compose

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, uses SQLite by default)
- Redis (optional, but recommended)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd royaltaxi
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Run database migrations**
   ```bash
   python main.py  # This will create the database tables
   ```

6. **Start the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The API will be available at `http://localhost:8000`

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Copy environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase credentials and other settings
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

This will start:
- PostgreSQL database
- Redis cache
- Main application
- Celery worker (for background tasks)
- Celery beat (for scheduled tasks)
- Flower (Celery monitoring dashboard)

3. **Access the application**
   - API: http://localhost:8000
   - Flower dashboard: http://localhost:5555

### Manual Docker Build

```bash
# Build and run
docker build -t royaltaxi .
docker run -p 8000:8000 royaltaxi
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_main.py
```

### Test Coverage
The test suite covers:
- User authentication and registration
- Ride booking and management
- API endpoints functionality
- Database operations
- Error handling

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./royaltaxi.db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `FIREBASE_CREDENTIALS_PATH` | Firebase credentials file path | `firebase-credentials.json` |
| `ENVIRONMENT` | Application environment | `development` |

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile

### Rides
- `POST /rides/book` - Book a new ride
- `GET /rides` - Get user's rides
- `PUT /rides/{ride_id}/status` - Update ride status
- `POST /rides/{ride_id}/track` - Record GPS track

### Drivers
- `POST /driver/vehicles` - Register vehicle
- `GET /driver/vehicles` - Get driver's vehicles
- `POST /driver/deposit` - Make deposit
- `GET /driver/balance` - Get driver balance

### Admin
- `POST /admin/approve-driver` - Approve driver
- `GET /admin/analytics/daily` - Daily analytics
- `GET /admin/analytics/weekly` - Weekly analytics
- `POST /admin/promo-codes` - Create promo codes
- `POST /admin/surge-areas` - Create surge areas

### Notifications
- `POST /fcm/register` - Register FCM token
- `GET /notifications` - Get user notifications
- `POST /upload/profile-picture` - Upload profile picture

## Project Structure

```
royaltaxi/
├── main.py              # Main FastAPI application
├── models.py            # Database models
├── auth.py              # Authentication utilities
├── test_main.py         # Test suite
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── pytest.ini         # Test configuration
├── .env.example       # Environment variables template
└── README.md          # This file
```

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for public functions
- Keep functions small and focused

### Database Migrations
Currently using SQLAlchemy's `create_all()` for simplicity. For production, consider using Alembic for migrations.

### Logging
Application logs are configured for different environments. Check the logs for debugging and monitoring.

## Production Deployment

### Security Checklist
- [ ] Set strong SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Set up Firebase credentials
- [ ] Configure email settings
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts

### Performance Optimization
- [ ] Enable Redis caching
- [ ] Configure database connection pooling
- [ ] Set up CDN for static files
- [ ] Enable compression
- [ ] Configure background task processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team

---

**Happy coding! 🚕**
