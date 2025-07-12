# Email Auditor - Production Ready

A professional email analysis and quality assessment service with a modern web interface, API access, and production-ready architecture.

## 🚀 Features

- **Email Content Analysis**: Comprehensive grammar checking, style analysis, and quality scoring
- **User Authentication**: Secure login/registration with email/mobile OTP verification
- **API Access**: RESTful API for programmatic access with rate limiting
- **Production Ready**: Scalable architecture with proper separation of concerns
- **Modern Web UI**: Responsive design with Bootstrap 5 and custom styling
- **Real-time Results**: Instant feedback on email quality and improvement suggestions

## 🏗️ Architecture

The application follows a production-ready architecture with:

- **Application Factory Pattern**: Modular Flask application creation
- **Blueprint Structure**: Organized routes and views
- **Service Layer**: Business logic separation
- **Model Layer**: Database models with relationships
- **Configuration Management**: Environment-based configuration
- **Rate Limiting**: API usage tracking and limits
- **Logging**: Comprehensive logging system

## 📁 Project Structure

```
EmailAuditor/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── otp.py              # OTP model
│   │   └── audit.py            # Email audit model
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── email_service.py    # Email/OTP service
│   │   ├── audit_service.py    # Email auditing service
│   │   ├── email_parser.py     # Email parsing
│   │   ├── rules_engine.py     # Rules evaluation
│   │   ├── audit_report.py     # Report generation
│   │   └── rules_impl.py       # Rule implementations
│   ├── web/                    # Web interface routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   └── rate_limiter.py
│   ├── templates/              # HTML templates
│   └── static/                 # Static files (CSS, JS)
├── config/                     # Configuration management
│   ├── __init__.py
│   └── config.py
├── tests/                      # Test suite
├── migrations/                 # Database migrations
├── scripts/                    # Utility scripts
├── logs/                       # Application logs
├── uploads/                    # File uploads
├── wsgi.py                     # WSGI entry point
├── manage.py                   # Management commands
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Production Docker image
├── docker-compose.yml          # Multi-service deployment
├── env.example                 # Environment variables template
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EmailAuditor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

5. **Initialize database**
   ```bash
   python manage.py init-db
   ```

6. **Run the application**
   ```bash
   python wsgi.py
   ```

7. **Access the application**
   - Web UI: http://localhost:5000
   - API Documentation: http://localhost:5000/docs

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production

# Database Configuration
DATABASE_URL=sqlite:///email_auditor.db
# For production: postgresql://user:password@localhost/email_auditor

# Email Configuration (for OTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# Rate Limiting
FREE_TIER_DAILY_LIMIT=5
PREMIUM_TIER_DAILY_LIMIT=100

# Security
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Email Configuration

For OTP functionality, configure SMTP settings:

1. **Gmail Setup**:
   - Enable 2-factor authentication
   - Generate an App Password
   - Use the App Password in `SMTP_PASSWORD`

2. **Other Email Providers**:
   - Update `SMTP_SERVER` and `SMTP_PORT` accordingly
   - Use appropriate credentials

## 🚀 Production Deployment

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Web UI: http://localhost:5000
   - API: http://localhost:5000/api

### Manual Deployment

1. **Set production environment**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   ```

2. **Use Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
   ```

3. **Set up reverse proxy** (nginx recommended)

4. **Configure SSL/TLS** for secure communication

## 📚 API Documentation

### Authentication

All API requests require an API key in the header:
```
X-API-Key: your_api_key_here
```

### Endpoints

**1. Audit Email**
```http
POST /api/audit
Content-Type: multipart/form-data
X-API-Key: your_api_key

file: [.eml file]
```

**2. Check Usage**
```http
GET /api/usage
X-API-Key: your_api_key
```

**3. Manage API Key**
```http
GET /api/key
POST /api/key
```

### Example Usage

**Python:**
```python
import requests

api_key = "your_api_key_here"
url = "http://localhost:5000/api/audit"

with open("email.eml", "rb") as f:
    files = {"file": f}
    headers = {"X-API-Key": api_key}
    response = requests.post(url, files=files, headers=headers)
    
result = response.json()
print(f"Email Score: {result['score']}")
```

**cURL:**
```bash
curl -X POST \
  -H "X-API-Key: your_api_key_here" \
  -F "file=@email.eml" \
  http://localhost:5000/api/audit
```

## 🧪 Testing

### Run Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app tests/
```

## 🔧 Management Commands

### Initialize Database
```bash
python manage.py init-db
```

### Create Admin User
```bash
python manage.py create-admin
```

### Test Email Configuration
```bash
python manage.py test-email
```

## 📊 Monitoring

### Logs
Application logs are stored in `logs/app.log` with rotation.

### Health Check
```http
GET /health
```

## 🔒 Security Features

- **API Key Authentication**: Secure API access
- **Rate Limiting**: Prevents abuse
- **Input Validation**: File type and size validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **XSS Protection**: Template escaping
- **CSRF Protection**: Built-in Flask protection

## 📈 Scalability

- **Database**: Supports PostgreSQL for production
- **Caching**: Redis integration ready
- **Background Tasks**: Celery integration ready
- **Load Balancing**: Gunicorn with multiple workers
- **Horizontal Scaling**: Stateless application design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the configuration examples

## 🔄 Changelog

### v2.0.0 - Production Ready
- Complete code refactoring with proper architecture
- Application factory pattern
- Service layer implementation
- Production deployment support
- Comprehensive testing setup
- Monitoring and logging
- Security enhancements