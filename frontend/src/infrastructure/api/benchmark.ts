/**
 * Benchmark API Client for WageLift Frontend
 * 
 * Provides functions to interact with salary benchmark endpoints,
 * including search, comparison, and statistics functionality.
 */

import { getToken } from '@/hooks/use-auth'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// TypeScript interfaces matching backend models
export interface BenchmarkSearchRequest {
  job_title: string
  location: string
  radius?: number
  refresh?: boolean
}

export interface SalaryComparisonRequest {
  current_salary: number
  job_title: string
  location: string
}

export interface BenchmarkResponse {
  id: string
  job_title: string
  location: string
  location_type: string
  base_salary_min: number
  base_salary_max: number
  base_salary_median?: number
  source: string
  effective_date: string
  confidence_score?: number
  sample_size?: number
}

export interface PercentileData {
  p10?: number
  p25?: number
  p50?: number
  p75?: number
  p90?: number
}

export interface SalaryComparisonResponse {
  current_salary: number
  job_title: string
  location: string
  percentiles: PercentileData
  percentile_rank?: number
  market_position?: string
  recommendations: string[]
  benchmark_count: number
}

export interface BenchmarkStatsResponse {
  total_benchmarks: number
  active_benchmarks: number
  sources: Record<string, number>
  recent_updates: number
  coverage_by_location: Record<string, number>
  coverage_by_job_family: Record<string, number>
}

// API Error handling
export class BenchmarkAPIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message)
    this.name = 'BenchmarkAPIError'
  }
}

// Helper function to make authenticated requests
async function makeRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const token = await getToken()
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`
      
      try {
        const errorData = JSON.parse(errorText)
        errorMessage = errorData.detail || errorMessage
      } catch {
        // Use default error message if JSON parsing fails
      }
      
      throw new BenchmarkAPIError(
        errorMessage,
        response.status,
        errorText
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof BenchmarkAPIError) {
      throw error
    }
    throw new BenchmarkAPIError(
      `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
    )
  }
}

/**
 * Search for salary benchmarks by job title and location
 */
