/**
 * Editor API client for WageLift frontend.
 * Handles raise letter document management with full CRUD operations.
 */

import { getAccessToken } from '@auth0/nextjs-auth0'

// API Configuration
const API_BASE_URL = typeof window !== 'undefined' 
  ? (window as any).ENV?.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  : 'http://localhost:8000';

// Types matching backend models
export interface RaiseLetterMetadata {
  employee_name: string
  employee_title: string
  company_name: string
  manager_name: string
  last_modified: string
  created_at: string
  version: number
}

export interface RaiseLetterData {
  id?: string
  title: string
  content: string
  metadata: RaiseLetterMetadata
  user_id?: string
  is_active?: boolean
}

export interface RaiseLetterListItem {
  id: string
  title: string
  last_modified: string
  created_at: string
  version: number
  is_active: boolean
}

export interface RaiseLetterVersion {
  id: string
  document_id: string
  version_number: number
  title: string
  content: string
  created_at: string
  change_summary?: string
}

export interface SaveResponse {
  id: string
  version: number
  message: string
  saved_at: string
}

export interface DuplicateResponse {
  id: string
  title: string
  message: string
}

// Email send types
export interface EmailSendRequest {
  recipient_email: string
  recipient_name?: string
  subject?: string
  include_pdf?: boolean
  cc_sender?: boolean
  custom_message?: string
}

export interface EmailSendResponse {
  success: boolean
  message: string
  message_id?: string
  sent_at: string
  recipients: string[]
}

// Custom error classes
export class EditorAPIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message)
    this.name = 'EditorAPIError'
  }
}

export class EditorServiceError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'EditorServiceError'
  }
}

// Helper function to make authenticated requests
async function makeRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const { accessToken } = await getAccessToken()
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        ...options.headers,
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`
      
      try {
        const errorData = JSON.parse(errorText)
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        // Use default error message if JSON parsing fails
      }
      
      throw new EditorAPIError(
        errorMessage,
        response.status,
        errorText
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof EditorAPIError) {
      throw error
    }
    throw new EditorServiceError(
      `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
    )
  }
}

/**
 * Save a raise letter document
 */
export async function saveRaiseLetter(
  letterData: Omit<RaiseLetterData, 'id' | 'user_id' | 'is_active'>
): Promise<SaveResponse> {
  return makeRequest<SaveResponse>('/api/v1/editor/save', {
    method: 'POST',
    body: JSON.stringify(letterData),
  })
}

/**
 * Get list of user's documents
 */
export async function getUserDocuments(
  limit: number = 50,
  offset: number = 0
): Promise<RaiseLetterListItem[]> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  })
  
  return makeRequest<RaiseLetterListItem[]>(`/api/v1/editor/documents?${params}`)
}

/**
 * Get a specific document by ID
 */
export async function getDocument(documentId: string): Promise<RaiseLetterData> {
  return makeRequest<RaiseLetterData>(`/api/v1/editor/documents/${documentId}`)
}

/**
 * Get version history for a document
 */
export async function getDocumentVersions(documentId: string): Promise<RaiseLetterVersion[]> {
  return makeRequest<RaiseLetterVersion[]>(`/api/v1/editor/documents/${documentId}/versions`)
}

/**
 * Delete a document (soft delete)
 */
export async function deleteDocument(documentId: string): Promise<{ message: string }> {
  return makeRequest<{ message: string }>(`/api/v1/editor/documents/${documentId}`, {
    method: 'DELETE',
  })
}

/**
 * Duplicate a document
 */
export async function duplicateDocument(documentId: string): Promise<DuplicateResponse> {
  return makeRequest<DuplicateResponse>(`/api/v1/editor/documents/${documentId}/duplicate`, {
    method: 'POST',
  })
}

/**
 * Send a document via email with optional PDF attachment
 */
export async function sendDocument(
  documentId: string,
  emailRequest: EmailSendRequest
): Promise<EmailSendResponse> {
  return makeRequest<EmailSendResponse>(`/api/v1/editor/documents/${documentId}/send`, {
    method: 'POST',
    body: JSON.stringify(emailRequest),
  })
}

/**
 * Check editor service health
 */
export async function checkEditorHealth(): Promise<{
  status: string
  service: string
  timestamp: string
  version: string
}> {
  return makeRequest('/api/v1/editor/health')
}

// Utility functions for working with editor data

/**
 * Create metadata object from form data
 */
export function createMetadata(
  employeeName: string,
  employeeTitle: string,
  companyName: string,
  managerName: string
): RaiseLetterMetadata {
  const now = new Date().toISOString()
  return {
    employee_name: employeeName,
    employee_title: employeeTitle,
    company_name: companyName,
    manager_name: managerName,
    last_modified: now,
    created_at: now,
    version: 1
  }
}

