'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import RaiseLetterEditor, { RaiseLetterEditorData } from '@/components/editor/raise-letter-editor'
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
  useEditorAPI,
  type RaiseLetterData,
  type RaiseLetterListItem,
  createMetadata,
  convertAILetterToEditorData,
  formatDate,
  getDocumentStatus,
  EditorAPIError,
  EditorServiceError
} from '@/lib/api/editor'
import { useCPIApi, type CPICalculationData } from '@/lib/api/cpi'
import { compareSalary, type SalaryComparisonResponse } from '@/lib/api/benchmark'
import { 
  FileText, 
  Plus, 
  Save, 
  Folder, 
  Clock, 
  User, 
  Building,
  Sparkles,
  RefreshCw,
  Trash2,
  Copy,
  Eye,
  AlertCircle,
  CheckCircle2,
  Settings
} from 'lucide-react'

// Types for the enhanced page
interface UserFormData {
  name: string
  job_title: string
  company: string
  department?: string
  manager_name?: string
  years_at_company: number
  current_salary: number
  location: string
  last_raise_date?: string
}

interface AIGenerationData {
  tone: LetterTone
  length: LetterLength
  key_achievements: string[]
  recent_projects: string[]
  custom_points: string[]
  requested_increase: number
}

export default function EnhancedRaiseLetterPage() {
  const router = useRouter()
  
  // API hooks
  const { generateLetter, generateLetterStream, checkHealth: checkAIHealth } = useRaiseLetterAPI()
  const { save, load, list, remove, duplicate } = useEditorAPI()
  const { calculateSalaryGap } = useCPIApi()

  // State management
  const [currentView, setCurrentView] = useState<'documents' | 'editor' | 'generator'>('documents')
  const [currentDocument, setCurrentDocument] = useState<RaiseLetterEditorData | null>(null)
  const [userDocuments, setUserDocuments] = useState<RaiseLetterListItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState<string>('')

  // User data and AI generation
  const [userFormData, setUserFormData] = useState<UserFormData>({
    name: '',
    job_title: '',
    company: '',
    department: '',
    manager_name: '',
    years_at_company: 2,
    current_salary: 75000,
    location: '',
    last_raise_date: ''
  })

  const [aiGenerationData, setAIGenerationData] = useState<AIGenerationData>({
    tone: LetterTone.PROFESSIONAL,
    length: LetterLength.STANDARD,
    key_achievements: [''],
    recent_projects: [''],
    custom_points: [''],
    requested_increase: 85000
  })

  // CPI and benchmark data
  const [cpiData, setCpiData] = useState<CPICalculationData | null>(null)
  const [benchmarkData, setBenchmarkData] = useState<SalaryComparisonResponse | null>(null)
  const [isGeneratingAI, setIsGeneratingAI] = useState(false)
  const [generatedContent, setGeneratedContent] = useState<string>('')

  // Load user documents on component mount
  useEffect(() => {
    loadUserDocuments()
  }, [])

  // Load CPI and benchmark data when user data changes
  useEffect(() => {
    if (userFormData.current_salary && userFormData.last_raise_date) {
      loadCPIData()
    }
    if (userFormData.job_title && userFormData.location) {
      loadBenchmarkData()
    }
  }, [userFormData.current_salary, userFormData.last_raise_date, userFormData.job_title, userFormData.location])

  const loadUserDocuments = async () => {
    try {
      setIsLoading(true)
      const documents = await list(50, 0)
      setUserDocuments(documents)
    } catch (error) {
      setError('Failed to load documents')
      console.error('Error loading documents:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadCPIData = async () => {
    if (!userFormData.last_raise_date || !userFormData.current_salary) return

    try {
      const response = await calculateSalaryGap({
        original_salary: userFormData.current_salary,
        current_salary: userFormData.current_salary,
        historical_date: userFormData.last_raise_date,
        current_date: new Date().toISOString().split('T')[0]
      })
      setCpiData(response.data)
    } catch (error) {
      console.error('Error loading CPI data:', error)
    }
  }

  const loadBenchmarkData = async () => {
    if (!userFormData.job_title || !userFormData.location || !userFormData.current_salary) return

    try {
      const response = await compareSalary({
        current_salary: userFormData.current_salary,
        job_title: userFormData.job_title,
        location: userFormData.location
      })
      setBenchmarkData(response)
    } catch (error) {
      console.error('Error loading benchmark data:', error)
    }
  }

  const handleGenerateAILetter = async () => {
    if (!cpiData) {
      setError('Please provide salary history for CPI analysis')
      return
    }

    setIsGeneratingAI(true)
    setError('')

    try {
      const request = cpiDataToLetterRequest(
        cpiData,
        {
          name: userFormData.name,
          job_title: userFormData.job_title,
          company: userFormData.company,
          department: userFormData.department,
          manager_name: userFormData.manager_name,
          years_at_company: userFormData.years_at_company
        },
        {
          tone: aiGenerationData.tone,
          length: aiGenerationData.length,
          key_achievements: aiGenerationData.key_achievements.filter(a => a.trim()),
          recent_projects: aiGenerationData.recent_projects.filter(p => p.trim()),
          custom_points: aiGenerationData.custom_points.filter(c => c.trim()),
          requested_increase: aiGenerationData.requested_increase
        },
        benchmarkData
      )

      const response = await generateLetter(request)
      setGeneratedContent(response.letter_content)
      
      // Create editor data from generated content
      const metadata = createMetadata(
        userFormData.name,
        userFormData.job_title,
        userFormData.company,
        userFormData.manager_name || ''
      )

      const editorData: RaiseLetterEditorData = {
        title: 'AI-Generated Salary Adjustment Request',
        content: response.letter_content,
        metadata: {
          employeeName: metadata.employee_name,
          employeeTitle: metadata.employee_title,
          companyName: metadata.company_name,
          managerName: metadata.manager_name,
          lastModified: metadata.last_modified,
          createdAt: metadata.created_at,
          version: metadata.version
        }
      }

      setCurrentDocument(editorData)
      setCurrentView('editor')
      setSuccess('AI letter generated successfully!')

    } catch (error) {
      if (error instanceof RaiseLetterServiceError) {
        setError('AI service is temporarily unavailable. Please try again later.')
      } else if (error instanceof RaiseLetterAPIError) {
        setError(`Generation failed: ${error.message}`)
      } else {
        setError('An unexpected error occurred. Please try again.')
      }
    } finally {
      setIsGeneratingAI(false)
    }
  }

  const handleSaveDocument = async (data: RaiseLetterEditorData) => {
    try {
      const saveData = convertAILetterToEditorData(
        data.content,
        data.title,
        {
          employee_name: data.metadata.employeeName,
          employee_title: data.metadata.employeeTitle,
          company_name: data.metadata.companyName,
          manager_name: data.metadata.managerName,
          last_modified: new Date().toISOString(),
          created_at: data.metadata.createdAt,
          version: data.metadata.version
        }
      )

      const response = await save(saveData)
      setSuccess(`Document saved successfully (Version ${response.version})`)
      await loadUserDocuments() // Refresh document list
    } catch (error) {
      if (error instanceof EditorAPIError) {
        throw new Error(`Save failed: ${error.message}`)
      } else {
        throw new Error('Failed to save document')
      }
    }
  }

  const handleLoadDocument = async (documentId: string) => {
    try {
      setIsLoading(true)
      const document = await load(documentId)
      
      const editorData: RaiseLetterEditorData = {
        id: document.id,
        title: document.title,
        content: document.content,
        metadata: {
          employeeName: document.metadata.employee_name,
          employeeTitle: document.metadata.employee_title,
          companyName: document.metadata.company_name,
          managerName: document.metadata.manager_name,
          lastModified: document.metadata.last_modified,
          createdAt: document.metadata.created_at,
          version: document.metadata.version
        }
      }

      setCurrentDocument(editorData)
      setCurrentView('editor')
    } catch (error) {
      setError('Failed to load document')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      await remove(documentId)
      setSuccess('Document deleted successfully')
      await loadUserDocuments()
    } catch (error) {
      setError('Failed to delete document')
    }
  }

  const handleDuplicateDocument = async (documentId: string) => {
    try {
      const response = await duplicate(documentId)
      setSuccess(`Document duplicated: ${response.title}`)
      await loadUserDocuments()
    } catch (error) {
      setError('Failed to duplicate document')
    }
  }

  const handleCreateNewDocument = () => {
    const metadata = createMetadata(
      userFormData.name || 'Your Name',
      userFormData.job_title || 'Your Title',
      userFormData.company || 'Your Company',
      userFormData.manager_name || 'Manager Name'
    )

    const newDocument: RaiseLetterEditorData = {
      title: 'New Salary Adjustment Request',
      content: '<p>Start writing your raise request letter...</p>',
      metadata: {
        employeeName: metadata.employee_name,
        employeeTitle: metadata.employee_title,
        companyName: metadata.company_name,
        managerName: metadata.manager_name,
        lastModified: metadata.last_modified,
        createdAt: metadata.created_at,
        version: metadata.version
      }
    }

    setCurrentDocument(newDocument)
    setCurrentView('editor')
  }

  const DocumentsList = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Your Raise Request Letters</h2>
        <div className="flex space-x-3">
          <button
            onClick={() => setCurrentView('generator')}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            AI Generator
          </button>
          <button
            onClick={handleCreateNewDocument}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Document
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Loading documents...</span>
        </div>
      ) : userDocuments.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
          <p className="text-gray-600 mb-6">Get started by creating your first raise request letter</p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setCurrentView('generator')}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Use AI Generator
            </button>
            <button
              onClick={handleCreateNewDocument}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Plus className="h-4 w-4 mr-2" />
              Start from Scratch
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {userDocuments.map((doc) => {
            const status = getDocumentStatus(doc.last_modified)
            return (
              <div key={doc.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900 truncate">{doc.title}</h3>
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => handleLoadDocument(doc.id)}
                        className="text-gray-400 hover:text-blue-600"
                        title="Open document"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDuplicateDocument(doc.id)}
                        className="text-gray-400 hover:text-green-600"
                        title="Duplicate document"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="text-gray-400 hover:text-red-600"
                        title="Delete document"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-2" />
                      <span>Modified {formatDate(doc.last_modified)}</span>
                    </div>
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 mr-2" />
                      <span>Version {doc.version}</span>
                    </div>
                    <div className={`flex items-center ${status.color}`}>
                      <div className="h-2 w-2 rounded-full bg-current mr-2" />
                      <span>{status.description}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleLoadDocument(doc.id)}
                    className="mt-4 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Open Document
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Raise Request Letters</h1>
              <p className="text-gray-600">Create, edit, and manage your salary adjustment requests</p>
            </div>
            
            <div className="flex items-center space-x-4">
              {currentView !== 'documents' && (
                <button
                  onClick={() => {
                    setCurrentView('documents')
                    setCurrentDocument(null)
                  }}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <Folder className="h-4 w-4 mr-2" />
                  My Documents
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-red-800">{error}</p>
              </div>
              <button
                onClick={() => setError('')}
                className="ml-auto text-red-400 hover:text-red-600"
              >
                ×
              </button>
            </div>
          </div>
        </div>
      )}

      {success && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex">
              <CheckCircle2 className="h-5 w-5 text-green-400" />
              <div className="ml-3">
                <p className="text-green-800">{success}</p>
              </div>
              <button
                onClick={() => setSuccess('')}
                className="ml-auto text-green-400 hover:text-green-600"
              >
                ×
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'documents' && <DocumentsList />}
        
        {currentView === 'editor' && currentDocument && (
          <RaiseLetterEditor
            initialData={currentDocument}
            onSave={handleSaveDocument}
            autoSave={true}
            autoSaveInterval={30000}
            className="max-w-4xl mx-auto"
          />
        )}

        {currentView === 'generator' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">AI-Powered Letter Generator</h2>
              
              {/* User Information Form */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Your Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <input
                      type="text"
                      placeholder="Your Name"
                      value={userFormData.name}
                      onChange={(e) => setUserFormData(prev => ({ ...prev, name: e.target.value }))}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="Job Title"
                      value={userFormData.job_title}
                      onChange={(e) => setUserFormData(prev => ({ ...prev, job_title: e.target.value }))}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="Company Name"
                      value={userFormData.company}
                      onChange={(e) => setUserFormData(prev => ({ ...prev, company: e.target.value }))}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="Manager Name"
                      value={userFormData.manager_name}
                      onChange={(e) => setUserFormData(prev => ({ ...prev, manager_name: e.target.value }))}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <input
                      type="number"
                      placeholder="Current Salary"
                      value={userFormData.current_salary}
                      onChange={(e) => setUserFormData(prev => ({ ...prev, current_salary: parseInt(e.target.value) || 0 }))}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <input
                      type="date"
                      placeholder="Last Raise Date"
                      value={userFormData.last_raise_date}
                      onChange={(e) => setUserFormData(prev => ({ ...prev, last_raise_date: e.target.value }))}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Letter Preferences</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <select
                      value={aiGenerationData.tone}
                      onChange={(e) => setAIGenerationData(prev => ({ ...prev, tone: e.target.value as LetterTone }))}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      {getLetterToneOptions().map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label} - {option.description}
                        </option>
                      ))}
                    </select>
                    <select
                      value={aiGenerationData.length}
                      onChange={(e) => setAIGenerationData(prev => ({ ...prev, length: e.target.value as LetterLength }))}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      {getLetterLengthOptions().map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label} - {option.description}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Key Achievements</h3>
                  {aiGenerationData.key_achievements.map((achievement, index) => (
                    <div key={index} className="flex items-center space-x-2 mb-2">
                      <input
                        type="text"
                        placeholder="Describe a key achievement..."
                        value={achievement}
                        onChange={(e) => {
                          const newAchievements = [...aiGenerationData.key_achievements]
                          newAchievements[index] = e.target.value
                          setAIGenerationData(prev => ({ ...prev, key_achievements: newAchievements }))
                        }}
                        className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      />
                      <button
                        onClick={() => {
                          const newAchievements = aiGenerationData.key_achievements.filter((_, i) => i !== index)
                          setAIGenerationData(prev => ({ ...prev, key_achievements: newAchievements }))
                        }}
                        className="text-red-500 hover:text-red-700"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => {
                      setAIGenerationData(prev => ({ 
                        ...prev, 
                        key_achievements: [...prev.key_achievements, ''] 
                      }))
                    }}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    + Add Achievement
                  </button>
                </div>

                <div className="flex justify-between items-center pt-6">
                  <button
                    onClick={() => setCurrentView('documents')}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleGenerateAILetter}
                    disabled={isGeneratingAI || !userFormData.name || !userFormData.company}
                    className="inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {isGeneratingAI ? (
                      <>
                        <RefreshCw className="animate-spin -ml-1 mr-3 h-4 w-4" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4 mr-2" />
                        Generate AI Letter
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 