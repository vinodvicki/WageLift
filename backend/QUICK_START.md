# WageLift Backend - Quick Start Guide

## 🚀 Running the Application

### Prerequisites
- Python 3.13+ installed
- Virtual environment activated

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Application
```bash
# Start the FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the Application
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **API Root:** http://localhost:8000/

## 🧪 Testing the System

### Run Core Functionality Tests
```bash
python core_functionality_test.py
```

Expected output:
```
🎉 ALL TESTS PASSED! Your WageLift backend is fully functional!
```

### Test Individual Components
```bash
# Test simple FastAPI app
python simple_app_test.py

# Test configuration
python -c "from app.core.config import settings; print(f'Project: {settings.PROJECT_NAME}')"

# Test database connection
python -c "from app.core.database import test_db_connection; print('DB OK' if test_db_connection() else 'DB Error')"
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
# Database (optional - defaults to SQLite)
POSTGRES_SERVER=localhost
POSTGRES_USER=wagelift
POSTGRES_PASSWORD=your_password
POSTGRES_DB=wagelift

# External APIs (optional for basic functionality)
OPENAI_API_KEY=your_openai_key
BLS_API_KEY=your_bls_key
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_auth0_client_id

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Development vs Production
The system automatically detects the environment:
- **Development:** DEBUG=True, detailed logging, test-friendly middleware
- **Production:** Set `DEBUG=False` in environment variables

## 📊 Monitoring

### Health Checks
```bash
curl http://localhost:8000/health
```

### Metrics (Prometheus)
```bash
curl http://localhost:8000/metrics
```

### Database Stats
```bash
python -c "from app.core.database import get_db_stats; import json; print(json.dumps(get_db_stats(), indent=2))"
```

## 🛠️ Development

### Project Structure
```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core functionality (config, database, error handling)
│   ├── models/       # Database models
│   ├── services/     # External service integrations
│   └── main.py       # FastAPI application
├── tests/            # Test files
└── requirements.txt  # Dependencies
```

### Key Features
- **Error Handling:** Comprehensive error prevention and recovery
- **Database:** SQLite (dev) / PostgreSQL (prod) with connection pooling
- **Security:** Input validation, security headers, CORS protection
- **Monitoring:** Prometheus metrics, structured logging
- **Performance:** Async support, connection pooling, compression

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors:**
   ```bash
   # Ensure you're in the backend directory
   cd backend
   # Activate virtual environment
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Database Errors:**
   ```bash
   # Test database connection
   python -c "from app.core.database import test_db_connection; print('OK' if test_db_connection() else 'FAIL')"
   ```

3. **Port Already in Use:**
   ```bash
   # Use different port
   uvicorn app.main:app --port 8001
   ```

4. **Missing Dependencies:**
   ```bash
   # Install all dependencies
   pip install -r requirements.txt
   ```

### Getting Help
- Check logs in the console output
- Review the `SYSTEM_OPTIMIZATION_REPORT.md` for detailed information
- Run the core functionality test to validate system health

## ✅ Verification Checklist

Before deploying, ensure:
- [ ] All tests pass: `python core_functionality_test.py`
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Database connection working
- [ ] Required environment variables set (for production features)

**Status: ✅ SYSTEM READY FOR USE**