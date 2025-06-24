import { useUser } from '@auth0/nextjs-auth0/client'
import { useEffect, useState } from 'react'
import { createSupabaseClientWithAuth } from './client'
import type { 
  Database,
  UserRow,
  UserProfileRow,
  SalaryEntryRow,
  RaiseRequestRow 
} from './types'

type SupabaseClient = ReturnType<typeof createSupabaseClientWithAuth>

// Hook to get authenticated Supabase client
export const useSupabaseAuth = () => {
  const { user, isLoading } = useUser()
  const [supabaseClient, setSupabaseClient] = useState<SupabaseClient | null>(null)

  useEffect(() => {
    if (user && !isLoading) {
      // Get the Auth0 access token and create authenticated client
      fetch('/api/auth/token')
        .then(res => res.json())
        .then(data => {
          if (data.accessToken) {
            setSupabaseClient(createSupabaseClientWithAuth(data.accessToken))
          }
        })
        .catch(error => {
          console.error('Failed to get access token:', error)
        })
    } else {
      setSupabaseClient(null)
    }
  }, [user, isLoading])

  return {
    supabase: supabaseClient,
    user,
    isLoading: isLoading || !supabaseClient,
    isAuthenticated: !!user && !!supabaseClient
  }
}

// Hook to manage user profile data
export const useUserProfile = () => {
  const { supabase, user, isLoading } = useSupabaseAuth()
  const [profile, setProfile] = useState<UserRow | null>(null)
  const [userProfile, setUserProfile] = useState<UserProfileRow | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (supabase && user) {
      fetchUserProfile()
    }
  }, [supabase, user])

  const fetchUserProfile = async () => {
    if (!supabase || !user) return

    setLoading(true)
    setError(null)

    try {
      // Fetch main user record
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('*')
        .eq('auth0_id', user.sub)
        .single()

      if (userError && userError.code !== 'PGRST116') {
        throw userError
      }

      if (!userData) {
        // Create user record if it doesn't exist
        const newUser = {
          auth0_id: user.sub!,
          email: user.email!,
          full_name: user.name || null,
          profile_picture_url: user.picture || null,
          last_login: new Date().toISOString()
        }

        const { data: createdUser, error: createError } = await supabase
          .from('users')
          .insert(newUser)
          .select()
          .single()

        if (createError) throw createError
        setProfile(createdUser)
      } else {
        // Update last login
        const { data: updatedUser, error: updateError } = await supabase
          .from('users')
          .update({ last_login: new Date().toISOString() })
          .eq('id', userData.id)
          .select()
          .single()

        if (updateError) throw updateError
        setProfile(updatedUser)
      }

      // Fetch user profile extension
      const { data: profileData, error: profileError } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', profile?.id || userData?.id)
        .single()

      if (profileError && profileError.code !== 'PGRST116') {
        throw profileError
      }

      setUserProfile(profileData || null)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (updates: Partial<UserProfileRow>) => {
    if (!supabase || !profile) return

    try {
      setError(null)
      
      if (userProfile) {
        // Update existing profile
        const { data, error } = await supabase
          .from('user_profiles')
          .update(updates)
          .eq('user_id', profile.id)
          .select()
          .single()

        if (error) throw error
        setUserProfile(data)
      } else {
        // Create new profile
        const { data, error } = await supabase
          .from('user_profiles')
          .insert({ user_id: profile.id, ...updates })
          .select()
          .single()

        if (error) throw error
        setUserProfile(data)
      }
    } catch (err: any) {
      setError(err.message)
      throw err
    }
  }

  return {
    profile,
    userProfile,
    loading: loading || isLoading,
    error,
    updateProfile,
    refetch: fetchUserProfile
  }
}

// Hook to manage salary entries
export const useSalaryEntries = () => {
  const { supabase, user } = useSupabaseAuth()
  const [entries, setEntries] = useState<SalaryEntryRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (supabase && user) {
      fetchSalaryEntries()
    }
  }, [supabase, user])

  const fetchSalaryEntries = async () => {
    if (!supabase || !user) return

    setLoading(true)
    setError(null)

    try {
      const { data, error } = await supabase
        .from('salary_entries')
        .select('*')
        .eq('user_id', user.sub)
        .order('effective_date', { ascending: false })

      if (error) throw error
      setEntries(data || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const addSalaryEntry = async (entry: Omit<SalaryEntryRow, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => {
    if (!supabase || !user) return

    try {
      setError(null)
      
      const { data, error } = await supabase
        .from('salary_entries')
        .insert({
          ...entry,
          user_id: user.sub!
        })
        .select()
        .single()

      if (error) throw error
      
      setEntries(prev => [data, ...prev])
      return data
    } catch (err: any) {
      setError(err.message)
      throw err
    }
  }

  return {
    entries,
    loading,
    error,
    addSalaryEntry,
    refetch: fetchSalaryEntries
  }
}

// Hook to manage raise requests
export const useRaiseRequests = () => {
  const { supabase, user } = useSupabaseAuth()
  const [requests, setRequests] = useState<RaiseRequestRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (supabase && user) {
      fetchRaiseRequests()
    }
  }, [supabase, user])

  const fetchRaiseRequests = async () => {
    if (!supabase || !user) return

    setLoading(true)
    setError(null)

    try {
      const { data, error } = await supabase
        .from('raise_requests')
        .select('*')
        .eq('user_id', user.sub)
        .order('created_at', { ascending: false })

      if (error) throw error
      setRequests(data || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const createRaiseRequest = async (request: Omit<RaiseRequestRow, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => {
    if (!supabase || !user) return

    try {
      setError(null)
      
      const { data, error } = await supabase
        .from('raise_requests')
        .insert({
          ...request,
          user_id: user.sub!
        })
        .select()
        .single()

      if (error) throw error
      
      setRequests(prev => [data, ...prev])
      return data
    } catch (err: any) {
      setError(err.message)
      throw err
    }
  }

  return {
    requests,
    loading,
    error,
    createRaiseRequest,
    refetch: fetchRaiseRequests
  }
} 