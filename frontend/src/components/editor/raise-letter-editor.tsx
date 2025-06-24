'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { 
  Bold, 
  Italic, 
  Underline, 
  AlignLeft, 
  AlignCenter, 
  AlignRight,
  List,
  ListOrdered,
  Save,
  Eye,
  EyeOff,
  Download,
  Printer,
  Undo,
  Redo,
  Type,
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react'

// Types for the editor
export interface RaiseLetterEditorData {
  id?: string
  title: string
  content: string
  metadata: {
    employeeName: string
    employeeTitle: string
    companyName: string
    managerName: string
    lastModified: string
    createdAt: string
    version: number
  }
}

export interface EditorProps {
  initialData?: RaiseLetterEditorData
  onSave?: (data: RaiseLetterEditorData) => Promise<void>
  onPreview?: (content: string) => void
  autoSave?: boolean
  autoSaveInterval?: number
  readOnly?: boolean
  className?: string
}

// Formatting options for the editor
interface FormatOption {
  command: string
  value?: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  shortcut?: string
}

const formatOptions: FormatOption[] = [
  { command: 'bold', icon: Bold, label: 'Bold', shortcut: 'Ctrl+B' },
  { command: 'italic', icon: Italic, label: 'Italic', shortcut: 'Ctrl+I' },
  { command: 'underline', icon: Underline, label: 'Underline', shortcut: 'Ctrl+U' },
  { command: 'justifyLeft', icon: AlignLeft, label: 'Align Left' },
  { command: 'justifyCenter', icon: AlignCenter, label: 'Center' },
  { command: 'justifyRight', icon: AlignRight, label: 'Align Right' },
  { command: 'insertUnorderedList', icon: List, label: 'Bullet List' },
  { command: 'insertOrderedList', icon: ListOrdered, label: 'Numbered List' },
]

