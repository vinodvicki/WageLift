/**
 * Raise Letter Template Utilities
 * Interfaces and utility functions for generating professional raise request letters
 */

// TypeScript interfaces for template data
export interface RaiseLetterData {
  // Personal Information
  employeeName: string
  employeeTitle: string
  employeeEmail: string
  employeePhone?: string
  
  // Manager Information
  managerName: string
  managerTitle: string
  
  // Company Information
  companyName: string
  department?: string
  
  // Salary Information
  currentSalary: number
  lastRaiseDate: string
  requestedSalary: number
  
  // CPI Analysis Data
  inflationRate: number
  cpiGapPercentage: number
  cpiGapAmount: number
  purchasingPowerLoss: number
  
  // Performance Data
  achievements?: string[]
  responsibilities?: string[]
  
  // Dates
  letterDate: string
  proposedEffectiveDate: string
}

// Default template data for preview
export const defaultTemplateData: RaiseLetterData = {
  employeeName: '[EMPLOYEE_NAME]',
  employeeTitle: '[EMPLOYEE_TITLE]',
  employeeEmail: '[EMPLOYEE_EMAIL]',
  managerName: '[MANAGER_NAME]',
  managerTitle: '[MANAGER_TITLE]',
  companyName: '[COMPANY_NAME]',
  department: '[DEPARTMENT]',
  currentSalary: 75000,
  lastRaiseDate: '[LAST_RAISE_DATE]',
  requestedSalary: 82000,
  inflationRate: 6.8,
  cpiGapPercentage: 9.3,
  cpiGapAmount: 7000,
  purchasingPowerLoss: 5100,
  achievements: [
    '[ACHIEVEMENT_1]',
    '[ACHIEVEMENT_2]',
    '[ACHIEVEMENT_3]'
  ],
  responsibilities: [
    '[RESPONSIBILITY_1]',
    '[RESPONSIBILITY_2]'
  ],
  letterDate: '[CURRENT_DATE]',
  proposedEffectiveDate: '[PROPOSED_DATE]'
}

// Currency formatter utility
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

// Percentage formatter utility
export const formatPercentage = (value: number): string => {
  return `${value.toFixed(1)}%`
}

// Date formatter utility
export const formatDate = (dateString: string): string => {
  if (dateString.startsWith('[') && dateString.endsWith(']')) {
    return dateString // Return placeholder as-is
  }
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}

// Generate template data from CPI analysis
export const generateTemplateDataFromCPI = (
  cpiData: {
    current_salary: number
    adjusted_salary: number
    dollar_gap: number
    percentage_gap: number
  },
  userInfo: {
    name?: string
    email?: string
  } = {},
  customData: Partial<RaiseLetterData> = {}
): RaiseLetterData => {
  const today = new Date()
  const proposedDate = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000) // 30 days from now
  
  return {
    ...defaultTemplateData,
    employeeName: userInfo.name || defaultTemplateData.employeeName,
    employeeEmail: userInfo.email || defaultTemplateData.employeeEmail,
    currentSalary: cpiData.current_salary,
    requestedSalary: cpiData.adjusted_salary,
    inflationRate: Math.abs(cpiData.percentage_gap),
    cpiGapPercentage: Math.abs(cpiData.percentage_gap),
    cpiGapAmount: Math.abs(cpiData.dollar_gap),
    purchasingPowerLoss: Math.abs(cpiData.dollar_gap),
    letterDate: today.toISOString().split('T')[0],
    proposedEffectiveDate: proposedDate.toISOString().split('T')[0],
    ...customData
  }
}

