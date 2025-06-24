'use client'

import { useAuth } from '@/hooks/use-auth'

/**
 * Login button component
 */
export function LoginButton() {
  const handleLogin = () => {
    // Redirect to Auth0 login
    window.location.href = '/api/auth/login'
  }

  return (
    <button
      onClick={handleLogin}
      className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200 flex items-center gap-2"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
      </svg>
      Sign In
    </button>
  )
}

/**
 * Logout button component
 */
export function LogoutButton() {
  const handleLogout = () => {
    // Redirect to Auth0 logout
    window.location.href = '/api/auth/logout'
  }

  return (
    <button
      onClick={handleLogout}
      className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200 flex items-center gap-2"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
      </svg>
      Sign Out
    </button>
  )
}

/**
 * Combined auth button that shows login/logout based on auth state
 */
export function AuthButton() {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) {
    return (
      <div className="bg-gray-200 text-gray-400 font-semibold py-2 px-4 rounded-lg flex items-center gap-2">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
        Loading...
      </div>
    )
  }

  if (isAuthenticated && user) {
    return (
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          {user.picture && (
            <img 
              src={user.picture} 
              alt={user.name || 'User'} 
              className="w-8 h-8 rounded-full"
            />
          )}
          <span className="text-sm text-gray-700 font-medium">
            {user.name || user.email}
          </span>
        </div>
        <LogoutButton />
      </div>
    )
  }

  return <LoginButton />
}

/**
 * User profile display component
 */
export function UserProfile() {
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated || !user) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-md">
      <div className="flex items-center gap-4 mb-4">
        {user.picture && (
          <img 
            src={user.picture} 
            alt={user.name || 'User'} 
            className="w-12 h-12 rounded-full"
          />
        )}
        <div>
          <h3 className="font-semibold text-lg">{user.name || 'User'}</h3>
          <p className="text-gray-600 text-sm">{user.email}</p>
        </div>
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Email Verified:</span>
          <span className={user.email_verified ? 'text-green-600' : 'text-red-600'}>
            {user.email_verified ? 'Yes' : 'No'}
          </span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-gray-500">User ID:</span>
          <span className="text-gray-800 font-mono text-xs">{user.sub}</span>
        </div>
        
        {user.updated_at && (
          <div className="flex justify-between">
            <span className="text-gray-500">Last Updated:</span>
            <span className="text-gray-800">
              {new Date(user.updated_at).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>
    </div>
  )
} 