/**
 * Convert AI-generated letter to editor format
 */
export function convertAILetterToEditorData(
  aiLetterContent: string,
  title: string,
  metadata: RaiseLetterMetadata
): Omit<RaiseLetterData, 'id' | 'user_id' | 'is_active'> {
  return {
    title,
    content: aiLetterContent,
    metadata: {
      ...metadata,
      last_modified: new Date().toISOString(),
      version: metadata.version + 1
    }
  }
}

/**
 * Format date for display
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Get document status based on last modified date
 */
export function getDocumentStatus(lastModified: string): {
  status: 'recent' | 'stale' | 'old'
  description: string
  color: string
} {
  const now = new Date()
  const modified = new Date(lastModified)
  const hoursDiff = (now.getTime() - modified.getTime()) / (1000 * 60 * 60)

  if (hoursDiff < 24) {
    return {
      status: 'recent',
      description: 'Recently modified',
      color: 'text-green-600'
    }
  } else if (hoursDiff < 168) { // 7 days
    return {
      status: 'stale',
      description: 'Modified this week',
      color: 'text-yellow-600'
    }
  } else {
    return {
      status: 'old',
      description: 'Older document',
      color: 'text-gray-600'
    }
  }
}

/**
 * Validate document data before saving
 */
export function validateDocumentData(data: Omit<RaiseLetterData, 'id' | 'user_id' | 'is_active'>): string[] {
  const errors: string[] = []

  if (!data.title || data.title.trim().length === 0) {
    errors.push('Document title is required')
  }

  if (data.title && data.title.length > 255) {
    errors.push('Document title must be less than 255 characters')
  }

  if (!data.content || data.content.trim().length === 0) {
    errors.push('Document content is required')
  }

  if (!data.metadata.employee_name || data.metadata.employee_name.trim().length === 0) {
    errors.push('Employee name is required')
  }

  if (!data.metadata.company_name || data.metadata.company_name.trim().length === 0) {
    errors.push('Company name is required')
  }

  return errors
}

/**
 * Clean HTML content for safe storage
 */
export function cleanHTMLContent(content: string): string {
  // Remove potentially dangerous HTML elements and attributes
  // This is a basic implementation - in production, consider using a library like DOMPurify
  return content
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/on\w+="[^"]*"/gi, '') // Remove event handlers
    .replace(/javascript:/gi, '') // Remove javascript: URLs
}

/**
 * Extract plain text from HTML content for search/preview
 */
export function extractPlainText(htmlContent: string, maxLength: number = 200): string {
  // Create a temporary DOM element to strip HTML tags
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = htmlContent
  const plainText = tempDiv.textContent || tempDiv.innerText || ''
  
  if (plainText.length <= maxLength) {
    return plainText
  }
  
  return plainText.substring(0, maxLength).trim() + '...'
}

/**
 * React hook for editor API operations
 */
export function useEditorAPI() {
  const save = async (data: Omit<RaiseLetterData, 'id' | 'user_id' | 'is_active'>) => {
    const errors = validateDocumentData(data)
    if (errors.length > 0) {
      throw new EditorAPIError(`Validation failed: ${errors.join(', ')}`)
    }

    const cleanedData = {
      ...data,
      content: cleanHTMLContent(data.content)
    }

    return saveRaiseLetter(cleanedData)
  }

  const load = async (documentId: string) => {
    return getDocument(documentId)
  }

  const list = async (limit?: number, offset?: number) => {
    return getUserDocuments(limit, offset)
  }

  const remove = async (documentId: string) => {
    return deleteDocument(documentId)
  }

  const duplicate = async (documentId: string) => {
    return duplicateDocument(documentId)
  }

  const versions = async (documentId: string) => {
    return getDocumentVersions(documentId)
  }

  const health = async () => {
    return checkEditorHealth()
  }

  const send = async (documentId: string, emailRequest: EmailSendRequest) => {
    return sendDocument(documentId, emailRequest)
  }

  return {
    save,
    load,
    list,
    remove,
    duplicate,
    versions,
    health,
    send
  }
}

// Error handling utilities
export function isEditorAPIError(error: unknown): error is EditorAPIError {
  return error instanceof EditorAPIError
}

export function isEditorServiceError(error: unknown): error is EditorServiceError {
  return error instanceof EditorServiceError
}

export function handleEditorError(error: unknown): string {
  if (isEditorAPIError(error)) {
    return error.message
  }
  
  if (isEditorServiceError(error)) {
    return error.message
  }
  
  return 'An unexpected error occurred while managing your document'
} 