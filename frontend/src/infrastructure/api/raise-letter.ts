/**
 * Raise Letter API Client
 * 
 * TypeScript client for AI-powered raise letter generation using OpenAI GPT-4 Turbo.
 * Provides type-safe interfaces and comprehensive error handling for letter generation.
 */

import { type CPICalculationData } from './cpi';
import { type SalaryComparisonResponse } from './benchmark';

// API Base Configuration
const API_BASE = 'http://localhost:8000';
const RAISE_LETTER_ENDPOINT = `${API_BASE}/api/v1/raise-letter`;

// Enums matching backend
export enum LetterTone {
  PROFESSIONAL = 'professional',
  CONFIDENT = 'confident',
  COLLABORATIVE = 'collaborative',
  ASSERTIVE = 'assertive'
}

export enum LetterLength {
  CONCISE = 'concise',
  STANDARD = 'standard',
  DETAILED = 'detailed'
}

// Type Definitions
export interface GenerateLetterRequest {
  // User Information
  user_name: string;
  job_title: string;
  company: string;
  department?: string | undefined;
  manager_name?: string | undefined;
  years_at_company?: number | undefined;
  
  // CPI Data (required)
  current_salary: number;
  adjusted_salary: number;
  percentage_gap: number;
  dollar_gap: number;
  inflation_rate: number;
  years_elapsed: number;
  calculation_method: string;
  calculation_date: string;
  historical_date: string;
  
  // Benchmark Data (optional)
  benchmark_data?: Record<string, any>;
  
  // Letter Preferences
  tone: LetterTone;
  length: LetterLength;
  
  // Additional Content
  key_achievements?: string[];
  recent_projects?: string[];
  custom_points?: string[];
  requested_increase?: number;
}

export interface GenerateLetterResponse {
  success: boolean;
  letter_content: string;
  subject_line: string;
  key_points: string[];
  tone_used: LetterTone;
  length_used: LetterLength;
  generation_metadata: {
    model_used: string;
    tokens_used: number;
    generation_time: string;
    prompt_tokens: number;
    completion_tokens: number;
  };
  generated_at: string;
}

export interface LetterToneOption {
  value: LetterTone;
  label: string;
  description: string;
}

export interface LetterLengthOption {
  value: LetterLength;
  label: string;
  description: string;
}

export interface RaiseLetterServiceHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  openai_connected: boolean;
  service: string;
  timestamp: string;
  model?: string;
  error?: string;
}

// Custom Error Classes
export class RaiseLetterAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'RaiseLetterAPIError';
  }
}

export class RaiseLetterValidationError extends RaiseLetterAPIError {
  constructor(message: string, public validationErrors?: Record<string, string[]>) {
    super(message, 400);
    this.name = 'RaiseLetterValidationError';
  }
}

export class RaiseLetterServiceError extends RaiseLetterAPIError {
  constructor(message: string) {
    super(message, 503);
    this.name = 'RaiseLetterServiceError';
  }
}

// API Client Class
export class RaiseLetterAPI {
  private baseUrl: string;
  
  constructor(baseUrl: string = RAISE_LETTER_ENDPOINT) {
    this.baseUrl = baseUrl;
  }
  
