# Auth0 Integration Setup Guide for WageLift

## Overview

This guide walks through setting up Auth0 authentication for WageLift's Next.js 14 frontend with App Router integration.

## Prerequisites

- Auth0 account (free tier available)
- Node.js 18+ and npm 9+
- Next.js 14.2.25+ (already configured)

## 1. Install Dependencies

**Important**: If you encounter npm permission issues on Windows, run PowerShell as Administrator:

```bash
# From the frontend directory
npm install @auth0/nextjs-auth0 --legacy-peer-deps

# Or if still having issues
npm install @auth0/nextjs-auth0 --force
```

## 2. Create Auth0 Application

1. Go to [Auth0 Dashboard](https://manage.auth0.com/)
2. Click **Applications** → **Create Application**
3. Choose **Regular Web Application**
4. Select **Next.js** as the technology

### Configure Application Settings

**Allowed Callback URLs:**
```
http://localhost:3000/api/auth/callback,https://your-domain.com/api/auth/callback
```

**Allowed Logout URLs:**
```
http://localhost:3000,https://your-domain.com
```

**Allowed Web Origins:**
```
http://localhost:3000,https://your-domain.com
```

## 3. Environment Configuration

Create `.env.local` in the frontend directory (copy from `auth0-config.example.txt`):

```bash
# Required Auth0 Configuration
AUTH0_SECRET='use-openssl-rand-hex-32-to-generate-this'
AUTH0_BASE_URL='http://localhost:3000'
AUTH0_ISSUER_BASE_URL='https://your-domain.auth0.com'
AUTH0_CLIENT_ID='your_client_id_from_auth0_dashboard'
AUTH0_CLIENT_SECRET='your_client_secret_from_auth0_dashboard'

# Optional: API Integration
AUTH0_AUDIENCE='your_api_identifier'
AUTH0_SCOPE='openid profile email'
```

### Generate AUTH0_SECRET

```bash
# macOS/Linux
openssl rand -hex 32

# Windows PowerShell
[System.Web.Security.Membership]::GeneratePassword(32, 0)

# Or use online generator: https://generate-secret.vercel.app/32
```

## 4. Update Code (Post-Installation)

Once `@auth0/nextjs-auth0` is installed, update these files:

### 4.1 Enable Auth Provider (`src/components/auth/auth-provider.tsx`)

```typescript
'use client'

import { UserProvider } from '@auth0/nextjs-auth0/client'
import { ReactNode } from 'react'

interface AuthProviderProps {
  children: ReactNode
}

export default function AuthProvider({ children }: AuthProviderProps) {
  return (
    <UserProvider>
      {children}
    </UserProvider>
  )
}
```

### 4.2 Enable Auth Hook (`src/hooks/use-auth.ts`)

Replace the placeholder with:

```typescript
'use client'

import { useUser } from '@auth0/nextjs-auth0/client'

export function useAuth() {
  const { user, error, isLoading } = useUser()
  
  return {
    user: user as AuthUser | undefined,
    error,
    isLoading,
    isAuthenticated: !!user && !error && !isLoading,
  }
}
```

### 4.3 Enable API Route (`src/app/api/auth/[auth0]/route.ts`)

Replace the placeholder with:

```typescript
import { handleAuth } from '@auth0/nextjs-auth0'

export const GET = handleAuth()
```

## 5. Update Layout

Add the AuthProvider to your root layout (`src/app/layout.tsx`):

```typescript
import AuthProvider from '@/components/auth/auth-provider'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
```

## 6. Usage Examples

### Basic Authentication Status

```typescript
import { useAuth } from '@/hooks/use-auth'
import { AuthButton } from '@/components/auth/login-button'

export default function HomePage() {
  const { isAuthenticated, user, isLoading } = useAuth()

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      <h1>Welcome to WageLift</h1>
      <AuthButton />
      
      {isAuthenticated && user && (
        <p>Hello, {user.name || user.email}!</p>
      )}
    </div>
  )
}
```

### Protected Page

```typescript
import ProtectedRoute from '@/components/auth/protected-route'
import { UserProfile } from '@/components/auth/login-button'

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>
        <h1>Dashboard</h1>
        <UserProfile />
      </div>
    </ProtectedRoute>
  )
}
```

### Page-Level Protection (HOC)

```typescript
import { withAuth } from '@/components/auth/protected-route'

function DashboardPage() {
  return <div>Protected Dashboard Content</div>
}

export default withAuth(DashboardPage)
```

## 7. Middleware Protection (Optional)

Create `middleware.ts` in the root for route-level protection:

```typescript
import { withMiddlewareAuthRequired } from '@auth0/nextjs-auth0/edge'

export default withMiddlewareAuthRequired()

export const config = {
  matcher: ['/dashboard/:path*', '/profile/:path*']
}
```

## 8. Testing Authentication

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Navigate to `http://localhost:3000`

3. Test the login flow:
   - Click the "Sign In" button
   - Complete Auth0 authentication
   - Verify user profile displays
   - Test logout functionality

## 9. API Integration (For FastAPI Backend)

The Auth0 tokens can be sent to your FastAPI backend:

```typescript
// Example API call with Auth0 token
import { getAccessToken } from '@auth0/nextjs-auth0'

export async function fetchProtectedData() {
  const { accessToken } = await getAccessToken()
  
  const response = await fetch('/api/protected-endpoint', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  })
  
  return response.json()
}
```

## 10. Troubleshooting

### Common Issues

1. **npm Installation Errors**:
   - Run PowerShell as Administrator
   - Clear npm cache: `npm cache clean --force`
   - Use `--legacy-peer-deps` or `--force` flags

2. **Environment Variables Not Loading**:
   - Ensure `.env.local` is in the frontend directory
   - Restart the development server
   - Check for typos in variable names

3. **Redirect Loops**:
   - Verify callback URLs in Auth0 dashboard
   - Check AUTH0_BASE_URL matches your domain
   - Ensure AUTH0_SECRET is properly generated

4. **TypeScript Errors**:
   - Verify `@auth0/nextjs-auth0` is installed
   - Check TypeScript configuration
   - Restart your IDE/TypeScript server

### Support Resources

- [Auth0 Next.js SDK Documentation](https://auth0.com/docs/quickstart/webapp/nextjs)
- [Auth0 Community](https://community.auth0.com/)
- [Next.js App Router Documentation](https://nextjs.org/docs/app)

## 11. Security Considerations

- Always use HTTPS in production
- Keep AUTH0_SECRET secure and never commit to version control
- Regularly rotate client secrets
- Enable MFA for Auth0 dashboard access
- Configure proper CORS settings
- Implement rate limiting on auth endpoints

## 12. Production Deployment

1. Update environment variables for production domain
2. Configure Auth0 application settings for production URLs
3. Ensure proper SSL/TLS certificates
4. Set up Auth0 monitoring and logging
5. Configure backup authentication methods

This completes the Auth0 integration setup for WageLift. The implementation follows Auth0 and Next.js best practices for security and performance. 