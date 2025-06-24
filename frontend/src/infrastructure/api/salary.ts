/**
 * Salary API client for WageLift frontend.
 * Handles salary form submission and data management with Auth0 integration.
 */

// Types matching backend Pydantic models
export interface SalaryFormData {
  current_salary: number;
  last_raise_date: string; // ISO date string
  job_title: string;
  location: string; // ZIP code
  experience_level: 'entry' | 'mid' | 'senior' | 'lead' | 'executive';
  company_size: 'startup' | 'small' | 'medium' | 'large' | 'enterprise';
  bonus_amount?: number;
  benefits?: string[];
  equity_details?: string;
  notes?: string;
}

export interface SalaryFormResponse {
  success: boolean;
  message: string;
  data_id?: string;
  submission_timestamp: string;
  analysis_preview?: {
    total_compensation: number;
    experience_level: string;
    warnings: string[];
    next_analysis_available: boolean;
  };
  next_steps: string[];
}

export interface SalaryFormErrorResponse {
  success: boolean;
  message: string;
  errors?: {
    validation_errors?: Array<{
      field: string;
      message: string;
    }>;
  };
  error_code?: string;
  timestamp: string;
  suggestions?: string[];
}

export interface SalaryDataRecord extends SalaryFormData {
  user_id: string;
  created_at: string;
  updated_at: string;
  annual_total_compensation?: number;
  submission_ip?: string;
  form_version: string;
  data_source: string;
}

// API Configuration
const API_BASE_URL = typeof window !== 'undefined' 
  ? (window as any).ENV?.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  : 'http://localhost:8000';
const API_VERSION = '/api/v1';

// API Client Class
export class SalaryApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}${API_VERSION}`;
  }

  /**
   * Get Authorization header with Auth0 token
   */
  private async getAuthHeaders(): Promise<HeadersInit> {
    try {
      // For now, return basic headers - Auth0 integration will be added when available
      // In production, this would get the token from Auth0 context or localStorage
      return {
        'Content-Type': 'application/json',
        // TODO: Add Authorization header when Auth0 is properly configured
      };
    } catch (error) {
      return {
        'Content-Type': 'application/json',
      };
    }
  }

  /**
   * Handle API response with proper error handling
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json() as SalaryFormErrorResponse;
      
      // Create user-friendly error message
      const errorMessage = errorData.message || 'An unexpected error occurred';
      const validationErrors = errorData.errors?.validation_errors || [];
      
      throw new Error(
        `${errorMessage}${validationErrors.length > 0 
          ? '\n\nValidation errors:\n' + validationErrors.map(err => `• ${err.field}: ${err.message}`).join('\n')
          : ''}`
      );
    }

    return response.json();
  }

  /**
   * Submit salary form data
   */
  async submitSalaryForm(data: SalaryFormData): Promise<SalaryFormResponse> {
    try {
      const headers = await this.getAuthHeaders();
      
      const response = await fetch(`${this.baseUrl}/salary/submit`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });

      return this.handleResponse<SalaryFormResponse>(response);
    } catch (error) {
      console.error('Error submitting salary form:', error);
      throw error;
    }
  }

  /**
   * Get user's salary data history
   */
  async getUserSalaryData(): Promise<SalaryDataRecord[]> {
    try {
      const headers = await this.getAuthHeaders();
      
      const response = await fetch(`${this.baseUrl}/salary/user-data`, {
        method: 'GET',
        headers,
      });

      return this.handleResponse<SalaryDataRecord[]>(response);
    } catch (error) {
      console.error('Error fetching user salary data:', error);
      throw error;
    }
  }

  /**
   * Update existing salary data
   */
  async updateSalaryData(
    dataId: string, 
    updates: Partial<SalaryFormData>
  ): Promise<SalaryFormResponse> {
    try {
      const headers = await this.getAuthHeaders();
      
      const response = await fetch(`${this.baseUrl}/salary/update/${dataId}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(updates),
      });

      return this.handleResponse<SalaryFormResponse>(response);
    } catch (error) {
      console.error('Error updating salary data:', error);
      throw error;
    }
  }

  /**
   * Delete salary data
   */
  async deleteSalaryData(dataId: string): Promise<{ success: boolean; message: string }> {
    try {
      const headers = await this.getAuthHeaders();
      
      const response = await fetch(`${this.baseUrl}/salary/delete/${dataId}`, {
        method: 'DELETE',
        headers,
      });

      return this.handleResponse<{ success: boolean; message: string }>(response);
    } catch (error) {
      console.error('Error deleting salary data:', error);
      throw error;
    }
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/salary/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      return this.handleResponse<{ status: string; service: string }>(response);
    } catch (error) {
      console.error('Error checking API health:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const salaryApi = new SalaryApiClient();

// Utility functions for form data conversion
export function convertFormDataToApiFormat(formData: any): SalaryFormData {
  const result: SalaryFormData = {
    current_salary: parseInt(formData.currentSalary),
    last_raise_date: formData.lastRaiseDate, // Should already be ISO string from form
    job_title: formData.jobTitle,
    location: formData.location,
    experience_level: formData.experienceLevel,
    company_size: formData.companySize,
  };

  // Add optional fields only if they have values
  if (formData.bonusAmount) {
    result.bonus_amount = parseInt(formData.bonusAmount);
  }
  if (formData.benefits && formData.benefits.length > 0) {
    result.benefits = formData.benefits;
  }
  if (formData.equityDetails) {
    result.equity_details = formData.equityDetails;
  }
  if (formData.notes) {
    result.notes = formData.notes;
  }

  return result;
}

export function convertApiDataToFormFormat(apiData: SalaryDataRecord): any {
  return {
    current_salary: apiData.current_salary.toString(),
    last_raise_date: apiData.last_raise_date.split('T')[0], // Convert to YYYY-MM-DD for date input
    job_title: apiData.job_title,
    location: apiData.location,
    experience_level: apiData.experience_level,
    company_size: apiData.company_size,
    bonus_amount: apiData.bonus_amount?.toString() || '',
    benefits: apiData.benefits || [],
    equity_details: apiData.equity_details || '',
    notes: apiData.notes || '',
  };
}

// Hook for React components (can be used with React Query or SWR)
export function useSalaryApi() {
  return {
    submitForm: salaryApi.submitSalaryForm.bind(salaryApi),
    getUserData: salaryApi.getUserSalaryData.bind(salaryApi),
    updateData: salaryApi.updateSalaryData.bind(salaryApi),
    deleteData: salaryApi.deleteSalaryData.bind(salaryApi),
    healthCheck: salaryApi.healthCheck.bind(salaryApi),
    convertToApiFormat: convertFormDataToApiFormat,
    convertFromApiFormat: convertApiDataToFormFormat,
  };
} 