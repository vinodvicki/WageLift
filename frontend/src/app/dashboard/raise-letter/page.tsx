'use client'

import React, { useState, useEffect } from 'react'
import { RaiseLetterTemplate, RaiseLetterData } from '@/components/templates/raise-letter-template'
import { 
  useRaiseLetterAPI, 
  LetterTone, 
  LetterLength, 
  getLetterToneOptions, 
  getLetterLengthOptions,
  type GenerateLetterRequest,
  type GenerateLetterResponse,
  RaiseLetterAPIError,
  RaiseLetterServiceError,
  cpiDataToLetterRequest
} from '@/lib/api/raise-letter'
import { 
  emailAPI, 
  EmailAPIError, 
  validateEmailAddress,
  type SendRaiseLetterRequest,
  type EmailResponse 
} from '@/lib/api/email'
import { type CPICalculationData } from '@/lib/api/cpi'
import { type SalaryComparisonResponse } from '@/lib/api/benchmark'

// Sample data for template preview
const sampleData: RaiseLetterData = {
  employeeName: 'John Smith',
  employeeTitle: 'Senior Software Engineer',
  employeeEmail: 'john.smith@company.com',
  employeePhone: '(555) 123-4567',
  managerName: 'Sarah Johnson',
  managerTitle: 'Engineering Manager',
  companyName: 'TechCorp Solutions',
  department: 'Engineering Department',
  currentSalary: 85000,
  lastRaiseDate: '2022-03-15',
  requestedSalary: 95000,
  inflationRate: 8.2,
  cpiGapPercentage: 11.8,
  cpiGapAmount: 10000,
  purchasingPowerLoss: 6970,
  achievements: [
    'Led the development of the new customer portal, resulting in 40% increase in user engagement',
    'Mentored 3 junior developers, improving team productivity by 25%',
    'Implemented automated testing framework, reducing bug reports by 60%',
    'Successfully delivered 5 major projects on time and under budget'
  ],
  responsibilities: [
    'Took on additional responsibility for system architecture decisions',
    'Leading cross-functional initiatives with Product and Design teams'
  ],
  letterDate: new Date().toISOString().split('T')[0],
  proposedEffectiveDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
}

// Sample CPI data for AI generation
const sampleCPIData: CPICalculationData = {
  original_salary: 75000,
  current_salary: 85000,
  adjusted_salary: 95000,
  percentage_gap: 11.8,
  dollar_gap: 10000,
  inflation_rate: 8.2,
  years_elapsed: 2,
  calculation_method: 'CPI-U All Items',
  calculation_date: '2024-01-01',
  historical_date: '2022-01-01',
  current_date: '2024-01-01'
}

