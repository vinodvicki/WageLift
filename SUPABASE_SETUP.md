# WageLift Supabase Integration Setup Guide

This guide will walk you through setting up Supabase for WageLift with Auth0 JWT integration and Row-Level Security.

## 🎯 Overview

WageLift uses Supabase as the primary database with:
- **Auth0 JWT Integration** - Users authenticated via Auth0 with JWT tokens
- **Row-Level Security** - Database-level security based on JWT claims
- **TypeScript Type Safety** - Auto-generated types for the database schema
- **Real-time Subscriptions** - Live updates for user data changes
- **Comprehensive API** - FastAPI backend with Supabase service integration

---

## 📋 Prerequisites

- Supabase account ([supabase.com](https://supabase.com))
- Auth0 account (from previous setup)
- Node.js 18+ and Python 3.11+

---

## 🚀 Phase 1: Supabase Project Setup

### 1.1 Create Supabase Project

1. **Go to [Supabase Dashboard](https://app.supabase.com)**
2. **Click "New Project"**
3. **Configure your project:**
   ```
   Organization: [Your Organization]
   Name: wagelift-production (or wagelift-dev for development)
   Database Password: [Generate a strong password - save this!]
   Region: [Choose closest to your users]
   ```

### 1.2 Get Project Credentials

After project creation, go to **Settings > API** and copy:

```bash
# Required Environment Variables
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1.3 Add to Environment Files

**Frontend (.env.local):**
```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Auth0 Configuration (from previous setup)
AUTH0_SECRET=your-auth0-secret
AUTH0_BASE_URL=http://localhost:3000
AUTH0_ISSUER_BASE_URL=https://your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=https://wagelift.api
```

**Backend (.env):**
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Existing Auth0 and other configs...
```

---

## 🗄️ Phase 2: Database Schema Setup

### 2.1 Run the Schema Script

1. **Go to Supabase Dashboard > SQL Editor**
2. **Create a new query**
3. **Copy and paste the entire contents of `backend/supabase-schema.sql`**
4. **Click "Run" to execute the schema**

This creates:
- ✅ All tables with proper relationships
- ✅ Row-Level Security policies
- ✅ Indexes for performance
- ✅ Triggers for automatic timestamps
- ✅ Sample benchmark data

### 2.2 Verify Schema Creation

Run this verification query in SQL Editor:
```sql
-- Verify tables exist
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('users', 'user_profiles', 'salary_entries', 'benchmarks', 'raise_requests');

-- Verify RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND rowsecurity = true;

-- Check sample data
SELECT COUNT(*) as benchmark_count FROM public.benchmarks;
```

Expected results:
- 5 tables created with `table_type = 'BASE TABLE'`
- 5 tables with `rowsecurity = true`
- 5 benchmark records

---

## 🔐 Phase 3: Auth0 Integration

### 3.1 Configure Auth0 for Supabase

In your **Auth0 Dashboard > Rules**, add this rule to include user info in JWT:

```javascript
function addSupabaseUserInfo(user, context, callback) {
  const namespace = 'https://wagelift.app/';
  
  context.accessToken[namespace + 'user_metadata'] = {
    user_id: user.user_id,
    email: user.email,
    name: user.name,
    picture: user.picture,
    email_verified: user.email_verified
  };
  
  // Add custom claims for Supabase
  context.accessToken.sub = user.user_id;
  context.accessToken.email = user.email;
  context.accessToken.name = user.name;
  context.accessToken.picture = user.picture;
  
  callback(null, user, context);
}
```

### 3.2 Test JWT Structure

In Supabase SQL Editor, test JWT parsing:
```sql
-- Test accessing JWT claims (run when authenticated)
SELECT 
  auth.jwt() ->> 'sub' as user_sub,
  auth.jwt() ->> 'email' as user_email,
  auth.jwt() ->> 'name' as user_name;
```

---

## 🔧 Phase 4: Application Integration

### 4.1 Install Frontend Dependencies

```bash
cd frontend
npm install @supabase/supabase-js@2.39.7 @supabase/auth-helpers-nextjs@0.10.0
```

### 4.2 Install Backend Dependencies

```bash
cd backend
pip install httpx  # For Supabase API calls
```

### 4.3 Generate TypeScript Types (Optional)

Install Supabase CLI and generate types:
```bash
npm install -g supabase
supabase login
supabase gen types typescript --project-id your-project-id > frontend/src/lib/supabase/database.types.ts
```

---

## 🧪 Phase 5: Testing the Integration

### 5.1 Test Backend API

Create a test script:
```bash
# backend/scripts/test_supabase.py
```

```python
import asyncio
import os
from app.services.supabase_service import supabase_service

async def test_supabase():
    # Test health check
    health = await supabase_service.health_check()
    print(f"Health Check: {health}")
    
    # Test benchmark data
    benchmarks = await supabase_service.get_benchmarks(job_title="Software Engineer")
    print(f"Found {len(benchmarks)} benchmarks")

if __name__ == "__main__":
    asyncio.run(test_supabase())
```

Run the test:
```bash
cd backend
python scripts/test_supabase.py
```

### 5.2 Test Frontend Integration

Create a test page:
```typescript
// frontend/src/app/test-supabase/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { useSupabaseAuth } from '@/lib/supabase/hooks'

export default function TestSupabase() {
  const { supabase, user, isLoading } = useSupabaseAuth()
  const [testResults, setTestResults] = useState<any>(null)

  useEffect(() => {
    if (supabase && user) {
      testConnection()
    }
  }, [supabase, user])

  const testConnection = async () => {
    try {
      const { data, error } = await supabase!
        .from('benchmarks')
        .select('*')
        .limit(3)

      setTestResults({ data, error })
    } catch (err) {
      setTestResults({ error: err })
    }
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="p-6">
      <h1>Supabase Test Page</h1>
      <div className="mt-4">
        <h2>User Status:</h2>
        <pre>{JSON.stringify({ user: !!user, supabase: !!supabase }, null, 2)}</pre>
      </div>
      
      <div className="mt-4">
        <h2>Supabase Test Results:</h2>
        <pre>{JSON.stringify(testResults, null, 2)}</pre>
      </div>
    </div>
  )
}
```

### 5.3 Test Protected API Endpoints

```bash
# Test auth-protected endpoints
curl -H "Authorization: Bearer YOUR_AUTH0_JWT" \
     http://localhost:8000/api/v1/supabase/user/profile

curl -H "Authorization: Bearer YOUR_AUTH0_JWT" \
     http://localhost:8000/api/v1/supabase/benchmarks
```

---

## 📊 Phase 6: Monitoring and Performance

### 6.1 Enable Database Monitoring

In Supabase Dashboard:
1. **Go to Settings > Database**
2. **Enable Statement Timeout: 8 seconds**
3. **Enable Log Statements: all**

### 6.2 Set Up Performance Monitoring

```sql
-- Monitor query performance
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
```

### 6.3 Monitor RLS Policy Performance

```sql
-- Check RLS policy usage
SELECT 
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual
FROM pg_policies 
WHERE schemaname = 'public';
```

---

## 🚨 Troubleshooting

### Issue: "JWT not found" errors
**Solution:** Ensure Auth0 is configured to include JWT claims and the user is properly authenticated.

### Issue: RLS blocking all queries
**Solution:** Verify JWT structure and RLS policy conditions:
```sql
-- Debug JWT structure
SELECT auth.jwt();

-- Temporarily disable RLS for testing (BE CAREFUL!)
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
-- Remember to re-enable: ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
```

### Issue: Type errors in frontend
**Solution:** Regenerate TypeScript types or check import paths in `frontend/src/lib/supabase/types.ts`.

### Issue: CORS errors
**Solution:** Verify CORS settings in Supabase Dashboard > Authentication > Settings.

---

## 🎉 Success Checklist

- [ ] Supabase project created and configured
- [ ] Database schema deployed successfully
- [ ] Environment variables configured
- [ ] Auth0 JWT integration working
- [ ] Frontend can connect to Supabase
- [ ] Backend API endpoints functional
- [ ] RLS policies protecting user data
- [ ] Sample data visible and accessible

---

## 🔄 Next Steps

After successful setup:

1. **Complete Auth0 configuration** with real credentials
2. **Test end-to-end user flows** (signup, login, data creation)
3. **Deploy to staging environment**
4. **Set up monitoring and alerting**
5. **Begin implementing core application features**

---

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Auth0 + Supabase Integration Guide](https://supabase.com/docs/guides/auth/auth0)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [TypeScript Types Generation](https://supabase.com/docs/reference/cli/usage#supabase-gen)

---

*This setup guide is part of the WageLift Supabase integration. For support, refer to the project documentation or contact the development team.* 