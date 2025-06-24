'use client'

import { useAuth } from '@/hooks/use-auth'
import { useRouter } from 'next/navigation'
import { useEffect, ReactNode } from 'react'

interface ProtectedRouteProps {
  children: ReactNode
  redirectTo?: string
  showLoading?: boolean
}

/**
 * Protected route wrapper component
 * Redirects unauthenticated users to login page
 */
export default function ProtectedRoute({ 
  children, 
  redirectTo = '/api/auth/login',
  showLoading = true 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        // Redirect to Auth0 login
        window.location.href = redirectTo
      } else if (user && !user.email_verified) {
        // Handle unverified email case
        console.warn('User email not verified:', user.email)
        // Could redirect to verification page here
      }
    }
  }, [isAuthenticated, isLoading, user, redirectTo, router])

  // Show loading state
  if (isLoading) {
    return showLoading ? (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Authenticating...</span>
      </div>
    ) : null
  }

  // Show nothing while redirecting
  if (!isAuthenticated) {
    return showLoading ? (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-pulse text-gray-600">Redirecting to login...</div>
        </div>
      </div>
    ) : null
  }

  // Render protected content
  return <>{children}</>
}

/**
 * Higher-order component for page-level protection
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options?: Omit<ProtectedRouteProps, 'children'>
) {
  return function AuthenticatedComponent(props: P) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    )
  }
} 