// Template sections for modular generation
export const templateSections = {
  header: {
    title: 'Salary Adjustment Request',
    subtitle: 'Professional compensation review based on market analysis'
  },
  
  opening: (managerName: string) => 
    `Dear ${managerName},\n\nI am writing to formally request a salary adjustment based on comprehensive market analysis and my continued contributions to the organization. This request is supported by data-driven insights regarding inflation impact and current market conditions.`,
  
  cpiAnalysis: (data: RaiseLetterData) => 
    `Based on official Consumer Price Index (CPI) data from the Bureau of Labor Statistics, my current compensation has been significantly impacted by inflation. The cumulative inflation rate since my last adjustment is ${formatPercentage(data.inflationRate)}, resulting in a purchasing power loss of ${formatCurrency(data.purchasingPowerLoss)}.`,
  
  marketJustification: (requestedSalary: number, companyName: string) =>
    `This adjustment request is not only justified by inflation impact but also reflects my continued value delivery and expanded contributions to the organization. The requested salary of ${formatCurrency(requestedSalary)} represents a fair market adjustment that accounts for both economic factors and performance.`,
  
  closing: (companyName: string) =>
    `I would welcome the opportunity to discuss this request in detail and provide any additional information you may need. I am confident that this adjustment reflects both market realities and my continued commitment to excellence at ${companyName}.\n\nThank you for your consideration. I look forward to our discussion.`,
  
  dataSource: (lastRaiseDate: string) => ({
    title: 'Data Sources & Methodology',
    items: [
      'Inflation Data: U.S. Bureau of Labor Statistics Consumer Price Index (CPI-U)',
      `Analysis Period: From ${formatDate(lastRaiseDate)} to present`,
      'Calculation Method: Compound inflation adjustment using official CPI data',
      'Data Accuracy: Updated monthly with latest BLS publications'
    ]
  })
}

// Validation functions
export const validateTemplateData = (data: Partial<RaiseLetterData>): string[] => {
  const errors: string[] = []
  
  if (!data.employeeName || data.employeeName.includes('[')) {
    errors.push('Employee name is required')
  }
  
  if (!data.managerName || data.managerName.includes('[')) {
    errors.push('Manager name is required')
  }
  
  if (!data.companyName || data.companyName.includes('[')) {
    errors.push('Company name is required')
  }
  
  if (!data.currentSalary || data.currentSalary <= 0) {
    errors.push('Valid current salary is required')
  }
  
  if (!data.requestedSalary || data.requestedSalary <= 0) {
    errors.push('Valid requested salary is required')
  }
  
  return errors
}

// Export template status helper
export const getTemplateStatus = (data: RaiseLetterData) => {
  const errors = validateTemplateData(data)
  const hasPlaceholders = Object.values(data).some(value => 
    typeof value === 'string' && value.includes('[') && value.includes(']')
  )
  
  return {
    isValid: errors.length === 0,
    hasPlaceholders,
    errors,
    readyForGeneration: errors.length === 0 && !hasPlaceholders
  }
}

// Simple HTML template for basic rendering
export const generateBasicHTMLTemplate = (data: RaiseLetterData): string => {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Salary Adjustment Request - ${data.employeeName}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .content { margin-bottom: 20px; }
        .highlight { background-color: #f0f8ff; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0; }
        .signature { margin-top: 40px; }
        .footer { font-size: 12px; color: #666; text-align: center; margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Salary Adjustment Request</h1>
        <p>Professional compensation review based on market analysis</p>
        <p><strong>Date:</strong> ${formatDate(data.letterDate)}</p>
    </div>
    
    <div class="content">
        <p><strong>From:</strong> ${data.employeeName}, ${data.employeeTitle}</p>
        <p><strong>To:</strong> ${data.managerName}, ${data.managerTitle}</p>
        <p><strong>Company:</strong> ${data.companyName}</p>
        
        <h2>Request Summary</h2>
        <div class="highlight">
            <p><strong>Current Salary:</strong> ${formatCurrency(data.currentSalary)}</p>
            <p><strong>Requested Salary:</strong> ${formatCurrency(data.requestedSalary)}</p>
            <p><strong>Inflation Impact:</strong> ${formatPercentage(data.inflationRate)}</p>
            <p><strong>Purchasing Power Loss:</strong> ${formatCurrency(data.purchasingPowerLoss)}</p>
        </div>
        
        <h2>Letter Content</h2>
        <p>${templateSections.opening(data.managerName)}</p>
        <p>${templateSections.cpiAnalysis(data)}</p>
        <p>${templateSections.marketJustification(data.requestedSalary, data.companyName)}</p>
        <p>${templateSections.closing(data.companyName)}</p>
        
        <div class="signature">
            <p>Sincerely,</p>
            <p><strong>${data.employeeName}</strong></p>
            <p>${data.employeeTitle}</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by WageLift - AI-Powered Salary Analysis Platform</p>
        <p>Data sourced from U.S. Bureau of Labor Statistics</p>
    </div>
</body>
</html>
  `.trim()
} 