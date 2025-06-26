// Types for email functionality
export interface SendRaiseLetterRequest {
  manager_email: string
  manager_name?: string
  letter_content: string
  subject_line: string
  include_pdf?: boolean
  cc_user?: boolean
  custom_message?: string
}

export interface EmailResponse {
  success: boolean
  message_id: string
  timestamp: string
  details: {
    to: string
    cc?: string[]
    subject: string
    pdf_attached: boolean
  }
}

export interface EmailConfigResponse {
  valid: boolean
  provider: string
  features: {
    pdf_generation: boolean
    cc_support: boolean
    tracking: boolean
  }
}

// Error classes
export class EmailAPIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message)
    this.name = 'EmailAPIError'
  }
}

// Utility functions
export function validateEmailAddress(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// API client
const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8001'

class EmailAPI {
  async sendRaiseLetter(request: SendRaiseLetterRequest): Promise<EmailResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/email/send-raise-letter`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new EmailAPIError(
          error.detail || `Failed to send email: ${response.statusText}`,
          response.status
        )
      }

      return await response.json()
    } catch (error) {
      if (error instanceof EmailAPIError) throw error
      throw new EmailAPIError('Unable to connect to email service', 503)
    }
  }

  async validateConfiguration(): Promise<EmailConfigResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/email/config`)
      
      if (!response.ok) {
        throw new EmailAPIError('Failed to validate email configuration', response.status)
      }

      return await response.json()
    } catch (error) {
      if (error instanceof EmailAPIError) throw error
      throw new EmailAPIError('Unable to connect to email service', 503)
    }
  }

  async testEmail(to: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/email/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ to })
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new EmailAPIError(
          error.detail || 'Failed to send test email',
          response.status
        )
      }

      return await response.json()
    } catch (error) {
      if (error instanceof EmailAPIError) throw error
      throw new EmailAPIError('Unable to connect to email service', 503)
    }
  }
}

export const emailAPI = new EmailAPI()