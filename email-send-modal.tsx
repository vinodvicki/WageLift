"use client"

import React, { useState } from 'react'
import { X, Mail, Paperclip, User, MessageSquare } from 'lucide-react'
import { EmailSendRequest, EmailSendResponse } from '@/lib/api/editor'

interface EmailSendModalProps {
  isOpen: boolean
  onClose: () => void
  onSend: (emailRequest: EmailSendRequest) => Promise<EmailSendResponse>
  documentTitle: string
  employeeName: string
  isLoading?: boolean
}

export function EmailSendModal({
  isOpen,
  onClose,
  onSend,
  documentTitle,
  employeeName,
  isLoading = false
}: EmailSendModalProps) {
  const [formData, setFormData] = useState<EmailSendRequest>({
    recipient_email: '',
    recipient_name: '',
    subject: `Salary Review Request - ${employeeName}`,
    include_pdf: true,
    cc_sender: true,
    custom_message: ''
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [sendStatus, setSendStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle')
  const [sendMessage, setSendMessage] = useState('')

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.recipient_email) {
      newErrors.recipient_email = 'Recipient email is required'
    } else if (!validateEmail(formData.recipient_email)) {
      newErrors.recipient_email = 'Please enter a valid email address'
    }

    if (!formData.subject?.trim()) {
      newErrors.subject = 'Subject is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setSendStatus('sending')
    setSendMessage('')

    try {
      const response = await onSend(formData)
      setSendStatus('success')
      setSendMessage(response.message)
      
      // Auto-close after success
      setTimeout(() => {
        onClose()
        setSendStatus('idle')
        setSendMessage('')
      }, 2000)
    } catch (error) {
      setSendStatus('error')
      setSendMessage(error instanceof Error ? error.message : 'Failed to send email')
    }
  }

  const handleInputChange = (field: keyof EmailSendRequest, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const handleClose = () => {
    if (sendStatus !== 'sending') {
      onClose()
      setSendStatus('idle')
      setSendMessage('')
      setErrors({})
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <Mail className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Send Document</h2>
          </div>
          <button
            onClick={handleClose}
            disabled={sendStatus === 'sending'}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              <strong>Document:</strong> {documentTitle}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Recipient Email */}
            <div>
              <label htmlFor="recipient_email" className="block text-sm font-medium text-gray-700 mb-1">
                Recipient Email *
              </label>
              <input
                type="email"
                id="recipient_email"
                value={formData.recipient_email}
                onChange={(e) => handleInputChange('recipient_email', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.recipient_email ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="manager@company.com"
                disabled={sendStatus === 'sending'}
              />
              {errors.recipient_email && (
                <p className="mt-1 text-sm text-red-600">{errors.recipient_email}</p>
              )}
            </div>

            {/* Recipient Name */}
            <div>
              <label htmlFor="recipient_name" className="block text-sm font-medium text-gray-700 mb-1">
                Recipient Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  id="recipient_name"
                  value={formData.recipient_name || ''}
                  onChange={(e) => handleInputChange('recipient_name', e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Manager Name"
                  disabled={sendStatus === 'sending'}
                />
              </div>
            </div>

            {/* Subject */}
            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
                Subject *
              </label>
              <input
                type="text"
                id="subject"
                value={formData.subject || ''}
                onChange={(e) => handleInputChange('subject', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.subject ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Salary Review Request"
                disabled={sendStatus === 'sending'}
              />
              {errors.subject && (
                <p className="mt-1 text-sm text-red-600">{errors.subject}</p>
              )}
            </div>

            {/* Custom Message */}
            <div>
              <label htmlFor="custom_message" className="block text-sm font-medium text-gray-700 mb-1">
                Additional Message
              </label>
              <div className="relative">
                <MessageSquare className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <textarea
                  id="custom_message"
                  value={formData.custom_message || ''}
                  onChange={(e) => handleInputChange('custom_message', e.target.value)}
                  rows={3}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Optional message to include with your request..."
                  disabled={sendStatus === 'sending'}
                />
              </div>
            </div>

            {/* Options */}
            <div className="space-y-3">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="include_pdf"
                  checked={formData.include_pdf}
                  onChange={(e) => handleInputChange('include_pdf', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  disabled={sendStatus === 'sending'}
                />
                <label htmlFor="include_pdf" className="ml-2 flex items-center text-sm text-gray-700">
                  <Paperclip className="h-4 w-4 mr-1" />
                  Include PDF attachment
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="cc_sender"
                  checked={formData.cc_sender}
                  onChange={(e) => handleInputChange('cc_sender', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  disabled={sendStatus === 'sending'}
                />
                <label htmlFor="cc_sender" className="ml-2 text-sm text-gray-700">
                  Send me a copy (CC)
                </label>
              </div>
            </div>

            {/* Status Messages */}
            {sendMessage && (
              <div className={`p-3 rounded-md ${
                sendStatus === 'success' 
                  ? 'bg-green-50 text-green-800 border border-green-200' 
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}>
                <p className="text-sm">{sendMessage}</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                disabled={sendStatus === 'sending'}
                className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={sendStatus === 'sending' || sendStatus === 'success'}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {sendStatus === 'sending' ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Sending...
                  </span>
                ) : sendStatus === 'success' ? (
                  '✓ Sent!'
                ) : (
                  'Send Email'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
} 