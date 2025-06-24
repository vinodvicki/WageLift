# WageLift Supabase Integration Guide

## 🚀 Complete Automatic Setup

Your WageLift application is now fully configured with **automatic Supabase integration** using the JavaScript client pattern you provided:

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://rtmegwnspngsxtixdhat.supabase.co'
const supabaseKey = process.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)
```

## ✅ Integration Status

### Backend (Python/FastAPI)
- ✅ **Supabase Service**: `backend/app/services/supabase_service.py` configured with your credentials
- ✅ **JavaScript Pattern**: Uses exact URL and key pattern you provided
- ✅ **API Endpoints**: All `/supabase/*` endpoints ready
- ✅ **CRUD Operations**: Full user, salary, raise request, CPI, and benchmark data management

### Frontend (Next.js)
- ✅ **Client Configuration**: `frontend/src/lib/supabase/client.ts` configured
- ✅ **TypeScript Types**: Complete database type definitions
- ✅ **React Integration**: Ready for Auth0 + Supabase workflow

### Mobile App (React Native)
- ✅ **API Integration**: `src/lib/api.ts` with Supabase support
- ✅ **Cross-Platform**: Works on iOS and Android
- ✅ **Offline Ready**: Proper error handling and retry logic

## 🗄️ Database Schema Setup

### Option 1: Automatic SQL Setup (Recommended)

1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard
2. **Navigate to**: Your project → SQL Editor
3. **Run the schema**: Copy and paste the contents of `backend/create_supabase_schema.sql`
4. **Execute**: Click "Run" to create all tables automatically

### Option 2: Manual Table Creation

If you prefer manual setup, create these tables in order:

1. **users** - User profiles and Auth0 integration
2. **salary_entries** - User salary history and details  
3. **raise_requests** - AI-generated raise requests
4. **cpi_data** - Inflation data storage
5. **benchmarks** - Salary benchmark data

## 🔧 Environment Configuration

### Backend Environment Variables

Create/update `backend/.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://rtmegwnspngsxtixdhat.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0bWVnd25zcG5nc3h0aXhkaGF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1NTczOTksImV4cCI6MjA2NjEzMzM5OX0.DdZ48QWj-lwyaWmUVW-CbIO-qKVrb6b6MRTdfBYDO3g

# Other existing variables...
OPENAI_API_KEY=your_openai_key
BLS_API_KEY=your_bls_key
# etc...
```

### Frontend Environment Variables

Create/update `frontend/.env.local`:

```bash
# Supabase Configuration  
NEXT_PUBLIC_SUPABASE_URL=https://rtmegwnspngsxtixdhat.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0bWVnd25zcG5nc3h0aXhkaGF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1NTczOTksImV4cCI6MjA2NjEzMzM5OX0.DdZ48QWj-lwyaWmUVW-CbIO-qKVrb6b6MRTdfBYDO3g

# Auth0 Configuration
AUTH0_SECRET=your_auth0_secret
AUTH0_BASE_URL=http://localhost:3000
AUTH0_ISSUER_BASE_URL=https://your-domain.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
```

## 🧪 Testing the Integration

### Run the Complete System Test

```bash
cd backend
python test_complete_system.py
```

Expected output:
```
🚀 WageLift Complete System Test
==================================================
✅ PASS Environment Variables
✅ PASS OpenAI API  
✅ PASS BLS API
✅ PASS CareerOneStop API
✅ PASS Database Connection
✅ PASS AI Letter Generation

Overall: 6/6 tests passed (100.0%)
🎉 ALL SYSTEMS OPERATIONAL!
```

### Test Supabase Specifically

```bash
cd backend
python -c "
import asyncio
import sys
sys.path.insert(0, 'app')

async def test():
    from app.services.supabase_service import supabase_service
    result = await supabase_service.test_connection()
    print('✅ Supabase Connected!' if result else '❌ Connection Failed')

asyncio.run(test())
"
```

## 🚀 Usage Examples

### Backend API Usage

```python
from app.services.supabase_service import supabase_service

# Create user
user_data = {
    "email": "user@example.com",
    "full_name": "John Doe",
    "auth0_id": "auth0|123456"
}
user = await supabase_service.create_user(user_data)

# Create salary entry  
salary_data = {
    "user_id": user["id"],
    "current_salary": 75000.00,
    "job_title": "Software Engineer",
    "location": "San Francisco, CA"
}
salary = await supabase_service.create_salary_entry(salary_data)
```

### Frontend Usage

```typescript
import { supabase } from '@/lib/supabase/client'

// Get user data
const getUser = async (email: string) => {
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('email', email)
    .single()
  
  return { data, error }
}
```

### Mobile App Usage

```typescript
import { api } from '@/lib/api'

// Calculate CPI gap
const cpiResult = await api.calculateCPIGap(formData)

// Get salary benchmarks
const benchmarks = await api.getBenchmarkData(jobTitle, location)
```

## 🔄 Data Flow

1. **User Authentication**: Auth0 → Frontend/Mobile
2. **User Management**: Frontend/Mobile → Backend → Supabase
3. **Salary Data**: User Input → Backend Processing → Supabase Storage
4. **CPI Calculation**: BLS API → Backend → Supabase Cache
5. **Benchmarks**: CareerOneStop API → Backend → Supabase Cache
6. **AI Letters**: OpenAI API → Backend → Supabase Storage

## 🛡️ Security Features

- ✅ **Row Level Security (RLS)**: Users can only access their own data
- ✅ **API Key Protection**: Environment variables for sensitive keys
- ✅ **Auth0 Integration**: Secure user authentication
- ✅ **HTTPS Only**: All connections encrypted
- ✅ **Input Validation**: Server-side data validation

## 📊 Database Schema Overview

### Core Tables
- **users**: User profiles and Auth0 mapping
- **salary_entries**: Historical salary data per user
- **raise_requests**: Generated raise requests with AI content
- **cpi_data**: Cached inflation data from BLS
- **benchmarks**: Cached salary benchmarks from CareerOneStop

### Relationships
- Users → Salary Entries (1:many)
- Users → Raise Requests (1:many) 
- Salary Entries → Raise Requests (1:many)

## 🎯 Next Steps

1. **Run the SQL schema** in your Supabase dashboard
2. **Test the connection** using the provided test commands
3. **Start your applications**:
   ```bash
   # Backend
   cd backend && uvicorn app.main:app --reload
   
   # Frontend  
   cd frontend && npm run dev
   
   # Mobile (if needed)
   cd ../src && npx expo start
   ```

## 🆘 Troubleshooting

### Common Issues

**Connection Failed**: 
- Verify your Supabase URL and key in environment variables
- Check that tables exist in your Supabase dashboard

**Permission Denied**:
- Ensure RLS policies are properly configured
- Verify Auth0 integration is working

**API Errors**:
- Check that all required environment variables are set
- Verify API keys are valid and have proper permissions

### Support

If you encounter issues:
1. Check the logs in `backend/logs/`
2. Verify environment variables are loaded
3. Test individual components using the provided test scripts
4. Check Supabase dashboard for table structure and data

---

## ✨ Summary

Your WageLift application now has **complete Supabase integration** with:

- ✅ **Automatic JavaScript client pattern** matching your specification
- ✅ **Full CRUD operations** for all data types
- ✅ **Cross-platform support** (Web + Mobile)
- ✅ **Production-ready security** with RLS and Auth0
- ✅ **Comprehensive testing** and validation
- ✅ **Easy deployment** with environment-based configuration

**You're ready to go! 🚀** 