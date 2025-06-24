/**
 * Email API Client for WageLift
 * Handles email sending operations for raise request letters
 */

import { getAccessToken } from '@auth0/nextjs-auth0';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface SendRaiseLetterRequest {
  manager_email: string;
  manager_name?: string;
  letter_content: string;
  subject_line: string;
  include_pdf?: boolean;
  cc_user?: boolean;
  custom_message?: string;
}

export interface EmailResponse {
  success: boolean;
  message_id?: string;
  error_message?: string;
  sent_at: string;
  provider_used: string;
  recipients_count: number;
  metadata: Record<string, any>;
}

export interface EmailConfigurationStatus {
  valid: boolean;
  provider: string;
  sender_configured: boolean;
  smtp_configured: boolean;
  message: string;
}

export interface EmailPreviewResponse {
  html_content: string;
  text_content: string;
  subject: string;
  recipients: {
    to: Array<{ email: string; name?: string }>;
    cc: Array<{ email: string; name?: string }>;
  };
}

export interface EmailHistoryItem {
  id: string;
  recipient_email: string;
  recipient_name?: string;
  subject: string;
  sent_at: string;
  status: string;
  provider_used: string;
  has_attachment: boolean;
  metadata: Record<string, any>;
}

export interface EmailHistoryResponse {
  items: EmailHistoryItem[];
  total_count: number;
  page: number;
  page_size: number;
}

export class EmailAPIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'EmailAPIError';
  }
}

class EmailAPI {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}/email`;
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    try {
      const { accessToken } = await getAccessToken();
      return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      };
    } catch (error) {
      console.warn('Failed to get access token, proceeding without auth');
      return {
        'Content-Type': 'application/json',
      };
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new EmailAPIError(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }
    return response.json();
  }

  /**
   * Send a raise request letter via email
   */
  async sendRaiseLetter(request: SendRaiseLetterRequest): Promise<EmailResponse> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${this.baseUrl}/send-raise-letter`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });

      return this.handleResponse<EmailResponse>(response);
    } catch (error) {
      if (error instanceof EmailAPIError) {
        throw error;
      }
      throw new EmailAPIError(`Failed to send raise letter: ${error}`);
    }
  }

  /**
   * Send a test email to verify configuration
   */
  async sendTestEmail(recipientEmail: string): Promise<EmailResponse> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${this.baseUrl}/send-test-email?recipient_email=${encodeURIComponent(recipientEmail)}`, {
        method: 'POST',
        headers,
      });

      return this.handleResponse<EmailResponse>(response);
    } catch (error) {
      if (error instanceof EmailAPIError) {
        throw error;
      }
      throw new EmailAPIError(`Failed to send test email: ${error}`);
    }
  }

  /**
   * Validate email service configuration
   */
  async validateConfiguration(): Promise<EmailConfigurationStatus> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${this.baseUrl}/configuration/validate`, {
        method: 'GET',
        headers,
      });

      return this.handleResponse<EmailConfigurationStatus>(response);
    } catch (error) {
      if (error instanceof EmailAPIError) {
        throw error;
      }
      throw new EmailAPIError(`Failed to validate configuration: ${error}`);
    }
  }

  /**
   * Preview email content without sending
   */
  async previewEmail(request: SendRaiseLetterRequest): Promise<EmailPreviewResponse> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${this.baseUrl}/preview-email`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });

      return this.handleResponse<EmailPreviewResponse>(response);
    } catch (error) {
      if (error instanceof EmailAPIError) {
        throw error;
      }
      throw new EmailAPIError(`Failed to preview email: ${error}`);
    }
  }

  /**
   * Get email sending history
   */
  async getEmailHistory(page: number = 1, pageSize: number = 20): Promise<EmailHistoryResponse> {
    try {
      const headers = await this.getAuthHeaders();
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });

      const response = await fetch(`${this.baseUrl}/history?${params}`, {
        method: 'GET',
        headers,
      });

      return this.handleResponse<EmailHistoryResponse>(response);
    } catch (error) {
      if (error instanceof EmailAPIError) {
        throw error;
      }
      throw new EmailAPIError(`Failed to get email history: ${error}`);
    }
  }

  /**
   * Check email service health
   */
  async checkHealth(): Promise<{
    status: string;
    provider: string;
    configured: boolean;
    timestamp: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      return this.handleResponse(response);
    } catch (error) {
      if (error instanceof EmailAPIError) {
        throw error;
      }
      throw new EmailAPIError(`Failed to check health: ${error}`);
    }
  }
}

// Export singleton instance
export const emailAPI = new EmailAPI();

// Export utility functions
export const formatEmailDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const validateEmailAddress = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const sanitizeFileName = (fileName: string): string => {
  return fileName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
}; 