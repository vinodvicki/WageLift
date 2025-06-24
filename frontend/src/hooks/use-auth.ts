'use client'

// Import will be available once @auth0/nextjs-auth0 is properly installed
// import { useUser } from '@auth0/nextjs-auth0/client'

/**
 * Enhanced Auth0 user type with required properties
 */
export interface AuthUser {
  sub: string           // Auth0 user ID
  email: string
  email_verified: boolean
  name?: string
  picture?: string
  nickname?: string
  updated_at?: string
}

/**
 * Auth hook return type
 */
interface UseAuthReturn {
  user: AuthUser | undefined
  error: Error | undefined
  isLoading: boolean
  isAuthenticated: boolean
  getAccessToken: () => Promise<string>
}

/**
 * Type-safe Auth0 hook for WageLift
 * Provides user authentication state and type safety
 */
export function useAuth(): UseAuthReturn {
  // Temporary implementation until Auth0 package is installed
  // const { user, error, isLoading } = useUser()
  
  // Placeholder for development - remove when Auth0 is properly installed
  const user = undefined
  const error = undefined
  const isLoading = false
  
  const getAccessToken = async (): Promise<string> => {
    // Placeholder implementation - replace with actual Auth0 token fetch
    return 'mock-token-for-development'
  }

  return {
    user: user as AuthUser | undefined,
    error,
    isLoading,
    isAuthenticated: !!user && !error && !isLoading,
    getAccessToken,
  }
}

/**
 * Helper function to get user ID safely
 */
export function getUserId(user: AuthUser | undefined): string | null {
  return user?.sub || null
}

/**
 * Helper function to check if user email is verified
 */
export function isEmailVerified(user: AuthUser | undefined): boolean {
  return user?.email_verified || false
} 