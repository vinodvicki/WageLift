// Types for AI-powered raise letter generation
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

export interface GenerateLetterRequest {
  user_info: {
    name: string
    job_title: string
    company: string
    department?: string
    manager_name?: string
    years_at_company: number
  }
  cpi_data: {
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
  preferences: {
    tone: LetterTone
    length: LetterLength
    key_achievements?: string[]
    recent_projects?: string[]
    custom_points?: string[]
    requested_increase?: number
  }
}

export interface GenerateLetterResponse {
  letter_content: string
  subject_line: string
  metadata: {
    word_count: number
    reading_time_minutes: number
    tone: LetterTone
    length: LetterLength
    generated_at: string
  }
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy'
  openai_available: boolean
  model: string
  timestamp: string
}

// Error classes
export class RaiseLetterAPIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message)
    this.name = 'RaiseLetterAPIError'
  }
}

export class RaiseLetterServiceError extends RaiseLetterAPIError {
  constructor(message: string) {
    super(message, 503, 'SERVICE_UNAVAILABLE')
    this.name = 'RaiseLetterServiceError'
  }
}

// Utility functions
export function getLetterToneOptions() {
  return [
    { value: LetterTone.PROFESSIONAL, label: 'Professional', description: 'Formal and business-appropriate' },
    { value: LetterTone.CONFIDENT, label: 'Confident', description: 'Self-assured and direct' },
    { value: LetterTone.COLLABORATIVE, label: 'Collaborative', description: 'Team-oriented and cooperative' },
    { value: LetterTone.ASSERTIVE, label: 'Assertive', description: 'Strong and compelling' }
  ]
}

export function getLetterLengthOptions() {
  return [
    { value: LetterLength.CONCISE, label: 'Concise', description: '~250 words' },
    { value: LetterLength.STANDARD, label: 'Standard', description: '~500 words' },
    { value: LetterLength.DETAILED, label: 'Detailed', description: '~750 words' }
  ]
}

// Convert CPI data to letter request
export function cpiDataToLetterRequest(
  cpiData: any,
  userInfo: any,
  preferences: any
): GenerateLetterRequest {
  return {
    user_info: userInfo,
    cpi_data: cpiData,
    preferences: preferences
  }
}

// API client
const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8001'

export function useRaiseLetterAPI() {
  const generateLetter = async (request: GenerateLetterRequest): Promise<GenerateLetterResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/raise-letter/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new RaiseLetterAPIError(
          error.detail || `Failed to generate letter: ${response.statusText}`,
          response.status
        )
      }

      return await response.json()
    } catch (error) {
      if (error instanceof RaiseLetterAPIError) throw error
      throw new RaiseLetterServiceError('Unable to connect to letter generation service')
    }
  }

  const generateLetterStream = async (
    request: GenerateLetterRequest,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ) => {
    // Streaming not yet implemented in backend, fall back to regular generation
    try {
      const result = await generateLetter(request)
      onChunk(result.letter_content)
      onComplete()
    } catch (error) {
      if (error instanceof Error) {
        onError(error)
      } else {
        onError(new Error('Unknown error'))
      }
    }
    return
    // Original streaming code kept for future implementation
    /*
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/raise-letter/generate/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new RaiseLetterAPIError(
          error.detail || `Failed to generate letter: ${response.statusText}`,
          response.status
        )
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new RaiseLetterServiceError('Streaming not supported')
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          onComplete()
          break
        }

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(line => line.trim())
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              onComplete()
              return
            }
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                onChunk(parsed.content)
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof RaiseLetterAPIError) {
        onError(error)
      } else {
        onError(new RaiseLetterServiceError('Streaming failed'))
      }
    }
    */
  }

  const checkHealth = async (): Promise<HealthCheckResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      if (!response.ok) {
        throw new RaiseLetterServiceError('Health check failed')
      }
      const data = await response.json()
      // Map general health response to expected format
      return {
        status: data.status === 'healthy' ? 'healthy' : 'unhealthy',
        openai_available: data.services?.openai || false,
        model: 'gpt-4',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new RaiseLetterServiceError('Unable to connect to service')
    }
  }

  return {
    generateLetter,
    generateLetterStream,
    checkHealth
  }
}