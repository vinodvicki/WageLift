// Types for salary benchmarking
export interface PercentileData {
  percentile: number
  salary: number
  label?: string
}

export interface SalaryComparisonResponse {
  occupation: string
  location: string
  percentiles: PercentileData[]
  user_percentile: number
  median_salary: number
  mean_salary: number
  total_employment: number
  data_source: string
  last_updated: string
}

export interface BenchmarkRequest {
  occupation: string
  location?: string
  years_experience?: number
  education_level?: string
  industry?: string
  company_size?: string
}

export interface MarketInsight {
  trend: 'increasing' | 'stable' | 'decreasing'
  growth_rate: number
  demand_level: 'high' | 'medium' | 'low'
  supply_level: 'high' | 'medium' | 'low'
}

export interface BenchmarkDetailedResponse extends SalaryComparisonResponse {
  market_insights: MarketInsight
  similar_roles: Array<{
    title: string
    median_salary: number
    similarity_score: number
  }>
  location_adjustments: Array<{
    location: string
    adjustment_factor: number
    median_salary: number
  }>
}

// Utility functions
export function formatSalary(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
  }).format(value)
}

export function getPercentileLabel(percentile: number): string {
  const suffix = percentile % 10 === 1 && percentile !== 11 ? 'st' :
                 percentile % 10 === 2 && percentile !== 12 ? 'nd' :
                 percentile % 10 === 3 && percentile !== 13 ? 'rd' : 'th'
  return `${percentile}${suffix} percentile`
}

// API client
const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8001'

export async function compareSalary(
  jobTitle: string,
  location: string,
  currentSalary: number
): Promise<SalaryComparisonResponse> {
  try {
    const params = new URLSearchParams({
      job_title: jobTitle,
      location: location,
      current_salary: currentSalary.toString()
    })

    const response = await fetch(`${API_BASE_URL}/api/v1/benchmark/compare?${params}`)

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Failed to fetch salary comparison')
    }

    return await response.json()
  } catch (error) {
    throw new Error('Benchmark service unavailable')
  }
}

export async function getBenchmarkDetails(
  request: BenchmarkRequest
): Promise<BenchmarkDetailedResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/benchmark/detailed`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Failed to fetch benchmark details')
    }

    return await response.json()
  } catch (error) {
    throw new Error('Benchmark service unavailable')
  }
}

export async function searchOccupations(query: string): Promise<string[]> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/benchmark/occupations/search?q=${encodeURIComponent(query)}`
    )

    if (!response.ok) {
      throw new Error('Failed to search occupations')
    }

    return await response.json()
  } catch (error) {
    throw new Error('Benchmark service unavailable')
  }
}

export async function getLocations(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/benchmark/locations`)

    if (!response.ok) {
      throw new Error('Failed to fetch locations')
    }

    return await response.json()
  } catch (error) {
    throw new Error('Benchmark service unavailable')
  }
}