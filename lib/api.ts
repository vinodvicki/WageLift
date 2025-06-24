/**
 * API Integration Layer for WageLift Mobile App
 * Connects with FastAPI backend services
 */

import { createClient } from '@supabase/supabase-js'

// API Configuration
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1'
  : 'https://api.wagelift.com/api/v1';

// Supabase configuration (matches backend)
const supabaseUrl = 'https://rtmegwnspngsxtixdhat.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0bWVnd25zcG5nc3h0aXhkaGF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1NTczOTksImV4cCI6MjA2NjEzMzM5OX0.DdZ48QWj-lwyaWmUVW-CbIO-qKVrb6b6MRTdfBYDO3g'
export const supabase = createClient(supabaseUrl, supabaseKey)

// Types (Updated to match backend API)
export interface SalaryFormData {
  annual_salary: number;
  last_raise_date: string;
  job_title: string;
  company: string;
  location: string;
}

export interface CPICalculationResponse {
  adjusted_salary: number;
  percentage_gap: number;
  dollar_gap: number;
  inflation_rate: number;
  years_elapsed: number;
  calculation_date: string;
  historical_date: string;
  cpi_data: {
    current: number;
    historical: number;
    difference: number;
  };
  recommendations: string[];
  severity: 'minimal' | 'moderate' | 'significant' | 'severe';
}

export interface BenchmarkData {
  percentile_10: number;
  percentile_25: number;
  percentile_50: number;
  percentile_75: number;
  percentile_90: number;
  user_percentile: number;
  market_position: string;
  occupation_title: string;
  location: string;
}

export interface RaiseLetterRequest {
  user_context: {
    name: string;
    job_title: string;
    company: string;
    years_at_company?: number;
  };
  cpi_data: CPICalculationResponse;
  benchmark_data?: BenchmarkData;
  tone: 'professional' | 'confident' | 'collaborative' | 'assertive';
  length: 'concise' | 'standard' | 'detailed';
}

export interface RaiseLetterResponse {
  letter_content: string;
  subject_line: string;
  key_points: string[];
  tone_used: string;
  length_used: string;
}

// User Authentication
export interface User {
  id: string;
  email: string;
  full_name?: string;
  auth0_id?: string;
}

// API Client Class
class WageLiftAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        return {
          'Authorization': `Bearer ${session.access_token}`,
        };
      }
      return {};
    } catch (error) {
      console.warn('Failed to get auth headers:', error);
      return {};
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const authHeaders = await this.getAuthHeaders();
    const defaultHeaders = {
      'Content-Type': 'application/json',
      ...authHeaders,
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || 
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network request failed');
    }
  }

  // Authentication Methods
  async signInWithEmail(email: string, password: string): Promise<User | null> {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;
      
      if (data.user) {
        return {
          id: data.user.id,
          email: data.user.email!,
          full_name: data.user.user_metadata?.full_name,
        };
      }
      
      return null;
    } catch (error) {
      throw error;
    }
  }

  async signUpWithEmail(email: string, password: string, fullName?: string): Promise<User | null> {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (error) throw error;
      
      if (data.user) {
        return {
          id: data.user.id,
          email: data.user.email!,
          full_name: fullName,
        };
      }
      
      return null;
    } catch (error) {
      throw error;
    }
  }

  async signOut(): Promise<void> {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (user) {
        return {
          id: user.id,
          email: user.email!,
          full_name: user.user_metadata?.full_name,
        };
      }
      
      return null;
    } catch (error) {
      return null;
    }
  }

  // CPI Calculation
  async calculateCPIGap(formData: SalaryFormData): Promise<CPICalculationResponse> {
    return this.request<CPICalculationResponse>('/cpi/calculate-gap', {
      method: 'POST',
      body: JSON.stringify({
        original_salary: formData.annual_salary,
        current_salary: formData.annual_salary,
        historical_date: formData.last_raise_date,
        current_date: new Date().toISOString().split('T')[0],
      }),
    });
  }

  // Salary Benchmarking
  async getBenchmarkData(
    jobTitle: string,
    location: string
  ): Promise<BenchmarkData> {
    return this.request<BenchmarkData>(
      `/benchmark/salary-percentiles?job_title=${encodeURIComponent(jobTitle)}&location=${encodeURIComponent(location)}`
    );
  }

  // AI Letter Generation
  async generateRaiseLetter(request: RaiseLetterRequest): Promise<RaiseLetterResponse> {
    return this.request<RaiseLetterResponse>('/raise-letter/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Email Sending
  async sendRaiseLetter(
    letterContent: string,
    subjectLine: string,
    managerEmail: string
  ): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>('/email/send-raise-letter', {
      method: 'POST',
      body: JSON.stringify({
        letter_content: letterContent,
        subject_line: subjectLine,
        manager_email: managerEmail,
      }),
    });
  }

  // Salary Entry Management
  async saveSalaryEntry(salaryData: SalaryFormData): Promise<any> {
    return this.request('/salary/entry', {
      method: 'POST',
      body: JSON.stringify(salaryData),
    });
  }

  async getUserSalaryEntries(): Promise<any[]> {
    return this.request('/salary/entries');
  }
}

// Export singleton instance
export const api = new WageLiftAPI();

// Error handling utility
export const handleApiError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

// Loading state management
export const createLoadingState = () => {
  let loading = false;
  
  return {
    setLoading: (state: boolean) => { loading = state; },
    isLoading: () => loading,
  };
}; 