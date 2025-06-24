/**
 * CPI API client for WageLift frontend.
 * Handles CPI gap calculations and inflation analysis with Auth0 integration.
 */

// Types matching backend Pydantic models
export interface CPICalculationRequest {
  original_salary: number;
  current_salary: number;
  historical_date: string; // ISO date string (YYYY-MM-DD)
  current_date?: string; // ISO date string, defaults to today
}

export interface CPICalculationData {
  adjusted_salary: number;
  percentage_gap: number;
  dollar_gap: number;
  original_salary: number;
  current_salary: number;
  inflation_rate: number;
  years_elapsed: number;
  calculation_method: string;
  calculation_date: string;
  historical_date: string;
  current_date: string;
}

export interface CPICalculationResponse {
  success: boolean;
  data: CPICalculationData;
  calculation_id: string;
  timestamp: string;
  user_id: string;
}

export interface InflationSummaryRequest {
  start_date: string; // ISO date string
  end_date: string; // ISO date string
}

export interface InflationSummaryData {
  start_date: string;
  end_date: string;
  total_inflation_percent: number;
  annualized_inflation_percent: number;
  years_analyzed: number;
  purchasing_power_loss: number;
  calculation_method: string;
  note?: string;
}

export interface InflationSummaryResponse {
  success: boolean;
  summary: InflationSummaryData;
  timestamp: string;
}

export interface CPIErrorResponse {
  error: string;
  message: string;
  calculation_id?: string;
  suggestions?: string[];
  timestamp?: string;
}

export interface CPIHealthResponse {
  status: string;
  service: string;
  timestamp: string;
  version: string;
  note?: string;
}

// API Configuration
const API_BASE_URL = typeof window !== 'undefined' 
  ? (window as any).ENV?.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  : 'http://localhost:8000';
const API_VERSION = '/api/v1';

// CPI API Client Class
export class CPIApiClient {
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
        // 'Authorization': `Bearer ${token}`,
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
      let errorData: CPIErrorResponse;
      
      try {
        errorData = await response.json() as CPIErrorResponse;
      } catch {
        // If JSON parsing fails, create a generic error
        errorData = {
          error: 'Network Error',
          message: `HTTP ${response.status}: ${response.statusText}`,
        };
      }
      
      // Create user-friendly error message
      const errorMessage = errorData.message || 'An unexpected error occurred during calculation';
      const suggestions = errorData.suggestions || [];
      
      throw new Error(
        `${errorMessage}${suggestions.length > 0 
          ? '\n\nSuggestions:\n' + suggestions.map(s => `• ${s}`).join('\n')
          : ''}`
      );
    }

    return response.json();
  }

  /**
   * Calculate salary gap based on inflation
   */
  async calculateSalaryGap(request: CPICalculationRequest): Promise<CPICalculationResponse> {
    try {
      const headers = await this.getAuthHeaders();
      
      // Validate request data
      if (request.original_salary <= 0 || request.current_salary <= 0) {
        throw new Error('Salary amounts must be greater than zero');
      }

      if (!request.historical_date) {
        throw new Error('Historical date is required');
      }

      // Set current_date to today if not provided
      const requestData = {
        ...request,
        current_date: request.current_date || new Date().toISOString().split('T')[0]
      };

      const response = await fetch(`${this.baseUrl}/cpi/calculate-gap`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestData),
      });

      return this.handleResponse<CPICalculationResponse>(response);
    } catch (error) {
      console.error('Error calculating salary gap:', error);
      throw error;
    }
  }

  /**
   * Get inflation summary for a date range
   */
  async getInflationSummary(request: InflationSummaryRequest): Promise<InflationSummaryResponse> {
    try {
      const headers = await this.getAuthHeaders();
      
      // Validate request data
      if (!request.start_date || !request.end_date) {
        throw new Error('Both start and end dates are required');
      }

      if (new Date(request.start_date) >= new Date(request.end_date)) {
        throw new Error('Start date must be before end date');
      }

      const response = await fetch(`${this.baseUrl}/cpi/inflation-summary`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });

      return this.handleResponse<InflationSummaryResponse>(response);
    } catch (error) {
      console.error('Error getting inflation summary:', error);
      throw error;
    }
  }

  /**
   * Check CPI service health
   */
  async healthCheck(): Promise<CPIHealthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/cpi/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      return this.handleResponse<CPIHealthResponse>(response);
    } catch (error) {
      console.error('Error checking CPI service health:', error);
      throw error;
    }
  }
}

// Singleton instance
export const cpiApi = new CPIApiClient();

// Utility functions for data formatting
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
}

export function formatInflationRate(rate: number): string {
  return `${rate.toFixed(1)}%`;
}

export function getGapStatus(percentageGap: number): 'positive' | 'negative' | 'neutral' {
  if (percentageGap > 0.5) return 'positive';
  if (percentageGap < -0.5) return 'negative';
  return 'neutral';
}

export function getGapStatusMessage(percentageGap: number, dollarGap: number): string {
  const status = getGapStatus(percentageGap);
  const absGap = Math.abs(dollarGap);
  
  switch (status) {
    case 'positive':
      return `Your current salary is ${formatCurrency(absGap)} above inflation-adjusted expectations`;
    case 'negative':
      return `Your current salary is ${formatCurrency(absGap)} below inflation-adjusted expectations`;
    case 'neutral':
      return 'Your current salary is roughly in line with inflation-adjusted expectations';
  }
}

// React hook for CPI calculations
export function useCPIApi() {
  return {
    calculateSalaryGap: cpiApi.calculateSalaryGap.bind(cpiApi),
    getInflationSummary: cpiApi.getInflationSummary.bind(cpiApi),
    healthCheck: cpiApi.healthCheck.bind(cpiApi),
    formatCurrency,
    formatPercentage,
    formatInflationRate,
    getGapStatus,
    getGapStatusMessage,
  };
}

// Error handling utilities
export function isCPIApiError(error: unknown): error is Error {
  return error instanceof Error;
}

export function handleCPIApiError(error: unknown): string {
  if (isCPIApiError(error)) {
    return error.message;
  }
  return 'An unexpected error occurred during CPI calculation';
} 