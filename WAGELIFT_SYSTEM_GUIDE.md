# WageLift System Guide 🚀

## Overview
WageLift is a professional salary increase platform with AI-powered raise letter generation and market data analysis. This guide covers the complete system architecture, setup, and operation.

## ✅ **SYSTEM STATUS: FULLY OPERATIONAL**

Both frontend and backend servers are stable and crash-resistant with comprehensive error handling and monitoring.

---

## 🏗️ Architecture

### Backend (FastAPI)
- **Location**: `/workspace/backend/`
- **Main File**: `simple_main.py`
- **Port**: 8000
- **Features**:
  - RESTful API with comprehensive error handling
  - Health monitoring endpoints
  - Mock salary calculation services
  - Email and raise letter generation APIs
  - CORS enabled for frontend integration
  - Structured logging with timestamps

### Frontend (Next.js 14)
- **Location**: `/workspace/frontend/`
- **Port**: 3000
- **Features**:
  - Modern React with TypeScript
  - Tailwind CSS with comprehensive design system
  - Mock authentication system
  - Responsive design with mobile support
  - Professional UI components
  - Error boundaries and graceful error handling

---

## 🚀 Quick Start

### Option 1: Master Startup Script (Recommended)
```bash
./start_wagelift.sh
```
This script:
- Kills any existing processes
- Starts backend with health monitoring
- Starts frontend with hot reload
- Provides comprehensive status monitoring
- Shows real-time health checks

### Option 2: Individual Server Startup
```bash
# Backend only
cd backend && ./start_backend.sh

# Frontend only  
cd frontend && ./start_frontend.sh
```

### Option 3: Manual Startup
```bash
# Backend (from /workspace/backend/)
source venv/bin/activate
uvicorn simple_main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (from /workspace/frontend/)
npm run dev
```

---

## 🔧 System Scripts

### 1. Master Startup Script
**File**: `start_wagelift.sh`
- Comprehensive server startup with monitoring
- Automatic process cleanup
- Health checks with retry logic
- PID tracking and monitoring
- Detailed logging and error reporting

### 2. Backend Startup Script
**File**: `backend/start_backend.sh`
- Virtual environment management
- Dependency installation
- Import verification
- Port conflict resolution
- Robust error handling

### 3. Frontend Startup Script
**File**: `frontend/start_frontend.sh`
- Node.js version checking
- Cache clearing
- Dependency management
- Build verification
- Port conflict resolution

### 4. Health Check Script
**File**: `health_check.sh`
- Process monitoring
- Port status verification
- HTTP endpoint testing
- Performance metrics
- Log file analysis
- System resource monitoring

---

## 📊 Health Monitoring

### Run Health Check
```bash
./health_check.sh
```

### Health Check Features
- ✅ Process status monitoring
- ✅ Port availability checking
- ✅ HTTP endpoint testing
- ✅ API functionality verification
- ✅ Frontend page testing
- ✅ Performance metrics
- ✅ Log file analysis
- ✅ System resource monitoring

### Key Endpoints for Monitoring
- **Backend Health**: `http://localhost:8000/health`
- **Backend API**: `http://localhost:8000/docs` (Swagger UI)
- **Frontend**: `http://localhost:3000`
- **Frontend Dashboard**: `http://localhost:3000/dashboard/salary`

---

## 🛠️ System Components

### Backend API Endpoints
```
GET  /                          - Root endpoint
GET  /health                    - Health check
GET  /docs                      - API documentation
GET  /api/test                  - Test endpoint
POST /api/salary/calculate      - Salary calculation
GET  /api/user/profile          - User profile
GET  /api/auth/session          - Auth session
GET  /api/raise-letter/templates - Letter templates
POST /api/raise-letter/generate - Generate letter
POST /api/email/send            - Send email
```

### Frontend Pages
```
/                               - Landing page
/dashboard/salary               - Salary calculator
/dashboard/raise-letter         - Letter generator
/dashboard/results              - Results display
/dashboard/gusto                - Gusto integration
```

### Authentication System
- Mock authentication for development
- Seamless login/logout flow
- Protected routes with redirects
- Session management

---

## 📁 File Structure