  /**
   * Get authentication headers for API requests
   */
  private async getAuthHeaders(): Promise<Record<string, string>> {
    try {
      // Get token from Auth0 or session storage
      const token = localStorage.getItem('accessToken') || 
                   sessionStorage.getItem('accessToken');
      
      if (!token) {
        throw new RaiseLetterAPIError('Authentication required', 401);
      }
      
      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };
    } catch (error) {
      throw new RaiseLetterAPIError('Failed to get authentication headers', 401);
    }
  }
  
  /**
   * Handle API response and errors
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      switch (response.status) {
        case 400:
          throw new RaiseLetterValidationError(
            errorData.detail || 'Invalid request data',
            errorData.validation_errors
          );
        case 401:
          throw new RaiseLetterAPIError('Authentication required', 401);
        case 403:
          throw new RaiseLetterAPIError('Access denied', 403);
        case 503:
          throw new RaiseLetterServiceError(
            errorData.detail || 'AI service temporarily unavailable'
          );
        default:
          throw new RaiseLetterAPIError(
            errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            errorData
          );
      }
    }
    
    return response.json();
  }
  
  /**
   * Generate a raise letter using AI
   */
  async generateLetter(request: GenerateLetterRequest): Promise<GenerateLetterResponse> {
    try {
      const headers = await this.getAuthHeaders();
      
      const response = await fetch(`${this.baseUrl}/generate`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });
      
      return this.handleResponse<GenerateLetterResponse>(response);
    } catch (error) {
      if (error instanceof RaiseLetterAPIError) {
        throw error;
      }
      throw new RaiseLetterAPIError(
        `Failed to generate raise letter: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }
  
  /**
   * Generate raise letter with streaming response
   */
  async generateLetterStream(
    request: GenerateLetterRequest,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const headers = await this.getAuthHeaders();
      
      const response = await fetch(`${this.baseUrl}/generate/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });
      
      if (!response.ok) {
        await this.handleResponse(response);
        return;
      }
      
      const reader = response.body?.getReader();
      if (!reader) {
        throw new RaiseLetterAPIError('Streaming not supported');
      }
      
      const decoder = new TextDecoder();
      
      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            onComplete();
            break;
          }
          
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              
              if (data === '[DONE]') {
                onComplete();
                return;
              }
              
              if (data.startsWith('[ERROR:')) {
                const errorMessage = data.slice(7, -1);
                onError(new RaiseLetterServiceError(errorMessage));
                return;
              }
              
              onChunk(data);
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      if (error instanceof RaiseLetterAPIError) {
        onError(error);
      } else {
        onError(new RaiseLetterAPIError(
          `Streaming failed: ${error instanceof Error ? error.message : 'Unknown error'}`
        ));
      }
    }
  }
  
  /**
   * Get available letter tones
   */
  async getLetterTones(): Promise<Record<string, string>> {
    try {
      const response = await fetch(`${this.baseUrl}/tones`);
      return this.handleResponse<Record<string, string>>(response);
    } catch (error) {
      throw new RaiseLetterAPIError(
        `Failed to get letter tones: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }
  
  /**
   * Get available letter lengths
   */
  async getLetterLengths(): Promise<Record<string, string>> {
    try {
      const response = await fetch(`${this.baseUrl}/lengths`);
      return this.handleResponse<Record<string, string>>(response);
    } catch (error) {
      throw new RaiseLetterAPIError(
        `Failed to get letter lengths: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }
  
  /**
   * Check service health
   */
  async checkHealth(): Promise<RaiseLetterServiceHealth> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return this.handleResponse<RaiseLetterServiceHealth>(response);
    } catch (error) {
      throw new RaiseLetterAPIError(
        `Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }
}

// Utility Functions

/**
 * Convert CPI calculation data to raise letter request format
 */
export function cpiDataToLetterRequest(
  cpiData: CPICalculationData,
  userInfo: {
    name: string;
    job_title: string;
    company: string;
    department?: string;
    manager_name?: string;
    years_at_company?: number;
  },
  preferences: {
    tone: LetterTone;
    length: LetterLength;
    key_achievements?: string[];
    recent_projects?: string[];
    custom_points?: string[];
    requested_increase?: number;
  },
  benchmarkData?: SalaryComparisonResponse
): GenerateLetterRequest {
  return {
    // User information
    user_name: userInfo.name,
    job_title: userInfo.job_title,
    company: userInfo.company,
    department: userInfo.department || undefined,
    manager_name: userInfo.manager_name || undefined,
    years_at_company: userInfo.years_at_company || undefined,
    
    // CPI data
    current_salary: cpiData.current_salary,
    adjusted_salary: cpiData.adjusted_salary,
    percentage_gap: cpiData.percentage_gap,
    dollar_gap: cpiData.dollar_gap,
    inflation_rate: cpiData.inflation_rate,
    years_elapsed: cpiData.years_elapsed,
    calculation_method: cpiData.calculation_method,
    calculation_date: cpiData.calculation_date,
    historical_date: cpiData.historical_date,
    
    // Benchmark data (optional)
    benchmark_data: benchmarkData ? {
      percentile_10: benchmarkData.percentiles.p10 || 0,
      percentile_25: benchmarkData.percentiles.p25 || 0,
      percentile_50: benchmarkData.percentiles.p50 || 0,
      percentile_75: benchmarkData.percentiles.p75 || 0,
      percentile_90: benchmarkData.percentiles.p90 || 0,
      user_percentile: benchmarkData.percentile_rank || 0,
      market_position: benchmarkData.market_position || 'Unknown',
      occupation_title: benchmarkData.job_title,
      location: benchmarkData.location,
      data_source: 'CareerOneStop',
      confidence_score: benchmarkData.benchmark_count >= 10 ? 8.5 : 6.0
    } : undefined,
    
    // Preferences
    tone: preferences.tone,
    length: preferences.length,
    key_achievements: preferences.key_achievements || [],
    recent_projects: preferences.recent_projects || [],
    custom_points: preferences.custom_points || [],
    requested_increase: preferences.requested_increase
  };
}

/**
 * Get user-friendly tone options
 */
export function getLetterToneOptions(): LetterToneOption[] {
  return [
    {
      value: LetterTone.PROFESSIONAL,
      label: 'Professional',
      description: 'Formal and respectful tone with traditional business language'
    },
    {
      value: LetterTone.CONFIDENT,
      label: 'Confident',
      description: 'Self-assured while remaining respectful and professional'
    },
    {
      value: LetterTone.COLLABORATIVE,
      label: 'Collaborative',
      description: 'Partnership-focused emphasizing mutual benefit and team success'
    },
    {
      value: LetterTone.ASSERTIVE,
      label: 'Assertive',
      description: 'Direct and clear while maintaining professionalism'
    }
  ];
}

/**
 * Get user-friendly length options
 */
export function getLetterLengthOptions(): LetterLengthOption[] {
  return [
    {
      value: LetterLength.CONCISE,
      label: 'Concise',
      description: 'Brief and to the point (200-300 words)'
    },
    {
      value: LetterLength.STANDARD,
      label: 'Standard',
      description: 'Standard business letter with full context (300-500 words)'
    },
    {
      value: LetterLength.DETAILED,
      label: 'Detailed',
      description: 'Comprehensive with extensive detail (500-800 words)'
    }
  ];
}

/**
 * Validate raise letter request data
 */
export function validateLetterRequest(request: Partial<GenerateLetterRequest>): string[] {
  const errors: string[] = [];
  
  // Required user information
  if (!request.user_name?.trim()) {
    errors.push('User name is required');
  }
  if (!request.job_title?.trim()) {
    errors.push('Job title is required');
  }
  if (!request.company?.trim()) {
    errors.push('Company name is required');
  }
  
  // Required CPI data
  if (!request.current_salary || request.current_salary <= 0) {
    errors.push('Current salary must be greater than 0');
  }
  if (!request.adjusted_salary || request.adjusted_salary <= 0) {
    errors.push('Adjusted salary must be greater than 0');
  }
  if (request.current_salary && request.adjusted_salary && 
      request.adjusted_salary <= request.current_salary) {
    errors.push('Adjusted salary must be greater than current salary');
  }
  if (request.percentage_gap === undefined || request.percentage_gap < 0) {
    errors.push('Percentage gap must be 0 or greater');
  }
  if (request.dollar_gap === undefined || request.dollar_gap < 0) {
    errors.push('Dollar gap must be 0 or greater');
  }
  if (!request.years_elapsed || request.years_elapsed < 1) {
    errors.push('Years elapsed must be at least 1');
  }
  
  // Optional validations
  if (request.years_at_company !== undefined && request.years_at_company < 0) {
    errors.push('Years at company cannot be negative');
  }
  if (request.requested_increase !== undefined && request.requested_increase <= 0) {
    errors.push('Requested increase must be greater than 0');
  }
  
  return errors;
}

/**
 * Format generation metadata for display
 */
export function formatGenerationMetadata(metadata: GenerateLetterResponse['generation_metadata']): {
  model: string;
  tokensUsed: string;
  generationTime: string;
  efficiency: string;
} {
  const generationDate = new Date(metadata.generation_time);
  
  return {
    model: metadata.model_used,
    tokensUsed: `${metadata.tokens_used.toLocaleString()} tokens`,
    generationTime: generationDate.toLocaleString(),
    efficiency: `${metadata.prompt_tokens} prompt + ${metadata.completion_tokens} completion`
  };
}

// Global API instance
export const raiseLetterAPI = new RaiseLetterAPI();

// React Hook for Raise Letter API
export function useRaiseLetterAPI() {
  return {
    generateLetter: raiseLetterAPI.generateLetter.bind(raiseLetterAPI),
    generateLetterStream: raiseLetterAPI.generateLetterStream.bind(raiseLetterAPI),
    getLetterTones: raiseLetterAPI.getLetterTones.bind(raiseLetterAPI),
    getLetterLengths: raiseLetterAPI.getLetterLengths.bind(raiseLetterAPI),
    checkHealth: raiseLetterAPI.checkHealth.bind(raiseLetterAPI),
    
    // Utility functions
    cpiDataToLetterRequest,
    getLetterToneOptions,
    getLetterLengthOptions,
    validateLetterRequest,
    formatGenerationMetadata
  };
}

// Export everything
export default raiseLetterAPI; 