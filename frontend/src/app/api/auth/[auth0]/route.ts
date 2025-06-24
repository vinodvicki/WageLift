// Auth0 Dynamic Route Handler for Next.js App Router
// This file will be functional once @auth0/nextjs-auth0 is properly installed

// import { handleAuth } from '@auth0/nextjs-auth0'

// export const GET = handleAuth()

// Temporary placeholder - remove when Auth0 package is installed
export async function GET() {
  return new Response(
    JSON.stringify({ 
      error: 'Auth0 not configured', 
      message: 'Please install @auth0/nextjs-auth0 and configure environment variables' 
    }),
    { 
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    }
  )
} 