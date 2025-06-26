// Types for CPI calculations
export interface CPICalculationData {
  original_salary: number
  current_salary: number
  adjusted_salary: number
  percentage_gap: number
  dollar_gap: number
  inflation_rate: number
  years_elapsed: number
  calculation_method: string
  calculation_date: string
  historical_date: string
  current_date: string
}

export interface CPIHistoricalData {
  date: string
  value: number
  year_over_year_change: number
}

export interface CPICalculationRequest {
  original_salary: number
  current_salary?: number
  start_date: string
  end_date?: string
  include_historical?: boolean
}

export interface CPICalculationResponse extends CPICalculationData {
  historical_data?: CPIHistoricalData[]
  recommendation: string
  confidence_level: number
}

// Utility functions
export function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
  }).format(value)
}

// API client
const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8001'

export function useCPIApi() {
  const calculateCPI = async (request: CPICalculationRequest): Promise<CPICalculationResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/cpi/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || 'Failed to calculate CPI')
      }

      return await response.json()
    } catch (error) {
      throw new Error('CPI calculation service unavailable')
    }
  }

  const getHistoricalCPI = async (startDate: string, endDate: string): Promise<CPIHistoricalData[]> => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/cpi/historical?start_date=${startDate}&end_date=${endDate}`
      )

      if (!response.ok) {
        throw new Error('Failed to fetch historical CPI data')
      }

      return await response.json()
    } catch (error) {
      throw new Error('CPI service unavailable')
    }
  }

  const getLatestCPI = async (): Promise<CPIHistoricalData> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/cpi/latest`)

      if (!response.ok) {
        throw new Error('Failed to fetch latest CPI')
      }

      return await response.json()
    } catch (error) {
      throw new Error('CPI service unavailable')
    }
  }

  return {
    calculateCPI,
    getHistoricalCPI,
    getLatestCPI
  }
}