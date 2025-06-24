import { createClient } from '@supabase/supabase-js'

// Your exact JavaScript pattern implementation
const supabaseUrl = 'https://rtmegwnspngsxtixdhat.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0bWVnd25zcG5nc3h0aXhkaGF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1NTczOTksImV4cCI6MjA2NjEzMzM5OX0.DdZ48QWj-lwyaWmUVW-CbIO-qKVrb6b6MRTdfBYDO3g'
const supabase = createClient(supabaseUrl, supabaseKey)

export { supabase }

// Database type definitions for TypeScript
export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          auth0_id: string | null
          email: string
          full_name: string | null
          profile_picture_url: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          auth0_id?: string | null
          email: string
          full_name?: string | null
          profile_picture_url?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          auth0_id?: string | null
          email?: string
          full_name?: string | null
          profile_picture_url?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      salary_entries: {
        Row: {
          id: string
          user_id: string
          current_salary: number
          job_title: string
          company: string | null
          location: string | null
          years_experience: number | null
          education_level: string | null
          industry: string | null
          employment_type: string
          benefits_value: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          current_salary: number
          job_title: string
          company?: string | null
          location?: string | null
          years_experience?: number | null
          education_level?: string | null
          industry?: string | null
          employment_type?: string
          benefits_value?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          current_salary?: number
          job_title?: string
          company?: string | null
          location?: string | null
          years_experience?: number | null
          education_level?: string | null
          industry?: string | null
          employment_type?: string
          benefits_value?: number
          created_at?: string
          updated_at?: string
        }
      }
      raise_requests: {
        Row: {
          id: string
          user_id: string
          salary_entry_id: string
          requested_salary: number
          current_salary: number
          percentage_increase: number
          justification: string | null
          ai_generated_letter: string | null
          cpi_data: any | null
          benchmark_data: any | null
          status: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          salary_entry_id: string
          requested_salary: number
          current_salary: number
          percentage_increase: number
          justification?: string | null
          ai_generated_letter?: string | null
          cpi_data?: any | null
          benchmark_data?: any | null
          status?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          salary_entry_id?: string
          requested_salary?: number
          current_salary?: number
          percentage_increase?: number
          justification?: string | null
          ai_generated_letter?: string | null
          cpi_data?: any | null
          benchmark_data?: any | null
          status?: string
          created_at?: string
          updated_at?: string
        }
      }
      cpi_data: {
        Row: {
          id: string
          year: number
          month: number
          cpi_value: number
          category: string
          region: string
          created_at: string
        }
        Insert: {
          id?: string
          year: number
          month: number
          cpi_value: number
          category?: string
          region?: string
          created_at?: string
        }
        Update: {
          id?: string
          year?: number
          month?: number
          cpi_value?: number
          category?: string
          region?: string
          created_at?: string
        }
      }
      benchmarks: {
        Row: {
          id: string
          job_title: string
          location: string
          salary_min: number | null
          salary_max: number | null
          salary_median: number | null
          salary_avg: number | null
          percentile_10: number | null
          percentile_25: number | null
          percentile_75: number | null
          percentile_90: number | null
          source: string
          data_date: string | null
          created_at: string
        }
        Insert: {
          id?: string
          job_title: string
          location: string
          salary_min?: number | null
          salary_max?: number | null
          salary_median?: number | null
          salary_avg?: number | null
          percentile_10?: number | null
          percentile_25?: number | null
          percentile_75?: number | null
          percentile_90?: number | null
          source?: string
          data_date?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          job_title?: string
          location?: string
          salary_min?: number | null
          salary_max?: number | null
          salary_median?: number | null
          salary_avg?: number | null
          percentile_10?: number | null
          percentile_25?: number | null
          percentile_75?: number | null
          percentile_90?: number | null
          source?: string
          data_date?: string | null
          created_at?: string
        }
      }
    }
  }
} 