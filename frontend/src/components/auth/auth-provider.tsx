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