export async function searchBenchmarks(
  request: BenchmarkSearchRequest
): Promise<BenchmarkResponse[]> {
  return makeRequest<BenchmarkResponse[]>('/api/v1/benchmark/search', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

/**
 * Compare a salary against market benchmarks
 */
export async function compareSalary(
  request: SalaryComparisonRequest
): Promise<SalaryComparisonResponse> {
  return makeRequest<SalaryComparisonResponse>('/api/v1/benchmark/compare', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

/**
 * Get salary percentiles for a job title and location
 */
export async function getPercentiles(
  jobTitle: string,
  location: string
): Promise<PercentileData> {
  const params = new URLSearchParams({
    job_title: jobTitle,
    location: location,
  })
  
  return makeRequest<PercentileData>(`/api/v1/benchmark/percentiles?${params}`)
}

/**
 * Get benchmark statistics
 */
export async function getBenchmarkStats(): Promise<BenchmarkStatsResponse> {
  return makeRequest<BenchmarkStatsResponse>('/api/v1/benchmark/stats')
}

/**
 * Refresh benchmark data (background task)
 */
export async function refreshBenchmarkData(
  daysOld: number = 30
): Promise<{ message: string; status: string; days_old_threshold: number }> {
  const params = new URLSearchParams({
    days_old: daysOld.toString(),
  })
  
  return makeRequest(`/api/v1/benchmark/refresh?${params}`, {
    method: 'POST',
  })
}

// Utility functions for working with benchmark data

/**
 * Format salary values consistently
 */
export function formatSalary(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

/**
 * Format percentile rank
 */
export function formatPercentileRank(rank?: number): string {
  if (rank === undefined) return 'N/A'
  return `${rank.toFixed(1)}th percentile`
}

/**
 * Get color for market position
 */
export function getMarketPositionColor(position?: string): string {
  if (!position) return 'gray'
  
  if (position.includes('Excellent') || position.includes('Top 10%')) {
    return 'green'
  } else if (position.includes('Above Market') || position.includes('Top 25%')) {
    return 'blue'
  } else if (position.includes('Good') || position.includes('Above Median')) {
    return 'yellow'
  } else if (position.includes('Consider Raise') || position.includes('Below Median')) {
    return 'orange'
  } else if (position.includes('Significant Gap') || position.includes('Bottom 25%')) {
    return 'red'
  }
  
  return 'gray'
}

/**
 * Calculate salary gap from percentiles
 */
export function calculateSalaryGap(
  currentSalary: number,
  percentiles: PercentileData
): {
  toMedian: number
  toMedianPercent: number
  to75th: number
  to75thPercent: number
} {
  const median = percentiles.p50 || 0
  const p75 = percentiles.p75 || 0
  
  const toMedian = Math.max(0, median - currentSalary)
  const toMedianPercent = currentSalary > 0 ? (toMedian / currentSalary) * 100 : 0
  
  const to75th = Math.max(0, p75 - currentSalary)
  const to75thPercent = currentSalary > 0 ? (to75th / currentSalary) * 100 : 0
  
  return {
    toMedian,
    toMedianPercent,
    to75th,
    to75thPercent,
  }
}

/**
 * Get benchmark data quality indicator
 */
export function getBenchmarkQuality(benchmarkCount: number): {
  level: 'high' | 'medium' | 'low'
  description: string
  color: string
} {
  if (benchmarkCount >= 10) {
    return {
      level: 'high',
      description: 'High confidence - based on comprehensive market data',
      color: 'green'
    }
  } else if (benchmarkCount >= 5) {
    return {
      level: 'medium',
      description: 'Medium confidence - based on moderate market data',
      color: 'yellow'
    }
  } else {
    return {
      level: 'low',
      description: 'Low confidence - limited market data available',
      color: 'red'
    }
  }
}

/**
 * Extract location components (city, state) from location string
 */
export function parseLocation(location: string): {
  city?: string
  state?: string
  full: string
} {
  const parts = location.split(',').map(part => part.trim())
  
  if (parts.length >= 2) {
    return {
      city: parts[0],
      state: parts[1],
      full: location
    }
  }
  
  return {
    full: location
  }
}

/**
 * Generate market insights based on comparison data
 */
export function generateMarketInsights(
  comparison: SalaryComparisonResponse
): string[] {
  const insights: string[] = []
  const { percentile_rank, percentiles, current_salary } = comparison
  
  if (percentile_rank !== undefined) {
    if (percentile_rank < 10) {
      insights.push('🔴 Your salary is significantly below market rate')
      insights.push('💡 Consider immediate salary negotiation or job search')
    } else if (percentile_rank < 25) {
      insights.push('🟠 Your salary is below the 25th percentile')
      insights.push('📈 Strong case for a substantial raise request')
    } else if (percentile_rank < 50) {
      insights.push('🟡 Your salary is below the median')
      insights.push('💼 Good opportunity for salary improvement')
    } else if (percentile_rank < 75) {
      insights.push('🟢 Your salary is above median - solid position')
      insights.push('🎯 Focus on performance-based increases')
    } else {
      insights.push('🌟 Excellent! You\'re in the top quartile')
      insights.push('🚀 Consider leadership roles or equity compensation')
    }
  }
  
  // Add specific gap information
  if (percentiles.p50 && current_salary < percentiles.p50) {
    const gap = percentiles.p50 - current_salary
    const gapPercent = (gap / current_salary) * 100
    insights.push(`💰 Gap to median: ${formatSalary(gap)} (${gapPercent.toFixed(1)}%)`)
  }
  
  return insights
}

/**
 * Validate benchmark search request
 */
export function validateBenchmarkSearch(request: BenchmarkSearchRequest): string[] {
  const errors: string[] = []
  
  if (!request.job_title || request.job_title.trim().length < 2) {
    errors.push('Job title must be at least 2 characters')
  }
  
  if (!request.location || request.location.trim().length < 2) {
    errors.push('Location must be at least 2 characters')
  }
  
  if (request.radius && (request.radius < 5 || request.radius > 100)) {
    errors.push('Radius must be between 5 and 100 miles')
  }
  
  return errors
}

/**
 * Validate salary comparison request  
 */
export function validateSalaryComparison(request: SalaryComparisonRequest): string[] {
  const errors: string[] = []
  
  if (!request.current_salary || request.current_salary <= 0) {
    errors.push('Current salary must be a positive number')
  }
  
  if (request.current_salary > 10000000) {
    errors.push('Current salary exceeds maximum allowed value')
  }
  
  if (!request.job_title || request.job_title.trim().length < 2) {
    errors.push('Job title must be at least 2 characters')
  }
  
  if (!request.location || request.location.trim().length < 2) {
    errors.push('Location must be at least 2 characters')
  }
  
  return errors
} 