export default function RaiseLetterPage() {
  const [showTooltips, setShowTooltips] = useState(true)
  const [templateData, setTemplateData] = useState<RaiseLetterData>(sampleData)
  const [showAIGenerator, setShowAIGenerator] = useState(false)
  const [generatedLetter, setGeneratedLetter] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationError, setGenerationError] = useState<string>('')
  const [streamedContent, setStreamedContent] = useState<string>('')
  const [useStreaming, setUseStreaming] = useState(false)

  // Email functionality state
  const [showEmailDialog, setShowEmailDialog] = useState(false)
  const [emailData, setEmailData] = useState({
    manager_email: '',
    manager_name: '',
    subject_line: 'Salary Adjustment Request',
    include_pdf: true,
    cc_user: true,
    custom_message: ''
  })
  const [isSendingEmail, setIsSendingEmail] = useState(false)
  const [emailError, setEmailError] = useState<string>('')
  const [emailSuccess, setEmailSuccess] = useState<EmailResponse | null>(null)
  const [emailConfigValid, setEmailConfigValid] = useState<boolean>(false)

  // AI Generation Form State
  const [formData, setFormData] = useState({
    user_name: 'John Smith',
    job_title: 'Senior Software Engineer',
    company: 'TechCorp Solutions',
    department: 'Engineering' as string | undefined,
    manager_name: 'Sarah Johnson' as string | undefined,
    years_at_company: 3,
    tone: LetterTone.PROFESSIONAL,
    length: LetterLength.STANDARD,
    key_achievements: [
      'Led development of customer portal with 40% engagement increase',
      'Mentored 3 junior developers, improving team productivity by 25%',
      'Implemented automated testing framework, reducing bugs by 60%'
    ],
    recent_projects: [
      'Customer Portal Redesign',
      'Automated Testing Implementation'
    ],
    custom_points: [
      'Took on additional architecture responsibilities',
      'Leading cross-functional initiatives'
    ],
    requested_increase: 95000
  })

  const { generateLetter, generateLetterStream, checkHealth } = useRaiseLetterAPI()

  useEffect(() => {
    // Check AI service health on component mount
    checkHealth().then(health => {
      if (health.status !== 'healthy') {
        setGenerationError('AI service is currently unavailable')
      }
    }).catch(() => {
      setGenerationError('Unable to connect to AI service')
    })

    // Check email configuration
    emailAPI.validateConfiguration().then(config => {
      setEmailConfigValid(config.valid)
    }).catch(() => {
      setEmailConfigValid(false)
    })
  }, [])

  const handleGenerateAILetter = async () => {
    setIsGenerating(true)
    setGenerationError('')
    setGeneratedLetter('')
    setStreamedContent('')

    try {
      const request = cpiDataToLetterRequest(
        sampleCPIData,
        {
          name: formData.user_name,
          job_title: formData.job_title,
          company: formData.company,
          department: formData.department,
          manager_name: formData.manager_name,
          years_at_company: formData.years_at_company
        },
        {
          tone: formData.tone,
          length: formData.length,
          key_achievements: formData.key_achievements.filter((a: string) => a.trim()),
          recent_projects: formData.recent_projects.filter((p: string) => p.trim()),
          custom_points: formData.custom_points.filter((c: string) => c.trim()),
          requested_increase: formData.requested_increase
        }
      )

      if (useStreaming) {
        await generateLetterStream(
          request,
          (chunk) => {
            setStreamedContent((prev: string) => prev + chunk)
          },
          () => {
            setIsGenerating(false)
            setGeneratedLetter(streamedContent)
          },
          (error) => {
            setIsGenerating(false)
            setGenerationError(error.message)
          }
        )
      } else {
        const response = await generateLetter(request)
        setGeneratedLetter(response.letter_content)
        setIsGenerating(false)
      }
    } catch (error) {
      setIsGenerating(false)
      if (error instanceof RaiseLetterServiceError) {
        setGenerationError('AI service is temporarily unavailable. Please try again later.')
      } else if (error instanceof RaiseLetterAPIError) {
        setGenerationError(`Generation failed: ${error.message}`)
      } else {
        setGenerationError('An unexpected error occurred. Please try again.')
      }
    }
  }

  const handleSendEmail = async () => {
    if (!generatedLetter) {
      setEmailError('Please generate a letter first')
      return
    }

    if (!validateEmailAddress(emailData.manager_email)) {
      setEmailError('Please enter a valid manager email address')
      return
    }

    setIsSendingEmail(true)
    setEmailError('')
    setEmailSuccess(null)

    try {
      const emailRequest: SendRaiseLetterRequest = {
        manager_email: emailData.manager_email,
        manager_name: emailData.manager_name || undefined,
        letter_content: generatedLetter,
        subject_line: emailData.subject_line,
        include_pdf: emailData.include_pdf,
        cc_user: emailData.cc_user,
        custom_message: emailData.custom_message || undefined
      }

      const response = await emailAPI.sendRaiseLetter(emailRequest)
      setEmailSuccess(response)
      setShowEmailDialog(false)

      // Reset email form
      setEmailData({
        manager_email: '',
        manager_name: '',
        subject_line: 'Salary Adjustment Request',
        include_pdf: true,
        cc_user: true,
        custom_message: ''
      })
    } catch (error) {
      if (error instanceof EmailAPIError) {
        setEmailError(`Email sending failed: ${error.message}`)
      } else {
        setEmailError('An unexpected error occurred while sending the email')
      }
    } finally {
      setIsSendingEmail(false)
    }
  }

  const handleFormChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }))
  }

  const handleArrayFieldChange = (field: string, index: number, value: string) => {
    setFormData((prev: any) => ({
      ...prev,
      [field]: prev[field as keyof typeof prev].map((item: string, i: number) => 
        i === index ? value : item
      )
    }))
  }

  const addArrayField = (field: string) => {
    setFormData((prev: any) => ({
      ...prev,
      [field]: [...prev[field as keyof typeof prev], '']
    }))
  }

  const removeArrayField = (field: string, index: number) => {
    setFormData((prev: any) => ({
      ...prev,
      [field]: prev[field as keyof typeof prev].filter((_: any, i: number) => i !== index)
    }))
  }

  const handlePrint = () => {
    window.print()
  }

  const handleDownload = () => {
    // Future implementation: Convert to PDF
    alert('PDF download functionality will be implemented in a future update')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Controls */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Raise Request Letter</h1>
              <p className="text-gray-600">Professional salary adjustment request template</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => setShowAIGenerator(!showAIGenerator)}
                className={`inline-flex items-center px-4 py-2 border rounded-md shadow-sm text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                  showAIGenerator 
                    ? 'border-blue-300 text-blue-700 bg-blue-50 hover:bg-blue-100' 
                    : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
                }`}
              >
                🤖 AI Generator
              </button>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={showTooltips}
                  onChange={(e) => setShowTooltips(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Show Tooltips</span>
              </label>
              <button
                onClick={handlePrint}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Print
              </button>
              <button
                onClick={handleDownload}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Download PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* AI Generator Panel */}
      {showAIGenerator && (
        <div className="bg-white border-b shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                🤖 AI-Powered Letter Generation
                <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">GPT-4 Turbo</span>
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* User Information */}
                <div className="space-y-4">
                  <h3 className="font-medium text-gray-900">User Information</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <input
                      type="text"
                      placeholder="Your Name"
                      value={formData.user_name}
                      onChange={(e) => handleFormChange('user_name', e.target.value)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                    <input
                      type="text"
                      placeholder="Job Title"
                      value={formData.job_title}
                      onChange={(e) => handleFormChange('job_title', e.target.value)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                    <input
                      type="text"
                      placeholder="Company Name"
                      value={formData.company}
                      onChange={(e) => handleFormChange('company', e.target.value)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                    <input
                      type="text"
                      placeholder="Manager Name"
                      value={formData.manager_name}
                      onChange={(e) => handleFormChange('manager_name', e.target.value)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                </div>

                {/* Letter Preferences */}
                <div className="space-y-4">
                  <h3 className="font-medium text-gray-900">Letter Preferences</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <select
                      value={formData.tone}
                      onChange={(e) => handleFormChange('tone', e.target.value as LetterTone)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    >
                      {getLetterToneOptions().map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label} - {option.description}
                        </option>
                      ))}
                    </select>
                    <select
                      value={formData.length}
                      onChange={(e) => handleFormChange('length', e.target.value as LetterLength)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    >
                      {getLetterLengthOptions().map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label} - {option.description}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Key Achievements */}
              <div className="mt-6">
                <h3 className="font-medium text-gray-900 mb-2">Key Achievements</h3>
                {formData.key_achievements.map((achievement, index) => (
                  <div key={index} className="flex items-center space-x-2 mb-2">
                    <input
                      type="text"
                      placeholder="Describe a key achievement..."
                      value={achievement}
                      onChange={(e) => handleArrayFieldChange('key_achievements', index, e.target.value)}
                      className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                    <button
                      onClick={() => removeArrayField('key_achievements', index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      ✕
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => addArrayField('key_achievements')}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  + Add Achievement
                </button>
              </div>

              {/* Generation Controls */}
              <div className="mt-6 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={useStreaming}
                      onChange={(e) => setUseStreaming(e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">Real-time streaming</span>
                  </label>
                </div>
                <button
                  onClick={handleGenerateAILetter}
                  disabled={isGenerating}
                  className="inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {isGenerating ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Generating...
                    </>
                  ) : (
                    '🚀 Generate AI Letter'
                  )}
                </button>
              </div>

              {/* Error Display */}
              {generationError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-red-800 text-sm">{generationError}</p>
                </div>
              )}

              {/* Generated Content Preview */}
              {(generatedLetter || streamedContent) && (
                <div className="mt-6">
                  <h3 className="font-medium text-gray-900 mb-2">Generated Letter Preview</h3>
                  <div className="bg-white border rounded-md p-4 max-h-64 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700">
                      {useStreaming ? streamedContent : generatedLetter}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Template Display */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <RaiseLetterTemplate 
            data={templateData} 
            showTooltips={showTooltips}
            className="print:shadow-none"
          />
        </div>

        {/* Template Information */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Template Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium text-gray-900">AI-Powered Generation</h3>
                <p className="text-sm text-gray-600">GPT-4 Turbo creates personalized, professional letters</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium text-gray-900">Data-Driven Analysis</h3>
                <p className="text-sm text-gray-600">Based on official CPI data from Bureau of Labor Statistics</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium text-gray-900">Real-time Streaming</h3>
                <p className="text-sm text-gray-600">Watch your letter generate in real-time</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium text-gray-900">Multiple Tones</h3>
                <p className="text-sm text-gray-600">Professional, confident, collaborative, or assertive</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-2 h-2 bg-red-500 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium text-gray-900">Flexible Length</h3>
                <p className="text-sm text-gray-600">Concise, standard, or detailed letter options</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-2 h-2 bg-indigo-500 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium text-gray-900">Achievement Integration</h3>
                <p className="text-sm text-gray-600">Automatically incorporates your accomplishments</p>
              </div>
            </div>
          </div>
        </div>

        {/* Usage Instructions */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 mb-4">How to Use AI Letter Generation</h2>
          <div className="space-y-3 text-sm text-blue-800">
            <p><strong>1. Configure Settings:</strong> Fill in your personal information and select your preferred tone and length.</p>
            <p><strong>2. Add Achievements:</strong> List your key accomplishments and recent projects to strengthen your case.</p>
            <p><strong>3. Generate Letter:</strong> Click "Generate AI Letter" and watch as GPT-4 Turbo creates your personalized request.</p>
            <p><strong>4. Review & Edit:</strong> Review the generated content and make any necessary adjustments.</p>
            <p><strong>5. Professional Delivery:</strong> Print or save as PDF for formal submission to your manager.</p>
          </div>
        </div>
      </div>

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          .no-print {
            display: none !important;
          }
          
          body {
            background: white !important;
          }
          
          .print\\:shadow-none {
            box-shadow: none !important;
          }
          
          .bg-gray-50 {
            background: white !important;
          }
        }
      `}</style>
    </div>
  )
} 