// TypeScript types for Supabase Database Schema
// This file will be auto-generated once we connect to Supabase
// For now, we'll define the core types based on our WageLift requirements

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          auth0_id: string
          email: string
          full_name: string | null
          profile_picture_url: string | null
          created_at: string
          updated_at: string
          last_login: string | null
        }
        Insert: {
          id?: string
          auth0_id: string
          email: string
          full_name?: string | null
          profile_picture_url?: string | null
          created_at?: string
          updated_at?: string
          last_login?: string | null
        }
        Update: {
          id?: string
          auth0_id?: string
          email?: string
          full_name?: string | null
          profile_picture_url?: string | null
          created_at?: string
          updated_at?: string
          last_login?: string | null
        }
      }
      user_profiles: {
        Row: {
          user_id: string
          job_title: string | null
          industry: string | null
          years_experience: number | null
          education_level: string | null
          location_postal_code: string | null
          is_public: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          user_id: string
          job_title?: string | null
          industry?: string | null
          years_experience?: number | null
          education_level?: string | null
          location_postal_code?: string | null
          is_public?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          user_id?: string
          job_title?: string | null
          industry?: string | null
          years_experience?: number | null
          education_level?: string | null
          location_postal_code?: string | null
          is_public?: boolean
          created_at?: string
          updated_at?: string
        }
      }
      salary_entries: {
        Row: {
          id: string
          user_id: string
          base_salary: number
          bonus_amount: number
          currency: string
          effective_date: string
          payment_frequency: string
          is_current: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          base_salary: number
          bonus_amount?: number
          currency?: string
          effective_date: string
          payment_frequency: string
          is_current?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          base_salary?: number
          bonus_amount?: number
          currency?: string
          effective_date?: string
          payment_frequency?: string
          is_current?: boolean
          created_at?: string
          updated_at?: string
        }
      }
      benchmarks: {
        Row: {
          id: string
          job_title: string
          industry: string
          location: string
          min_salary: number
          max_salary: number
          median_salary: number
          currency: string
          data_source: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          job_title: string
          industry: string
          location: string
          min_salary: number
          max_salary: number
          median_salary: number
          currency?: string
          data_source: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          job_title?: string
          industry?: string
          location?: string
          min_salary?: number
          max_salary?: number
          median_salary?: number
          currency?: string
          data_source?: string
          created_at?: string
          updated_at?: string
        }
      }
      raise_requests: {
        Row: {
          id: string
          user_id: string
          current_salary: number
          requested_salary: number
          justification: string
          status: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          current_salary: number
          requested_salary: number
          justification: string
          status?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          current_salary?: number
          requested_salary?: number
          justification?: string
          status?: string
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      payment_frequency: 'hourly' | 'weekly' | 'biweekly' | 'monthly' | 'annually'
      raise_request_status: 'draft' | 'submitted' | 'approved' | 'rejected'
      education_level: 'high_school' | 'associates' | 'bachelors' | 'masters' | 'phd'
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

// Helper types for easier usage
export type UserRow = Database['public']['Tables']['users']['Row']
export type UserInsert = Database['public']['Tables']['users']['Insert']
export type UserUpdate = Database['public']['Tables']['users']['Update']

export type UserProfileRow = Database['public']['Tables']['user_profiles']['Row']
export type UserProfileInsert = Database['public']['Tables']['user_profiles']['Insert']
export type UserProfileUpdate = Database['public']['Tables']['user_profiles']['Update']

export type SalaryEntryRow = Database['public']['Tables']['salary_entries']['Row']
export type SalaryEntryInsert = Database['public']['Tables']['salary_entries']['Insert']
export type SalaryEntryUpdate = Database['public']['Tables']['salary_entries']['Update']

export type BenchmarkRow = Database['public']['Tables']['benchmarks']['Row']
export type BenchmarkInsert = Database['public']['Tables']['benchmarks']['Insert']
export type BenchmarkUpdate = Database['public']['Tables']['benchmarks']['Update']

export type RaiseRequestRow = Database['public']['Tables']['raise_requests']['Row']
export type RaiseRequestInsert = Database['public']['Tables']['raise_requests']['Insert']
export type RaiseRequestUpdate = Database['public']['Tables']['raise_requests']['Update']

// Enums
export type PaymentFrequency = Database['public']['Enums']['payment_frequency']
export type RaiseRequestStatus = Database['public']['Enums']['raise_request_status']
export type EducationLevel = Database['public']['Enums']['education_level'] 