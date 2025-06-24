// Mock Auth Handler for Development
// This provides working auth routes without requiring Auth0 setup

import { NextRequest } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { auth0: string } }
) {
  const { auth0: route } = params
  const { searchParams } = new URL(request.url)
  const returnTo = searchParams.get('returnTo') || '/dashboard/salary'

  switch (route) {
    case 'login':
      // Mock login - redirect to dashboard
      return Response.redirect(new URL(returnTo, request.url), 302)
      
    case 'logout':
      // Mock logout - redirect to home
      return Response.redirect(new URL('/', request.url), 302)
      
    case 'callback':
      // Mock callback - redirect to return URL
      return Response.redirect(new URL(returnTo, request.url), 302)
      
    case 'me':
      // Mock user endpoint
      return new Response(
        JSON.stringify({ 
          user: null, // No user authenticated in mock mode
          message: 'Mock auth - no authentication required for development'
        }),
        { 
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        }
      )
      
    default:
      return new Response(
        JSON.stringify({ 
          error: 'Route not found',
          available: ['login', 'logout', 'callback', 'me']
        }),
        { 
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      )
  }
} 