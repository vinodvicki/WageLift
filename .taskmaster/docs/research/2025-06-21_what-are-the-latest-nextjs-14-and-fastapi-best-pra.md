---
title: Research Session
query: "What are the latest Next.js 14 and FastAPI best practices for 2024? Include TypeScript setup, project structure, performance optimization, and security considerations."
date: 6/21/2025
time: 5:48:32 AM
timestamp: 2025-06-21T10:48:32.190Z
exchanges: 1
---

# Research Session

## Initial Query

**Question:** What are the latest Next.js 14 and FastAPI best practices for 2024? Include TypeScript setup, project structure, performance optimization, and security considerations.

**Response:**

# Next.js 14 and FastAPI Best Practices for 2024

## TypeScript Setup

### Next.js TypeScript Configuration
1. **Strict Mode**: Enable all strict type checking options in `tsconfig.json`:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "noImplicitThis": true,
    "alwaysStrict": true
  }
}
```

2. **App Router Types**: For Next.js 14's App Router, create custom types for route handlers:
```typescript
// types/next.d.ts
import { NextRequest } from 'next/server'

declare module 'next/server' {
  interface NextRequest {
    user?: {
      id: string
      email: string
    }
  }
}
```

3. **Component Props**: Use generics for reusable components:
```typescript
type TableProps<T> = {
  data: T[]
  renderRow: (item: T) => React.ReactNode
}

function Table<T>({ data, renderRow }: TableProps<T>) {
  return <div>{data.map(renderRow)}</div>
}
```

### FastAPI TypeScript Integration
1. **Pydantic v2 Models**: Use Pydantic v2 with strict typing:
```python
from pydantic import BaseModel, Field

class SalaryEntry(BaseModel):
    user_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    currency: str = Field("USD", pattern="^[A-Z]{3}$")
```

2. **Type Hints for Routes**:
```python
from fastapi import FastAPI
from typing import Annotated
from fastapi.params import Depends

app = FastAPI()

async def get_current_user(token: str) -> User:
    ...

@app.get("/salaries/")
async def read_salaries(user: Annotated[User, Depends(get_current_user)]) -> list[SalaryEntry]:
    return []
```

## Project Structure

### Next.js 14 Structure
```
/app
  /(auth)
    /login
      page.tsx
  /dashboard
    /salaries
      page.tsx
      components/
        SalaryTable.tsx
  /api
    /salaries
      route.ts
/lib
  /db
    client.ts
  /auth
    providers.ts
/types
  index.ts
```

### FastAPI Structure
```
/app
  /api
    /v1
      /endpoints
        salaries.py
        auth.py
      __init__.py
  /core
    config.py
    security.py
  /models
    schemas.py
    database.py
  /services
    salary_service.py
    auth_service.py
  main.py
```

## Performance Optimization

### Next.js Optimizations
1. **Server Actions**: Use for form handling (reduces client-side JS):
```typescript
// app/actions.ts
'use server'

export async function createSalaryEntry(formData: FormData) {
  const amount = formData.get('amount')
  // Validate and save to DB
}
```

2. **Dynamic Imports**: For heavy components:
```typescript
const SalaryChart = dynamic(() => import('@/components/SalaryChart'), {
  ssr: false,
  loading: () => <Skeleton />
})
```

3. **Image Optimization**:
```typescript
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="Logo"
  width={500}
  height={500}
  priority
  quality={80}
/>
```

### FastAPI Optimizations
1. **Response Caching**:
```python
from fastapi_cache.decorator import cache

@app.get("/cpi/")
@cache(expire=60*60*24)  # Cache for 24 hours
async def get_cpi_data():
    return await fetch_cpi_data()
```

2. **Background Tasks**:
```python
from fastapi import BackgroundTasks

def update_cpi_cache():
    # Fetch and update CPI data

@app.get("/refresh-cpi/")
async def refresh_cpi(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_cpi_cache)
    return {"message": "CPI update initiated"}
```

3. **Database Connection Pooling**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=10,
    pool_timeout=30
)
```

## Security Considerations

### Next.js Security
1. **CSP Headers**: Configure in `next.config.js`:
```javascript
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-inline'"
  }
]

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ]
  }
}
```

2. **Auth Protection**: Use middleware for route protection:
```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  if (!request.cookies.has('auth_token')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}
```

3. **API Route Validation**:
```typescript
// app/api/salaries/route.ts
import { NextResponse } from 'next/server'
import { z } from 'zod'

const schema = z.object({
  amount: z.number().positive()
})

export async function POST(req: Request) {
  try {
    const body = await req.json()
    const data = schema.parse(body)
    // Process data
  } catch (err) {
    return NextResponse.json({ error: 'Invalid data' }, { status: 400 })
  }
}
```

### FastAPI Security
1. **Dependency Injection for Auth**:
```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await authenticate_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
```

2. **Rate Limiting**:
```python
from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(middleware=[Middleware(limiter)])

@app.get("/cpi/")
@limiter.limit("5/minute")
async def get_cpi(request: Request):
    return {"data": cpi_data}
```

3. **Input Validation**:
```python
from pydantic import BaseModel, validator

class RaiseRequest(BaseModel):
    amount: float
    justification: str

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)
```

## Database Integration (Relevant to Task 3)

### Next.js with Supabase
```typescript
// lib/db/client.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseKey)
```

### FastAPI with Async PostgreSQL
```python
# app/models/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## Cron Job Implementation (Relevant to Task 4)

```python
# app/services/cpi_service.py
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.models.database import get_db

async def fetch_cpi_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.bls.gov/publicAPI/v2/timeseries/data/CUSR0000SA0",
            params={"startyear": "2020", "endyear": "2024"}
        )
        return response.json()

async def update_cpi_in_db():
    data = await fetch_cpi_data()
    async with get_db() as session:
        # Store data in PostgreSQL
        await session.execute(
            "INSERT INTO cpi_data (date, value) VALUES (:date, :value)",
            {"date": data["date"], "value": data["value"]}
        )
        await session.commit()

def setup_cron():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_cpi_in_db, 'cron', month='1-12', day='1')
    scheduler.start()
```

## PDF Generation (Relevant to Task 13)

### Next.js + PDF-Lib
```typescript
// app/api/generate-pdf/route.ts
import { PDFDocument, StandardFonts } from 'pdf-lib'

export async function POST(request: Request) {
  const { content } = await request.json()
  
  const pdfDoc = await PDFDocument.create()
  const page = pdfDoc.addPage()
  const font = await pdfDoc.embedFont(StandardFonts.Helvetica)
  
  page.drawText(content, {
    x: 50,
    y: 500,
    size: 12,
    font
  })
  
  const pdfBytes = await pdfDoc.save()
  return new Response(pdfBytes, {
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': 'attachment; filename="raise_request.pdf"'
    }
  })
}
```

## Mobile Considerations (Relevant to Task 14)

### Shared Components Strategy
1. **Core Component Library**:
```
/shared
  /components
    Button.tsx
    Card.tsx
    Typography.tsx
  /hooks
    useAuth.ts
    useApi.ts
```

2. **React Native Adaptation**:
```typescript
// shared/components/Button.tsx
import { Platform } from 'react-native'
import { Button as RNButton } from 'react-native'
import { Button as WebButton } from '@radix-ui/react-button'

export const Button = Platform.select({
  native: RNButton,
  web: WebButton
})
```

3. **API Client Abstraction**:
```typescript
// shared/lib/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const fetchSalaries = async (userId: string) => {
  return api.get(`/salaries/${userId}`)
}
```


---

*Generated by Task Master Research Command*  
*Timestamp: 2025-06-21T10:48:32.190Z*
