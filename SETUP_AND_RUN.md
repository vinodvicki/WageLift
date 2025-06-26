# WageLift Application Setup & Run Guide

This guide provides step-by-step instructions to get the WageLift application running with all Phase 1 and Phase 2 features.

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11 (for backend) 
- PostgreSQL or Supabase account
- Redis (optional, for caching)
- API keys for various services

## Quick Start (Development)

### 1. Clone and Setup Environment Files

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd WageLift

# Frontend environment setup
cd frontend
cp .env.example .env.local
# Edit .env.local and add your API keys

# Backend environment setup
cd ../backend
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run build  # Verify build works
npm run dev    # Start development server on port 3000
```

Frontend should now be accessible at: http://localhost:3000

### 3. Backend Setup (Option A: Using Python 3.11)

```bash
cd backend

# Install Python 3.11 if not available
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --port 8001
```

### 3. Backend Setup (Option B: Using Docker)

```bash
cd backend

# Build the Docker image
docker build -t wagelift-backend .

# Run the container
docker run -p 8001:8000 \
  --env-file .env \
  -v $(pwd):/app \
  wagelift-backend
```

## Required API Keys

### Frontend (.env.local)
- `AUTH0_*` - Auth0 credentials for authentication
- `NEXT_PUBLIC_SUPABASE_*` - Supabase project credentials

### Backend (.env)
- `OPENAI_API_KEY` - For AI-powered letter generation
- `BLS_API_KEY` - For CPI data from Bureau of Labor Statistics
- `CAREERONESTOP_*` - For salary benchmarking data
- `SUPABASE_*` - Database credentials
- `AUTH0_*` - Authentication configuration

## Database Setup

### Using Supabase (Recommended)

1. Create a Supabase project at https://supabase.com
2. Get your project URL and keys
3. Run the migrations:

```bash
cd backend
python run_migration.py
```

### Using Local PostgreSQL

1. Create a database:
```sql
CREATE DATABASE wagelift;
```

2. Update DATABASE_URL in backend/.env
3. Run migrations as shown above

## Verify Setup

### Frontend Health Check
```bash
curl http://localhost:3000/api/auth/token
# Should return authentication-related response
```

### Backend Health Check
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy","timestamp":"..."}
```

### Test Core Features

1. **CPI Calculation**: Visit http://localhost:3000/dashboard/salary
2. **AI Letter Generation**: Visit http://localhost:3000/dashboard/raise-letter
3. **Phase 2 Features**: Visit http://localhost:3000/dashboard/phase2

## Common Issues & Solutions

### Frontend Build Errors
- **Missing modules**: Run `npm install` again
- **Type errors**: Run `npm run type-check` to identify issues
- **Environment variables**: Ensure all NEXT_PUBLIC_* variables are set

### Backend Import Errors
- **Python version**: Must use Python 3.11 (not 3.12 or 3.13)
- **Missing system packages**: Install `libpq-dev` for PostgreSQL support
- **Redis connection**: Redis is optional; disable in config if not using

### API Connection Errors
- **CORS issues**: Ensure backend allows frontend origin
- **Port conflicts**: Change ports in package.json and main.py if needed
- **SSL/HTTPS**: Use proper certificates in production

## Production Deployment

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy the .next folder
```

### Backend (AWS/GCP/Heroku)
```bash
# Use the production Dockerfile
docker build -t wagelift-backend:prod .
# Deploy to your cloud provider
```

## Feature Verification Checklist

### Phase 1 Features
- [ ] Landing page loads correctly
- [ ] Salary form submits and calculates CPI
- [ ] Results page shows inflation-adjusted salary
- [ ] Benchmark data displays correctly

### Phase 2 Features  
- [ ] AI letter generation works
- [ ] Manager profiler loads communication styles
- [ ] Readiness score calculates properly
- [ ] Email functionality (if configured)

## Support

If you encounter issues:

1. Check the error logs in browser console (F12)
2. Check backend logs in terminal
3. Verify all environment variables are set
4. Ensure all services (database, Redis) are running
5. Review the error analysis report: WAGELIFT_ERROR_ANALYSIS_REPORT.md

## Next Steps

Once running successfully:

1. Configure real API keys for production use
2. Set up proper authentication with Auth0
3. Configure email service for letter delivery
4. Enable Redis for better performance
5. Set up monitoring and logging

Happy coding! 🚀