export default function RaiseLetterEditor({
  initialData,
  onSave,
  onPreview,
  autoSave = true,
  autoSaveInterval = 30000, // 30 seconds
  readOnly = false,
  className = ''
}: EditorProps) {
  // Editor state
  const [editorData, setEditorData] = useState<RaiseLetterEditorData>(
    initialData || {
      title: 'Salary Adjustment Request',
      content: '',
      metadata: {
        employeeName: '',
        employeeTitle: '',
        companyName: '',
        managerName: '',
        lastModified: new Date().toISOString(),
        createdAt: new Date().toISOString(),
        version: 1
      }
    }
  )

  // UI state
  const [isPreviewMode, setIsPreviewMode] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'error' | 'unsaved'>('saved')
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // Refs
  const editorRef = useRef<HTMLDivElement>(null)
  const autoSaveTimeoutRef = useRef<ReturnType<typeof setTimeout>>()

  // Initialize editor content
  useEffect(() => {
    if (editorRef.current && editorData.content) {
      editorRef.current.innerHTML = editorData.content
    }
  }, [editorData.content])

  // Auto-save functionality
  useEffect(() => {
    if (!autoSave || !hasUnsavedChanges || readOnly) return

    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current)
    }

    autoSaveTimeoutRef.current = setTimeout(() => {
      handleSave(true) // Auto-save
    }, autoSaveInterval)

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current)
      }
    }
  }, [hasUnsavedChanges, autoSave, autoSaveInterval])

  // Handle content changes
  const handleContentChange = useCallback(() => {
    if (!editorRef.current || readOnly) return

    const content = editorRef.current.innerHTML
    setEditorData((prev: RaiseLetterEditorData) => ({
      ...prev,
      content,
      metadata: {
        ...prev.metadata,
        lastModified: new Date().toISOString(),
        version: prev.metadata.version + 1
      }
    }))
    setHasUnsavedChanges(true)
    setSaveStatus('unsaved')
  }, [readOnly])

  // Handle formatting commands
  const handleFormat = (command: string, value?: string) => {
    if (readOnly) return
    
    document.execCommand(command, false, value)
    editorRef.current?.focus()
    handleContentChange()
  }

  // Handle save
  const handleSave = async (isAutoSave = false) => {
    if (!onSave || readOnly) return

    setIsSaving(true)
    setSaveStatus('saving')

    try {
      await onSave(editorData)
      setHasUnsavedChanges(false)
      setSaveStatus('saved')
      setLastSaved(new Date())
      
      if (!isAutoSave) {
        // Show success feedback for manual saves
        setTimeout(() => setSaveStatus('saved'), 2000)
      }
    } catch (error) {
      console.error('Error saving document:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('unsaved'), 3000)
    } finally {
      setIsSaving(false)
    }
  }

  // Handle preview toggle
  const handlePreviewToggle = () => {
    setIsPreviewMode(!isPreviewMode)
    if (onPreview && !isPreviewMode) {
      onPreview(editorData.content)
    }
  }

  // Handle print
  const handlePrint = () => {
    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Salary Adjustment Request</title>
            <style>
              body { font-family: 'Times New Roman', serif; margin: 1in; line-height: 1.6; }
              h1, h2, h3 { color: #333; }
              p { margin-bottom: 1em; }
              @media print { body { margin: 0.5in; } }
            </style>
          </head>
          <body>
            <h1>${editorData.title}</h1>
            ${editorData.content}
          </body>
        </html>
      `)
      printWindow.document.close()
      printWindow.print()
    }
  }

  // Handle download
  const handleDownload = () => {
    const element = document.createElement('a')
    const content = `
      <html>
        <head>
          <title>${editorData.title}</title>
          <meta charset="UTF-8">
          <style>
            body { font-family: 'Times New Roman', serif; margin: 1in; line-height: 1.6; }
            h1, h2, h3 { color: #333; }
            p { margin-bottom: 1em; }
          </style>
        </head>
        <body>
          <h1>${editorData.title}</h1>
          ${editorData.content}
        </body>
      </html>
    `
    const file = new Blob([content], { type: 'text/html' })
    element.href = URL.createObjectURL(file)
    element.download = `${editorData.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.html`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (readOnly) return

      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'b':
            e.preventDefault()
            handleFormat('bold')
            break
          case 'i':
            e.preventDefault()
            handleFormat('italic')
            break
          case 'u':
            e.preventDefault()
            handleFormat('underline')
            break
          case 's':
            e.preventDefault()
            handleSave()
            break
          case 'z':
            if (e.shiftKey) {
              e.preventDefault()
              handleFormat('redo')
            } else {
              e.preventDefault()
              handleFormat('undo')
            }
            break
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [readOnly])

  // Save status indicator
  const SaveStatusIndicator = () => {
    const getStatusConfig = () => {
      switch (saveStatus) {
        case 'saving':
          return { icon: Clock, text: 'Saving...', color: 'text-blue-600' }
        case 'saved':
          return { icon: CheckCircle2, text: 'Saved', color: 'text-green-600' }
        case 'error':
          return { icon: AlertCircle, text: 'Error saving', color: 'text-red-600' }
        case 'unsaved':
          return { icon: FileText, text: 'Unsaved changes', color: 'text-yellow-600' }
        default:
          return { icon: FileText, text: '', color: 'text-gray-600' }
      }
    }

    const { icon: Icon, text, color } = getStatusConfig()

    return (
      <div className={`flex items-center space-x-1 text-xs ${color}`}>
        <Icon className="h-3 w-3" />
        <span>{text}</span>
        {lastSaved && saveStatus === 'saved' && (
          <span className="text-gray-500">
            at {lastSaved.toLocaleTimeString()}
          </span>
        )}
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gray-50 border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <input
              type="text"
              value={editorData.title}
              onChange={(e) => {
                setEditorData((prev: RaiseLetterEditorData) => ({ ...prev, title: e.target.value }))
                setHasUnsavedChanges(true)
              }}
              disabled={readOnly}
              className="text-lg font-semibold bg-transparent border-none outline-none focus:bg-white focus:border focus:border-blue-300 rounded px-2 py-1"
              placeholder="Document title..."
            />
            <div className="mt-1">
              <SaveStatusIndicator />
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {!readOnly && (
              <button
                onClick={() => handleSave()}
                disabled={isSaving || !hasUnsavedChanges}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="h-4 w-4 mr-1" />
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            )}
            
            <button
              onClick={handlePreviewToggle}
              className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                isPreviewMode
                  ? 'border-blue-300 text-blue-700 bg-blue-50 hover:bg-blue-100'
                  : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
              }`}
            >
              {isPreviewMode ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
              {isPreviewMode ? 'Edit' : 'Preview'}
            </button>
            
            <button
              onClick={handlePrint}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Printer className="h-4 w-4 mr-1" />
              Print
            </button>
            
            <button
              onClick={handleDownload}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Download className="h-4 w-4 mr-1" />
              Download
            </button>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      {!isPreviewMode && !readOnly && (
        <div className="bg-white border-b px-6 py-3">
          <div className="flex items-center space-x-1">
            {formatOptions.map((option) => (
              <button
                key={option.command}
                onClick={() => handleFormat(option.command, option.value)}
                className="inline-flex items-center justify-center w-8 h-8 border border-gray-300 rounded hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                title={`${option.label}${option.shortcut ? ` (${option.shortcut})` : ''}`}
              >
                <option.icon className="h-4 w-4 text-gray-600" />
              </button>
            ))}
            
            <div className="w-px h-6 bg-gray-300 mx-2" />
            
            <button
              onClick={() => handleFormat('undo')}
              className="inline-flex items-center justify-center w-8 h-8 border border-gray-300 rounded hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              title="Undo (Ctrl+Z)"
            >
              <Undo className="h-4 w-4 text-gray-600" />
            </button>
            
            <button
              onClick={() => handleFormat('redo')}
              className="inline-flex items-center justify-center w-8 h-8 border border-gray-300 rounded hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              title="Redo (Ctrl+Shift+Z)"
            >
              <Redo className="h-4 w-4 text-gray-600" />
            </button>

            <div className="w-px h-6 bg-gray-300 mx-2" />

            <select
              onChange={(e) => handleFormat('fontSize', e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
              defaultValue="3"
            >
              <option value="1">Small</option>
              <option value="2">Normal</option>
              <option value="3">Medium</option>
              <option value="4">Large</option>
              <option value="5">X-Large</option>
            </select>
          </div>
        </div>
      )}

      {/* Editor Content */}
      <div className="px-6 py-6">
        {isPreviewMode ? (
          <div className="prose max-w-none">
            <h1 className="text-2xl font-bold mb-6">{editorData.title}</h1>
            <div 
              dangerouslySetInnerHTML={{ __html: editorData.content }}
              className="leading-relaxed"
            />
          </div>
        ) : (
          <div
            ref={editorRef}
            contentEditable={!readOnly}
            onInput={handleContentChange}
            onBlur={handleContentChange}
            className={`min-h-96 outline-none leading-relaxed ${
              readOnly ? 'cursor-default' : 'cursor-text'
            }`}
            style={{
              fontFamily: '"Times New Roman", serif',
              fontSize: '14px',
              lineHeight: '1.6'
            }}
            data-placeholder={readOnly ? '' : 'Start writing your raise request letter...'}
          />
        )}
      </div>

      {/* Footer with metadata */}
      <div className="bg-gray-50 border-t px-6 py-3">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div>
            Version {editorData.metadata.version} • 
            Created {new Date(editorData.metadata.createdAt).toLocaleDateString()} • 
            Modified {new Date(editorData.metadata.lastModified).toLocaleDateString()}
          </div>
          <div className="flex items-center space-x-4">
            {editorData.metadata.employeeName && (
              <span>{editorData.metadata.employeeName}</span>
            )}
            {editorData.metadata.companyName && (
              <span>at {editorData.metadata.companyName}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 