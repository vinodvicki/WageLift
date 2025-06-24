/**
 * Email API Module
 * Mock implementation for development
 */

export class EmailAPIError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message)
    this.name = 'EmailAPIError'
  }
}

export interface EmailData {
  to: string
  subject: string
  content: string
  attachments?: Array<{
    filename: string
    content: string
    contentType: string
  }>
}

export interface EmailResponse {
  id: string
  status: 'sent' | 'pending' | 'failed'
  timestamp: string
}

/**
 * Validate email address format
 */
export function validateEmailAddress(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Mock email API
 */
export const emailAPI = {
  async sendEmail(data: EmailData): Promise<EmailResponse> {
    // Validate email
    if (!validateEmailAddress(data.to)) {
      throw new EmailAPIError('Invalid email address', 400)
    }

    // Mock delay
    await new Promise(resolve => setTimeout(resolve, 500))

    // Mock response
    return {
      id: `email_${Date.now()}`,
      status: 'sent',
      timestamp: new Date().toISOString()
    }
  },

  async getEmailStatus(emailId: string): Promise<EmailResponse> {
    // Mock delay
    await new Promise(resolve => setTimeout(resolve, 200))

    return {
      id: emailId,
      status: 'sent',
      timestamp: new Date().toISOString()
    }
  }
}