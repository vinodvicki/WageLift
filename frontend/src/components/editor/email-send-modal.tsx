"use client"

import React, { useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { EmailSendRequest, EmailSendResponse, sendDocument } from '@/lib/api/editor'

const emailSchema = z.object({
  recipientEmail: z.string().email('Please enter a valid email address'),
  recipientName: z.string().optional(),
  subject: z.string().min(1, 'Subject is required'),
  customMessage: z.string().optional(),
  includePdf: z.boolean().default(true),
  ccSender: z.boolean().default(false),
})

type EmailFormData = z.infer<typeof emailSchema>

interface EmailSendModalProps {
  documentId: string
  documentTitle: string
  trigger: React.ReactNode
  onSuccess?: (response: EmailSendResponse) => void
  onError?: (error: string) => void
}

export function EmailSendModal({
  documentId,
  documentTitle,
  trigger,
  onSuccess,
  onError,
}: EmailSendModalProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<EmailFormData>({
    resolver: zodResolver(emailSchema),
    defaultValues: {
      subject: `Salary Review Request - ${documentTitle}`,
      includePdf: true,
      ccSender: false,
    },
  })

  const onSubmit = async (data: EmailFormData) => {
    setIsLoading(true)
    try {
      const emailRequest: EmailSendRequest = {
        recipient_email: data.recipientEmail,
        ...(data.recipientName && { recipient_name: data.recipientName }),
        subject: data.subject,
        ...(data.customMessage && { custom_message: data.customMessage }),
        include_pdf: data.includePdf,
        cc_sender: data.ccSender,
      }

      const response = await sendDocument(documentId, emailRequest)
      
      if (response.success) {
        onSuccess?.(response)
        setIsOpen(false)
        reset()
      } else {
        onError?.(response.message || 'Failed to send email')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      onError?.(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={setIsOpen}>
      <Dialog.Trigger asChild>
        {trigger}
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black bg-opacity-50" />
        <Dialog.Content className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-xl w-full max-w-md p-6">
          <Dialog.Title className="text-lg font-semibold text-gray-900 mb-4">
            Send Raise Letter
          </Dialog.Title>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="recipientEmail" className="block text-sm font-medium text-gray-700">
                Recipient Email *
              </label>
              <input
                {...register('recipientEmail')}
                type="email"
                id="recipientEmail"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="manager@company.com"
              />
              {errors.recipientEmail && (
                <p className="mt-1 text-sm text-red-600">{errors.recipientEmail.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="recipientName" className="block text-sm font-medium text-gray-700">
                Recipient Name
              </label>
              <input
                {...register('recipientName')}
                type="text"
                id="recipientName"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="Manager Name"
              />
            </div>

            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-gray-700">
                Subject *
              </label>
              <input
                {...register('subject')}
                type="text"
                id="subject"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              {errors.subject && (
                <p className="mt-1 text-sm text-red-600">{errors.subject.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="customMessage" className="block text-sm font-medium text-gray-700">
                Custom Message
              </label>
              <textarea
                {...register('customMessage')}
                id="customMessage"
                rows={3}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="Add a personal message (optional)"
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center">
                <input
                  {...register('includePdf')}
                  type="checkbox"
                  id="includePdf"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="includePdf" className="ml-2 block text-sm text-gray-900">
                  Include PDF attachment
                </label>
              </div>

              <div className="flex items-center">
                <input
                  {...register('ccSender')}
                  type="checkbox"
                  id="ccSender"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="ccSender" className="ml-2 block text-sm text-gray-900">
                  Send copy to myself
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4">
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Sending...' : 'Send Email'}
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