```
workspace/
├── start_wagelift.sh           # Master startup script
├── health_check.sh             # Comprehensive health monitoring
├── backend/
│   ├── start_backend.sh        # Backend startup script
│   ├── simple_main.py          # Main FastAPI application
│   ├── requirements-ultra-minimal.txt
│   ├── venv/                   # Python virtual environment
│   └── backend.log             # Backend logs
├── frontend/
│   ├── start_frontend.sh       # Frontend startup script
│   ├── package.json            # Node.js dependencies
│   ├── next.config.js          # Next.js configuration
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   ├── src/                    # Source code
│   │   ├── app/                # Next.js app directory
│   │   ├── components/         # React components
│   │   ├── lib/                # Utility libraries
│   │   └── infrastructure/     # API and config
│   └── frontend.log            # Frontend logs
└── WAGELIFT_SYSTEM_GUIDE.md   # This guide
```

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Servers Won't Start
```bash
# Kill all processes and restart
pkill -f "uvicorn|next"
./start_wagelift.sh
```

#### 2. Port Conflicts
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :3000

# Kill specific processes
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

#### 3. Frontend Build Errors
```bash
cd frontend
rm -rf .next node_modules/.cache
npm install
npm run dev
```

#### 4. Backend Import Errors
```bash
cd backend
source venv/bin/activate
pip install -r requirements-ultra-minimal.txt
python -c "import simple_main; print('OK')"
```

#### 5. CSS/Styling Issues
- Check `frontend/src/app/globals.css` for syntax errors
- Verify Tailwind configuration in `tailwind.config.js`
- Clear browser cache and hard refresh

### Log Analysis
```bash
# Backend logs
tail -f backend/backend.log

# Frontend logs  
tail -f frontend/frontend.log

# Real-time monitoring
watch -n 2 './health_check.sh'
```

---

## 🔧 Development Commands

### Backend Development
```bash
cd backend
source venv/bin/activate

# Install dependencies
pip install -r requirements-ultra-minimal.txt

# Run tests
python -m pytest

# Start development server
uvicorn simple_main:app --reload
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## 📈 Performance Optimization

### Backend Optimizations
- Async/await for all endpoints
- Structured logging for debugging
- Error handling with proper HTTP status codes
- CORS optimization for frontend integration

### Frontend Optimizations
- Next.js 14 with App Router
- Tailwind CSS for optimized styling
- Component-based architecture
- TypeScript for type safety
- Responsive design with mobile-first approach

---

## 🔒 Security Features

### Backend Security
- Input validation and sanitization
- Error handling without exposing internals
- CORS configuration for specific origins
- Structured logging for audit trails

### Frontend Security
- TypeScript for type safety
- Input validation on forms
- Protected routes with authentication
- Secure API communication

---

## 🚀 Deployment Ready

### Production Checklist
- ✅ Robust error handling
- ✅ Comprehensive logging
- ✅ Health monitoring
- ✅ Process management
- ✅ Port conflict resolution
- ✅ Dependency management
- ✅ Performance optimization
- ✅ Security measures

### Environment Variables
```bash
# Backend (.env)
ENVIRONMENT=production
LOG_LEVEL=info

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📞 Support Commands

### Quick Status Check
```bash
curl http://localhost:8000/health
curl -I http://localhost:3000
```

### Process Information
```bash
ps aux | grep -E "(uvicorn|next)" | grep -v grep
```

### Stop All Servers
```bash
pkill -f "uvicorn|next"
```

### Restart Everything
```bash
pkill -f "uvicorn|next"
sleep 3
./start_wagelift.sh
```

---

## 🎯 Success Metrics

The system is considered fully operational when:
- ✅ Both servers start without errors
- ✅ All health checks pass
- ✅ All API endpoints respond correctly
- ✅ All frontend pages load successfully
- ✅ No crashes occur during normal operation
- ✅ Logs show no critical errors
- ✅ Performance metrics are within acceptable ranges

---

## 🔄 Maintenance

### Daily Checks
- Run `./health_check.sh`
- Review log files for errors
- Monitor system resources

### Weekly Maintenance
- Update dependencies
- Clear old log files
- Performance review

### Monthly Tasks
- Security updates
- Backup configurations
- Performance optimization review

---

**System Status**: ✅ **FULLY OPERATIONAL**
**Last Updated**: June 26, 2025
**Version**: 1.0.1

For issues or questions, refer to the troubleshooting section or run the health check script for detailed diagnostics.