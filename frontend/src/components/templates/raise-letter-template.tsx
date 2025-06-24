'use client'

import React, { useState } from 'react'
import { Info, Calendar, DollarSign, TrendingUp, FileText, Building, User } from 'lucide-react'

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
const defaultData: RaiseLetterData = {
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

// Tooltip component for explanations
const Tooltip: React.FC<{ content: string; children: React.ReactNode }> = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false)
  
  return (
    <span 
      className="relative inline-block cursor-help"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div className="absolute z-10 w-64 p-2 mt-1 text-sm text-white bg-gray-800 rounded-lg shadow-lg -top-2 left-full ml-2">
          <div className="absolute w-2 h-2 bg-gray-800 transform rotate-45 -left-1 top-3"></div>
          {content}
        </div>
      )}
    </span>
  )
}

// Currency formatter utility
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

// Percentage formatter utility
const formatPercentage = (value: number): string => {
  return `${value.toFixed(1)}%`
}

// Date formatter utility
const formatDate = (dateString: string): string => {
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

interface RaiseLetterTemplateProps {
  data?: Partial<RaiseLetterData>
  className?: string
  showTooltips?: boolean
}

export const RaiseLetterTemplate: React.FC<RaiseLetterTemplateProps> = ({ 
  data = {}, 
  className = '',
  showTooltips = true 
}) => {
  const templateData = { ...defaultData, ...data }
  
  const TooltipWrapper: React.FC<{ tooltip: string; children: React.ReactNode }> = ({ tooltip, children }) => {
    if (!showTooltips) return <>{children}</>
    return <Tooltip content={tooltip}>{children}</Tooltip>
  }

  return (
    <div className={`max-w-4xl mx-auto bg-white shadow-lg rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
        <div className="flex items-center space-x-3">
          <FileText className="w-8 h-8" />
          <div>
            <h1 className="text-2xl font-bold">Salary Adjustment Request</h1>
            <p className="text-blue-100">Professional compensation review based on market analysis</p>
          </div>
        </div>
      </div>

      {/* Letter Content */}
      <div className="p-8 space-y-6">
        
        {/* Letter Header */}
        <div className="flex justify-between items-start border-b pb-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <User className="w-4 h-4 text-gray-500" />
              <span className="font-medium">{templateData.employeeName}</span>
            </div>
            <div className="text-gray-600">{templateData.employeeTitle}</div>
            <div className="text-gray-600">{templateData.employeeEmail}</div>
            {templateData.employeePhone && (
              <div className="text-gray-600">{templateData.employeePhone}</div>
            )}
          </div>
          <div className="text-right space-y-1">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span>{formatDate(templateData.letterDate)}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Building className="w-4 h-4 text-gray-500" />
              <span>{templateData.companyName}</span>
            </div>
          </div>
        </div>

        {/* Recipient Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="font-semibold text-gray-800">To:</div>
          <div className="mt-1">
            <div className="font-medium">{templateData.managerName}</div>
            <div className="text-gray-600">{templateData.managerTitle}</div>
            {templateData.department && (
              <div className="text-gray-600">{templateData.department}</div>
            )}
          </div>
        </div>

        {/* Letter Body */}
        <div className="space-y-4 text-gray-800 leading-relaxed">
          
          {/* Opening */}
          <p>
            Dear {templateData.managerName},
          </p>
          
          <p>
            I am writing to formally request a salary adjustment based on comprehensive market analysis and my continued contributions to {templateData.companyName}. This request is supported by data-driven insights regarding inflation impact and current market conditions.
          </p>

          {/* Current Situation */}
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
            <h3 className="font-semibold text-blue-800 mb-2 flex items-center">
              <DollarSign className="w-4 h-4 mr-2" />
              Current Compensation Analysis
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Current Salary:</span> {formatCurrency(templateData.currentSalary)}
              </div>
              <div>
                <span className="font-medium">Last Adjustment:</span> {formatDate(templateData.lastRaiseDate)}
              </div>
              <div>
                <span className="font-medium">Requested Salary:</span> {formatCurrency(templateData.requestedSalary)}
              </div>
              <div>
                <span className="font-medium">Proposed Effective Date:</span> {formatDate(templateData.proposedEffectiveDate)}
              </div>
            </div>
          </div>

          {/* Inflation Impact Analysis */}
          <div className="bg-orange-50 border-l-4 border-orange-400 p-4 rounded-r-lg">
            <h3 className="font-semibold text-orange-800 mb-2 flex items-center">
              <TrendingUp className="w-4 h-4 mr-2" />
              Purchasing Power Analysis
            </h3>
            <p className="mb-3 text-sm text-gray-700">
              Based on official Consumer Price Index (CPI) data from the Bureau of Labor Statistics, my current compensation has been significantly impacted by inflation:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <TooltipWrapper tooltip="The cumulative inflation rate since your last salary adjustment, calculated using official CPI data from the Bureau of Labor Statistics.">
                  <span className="font-medium border-b border-dotted border-gray-400">Cumulative Inflation Rate:</span>
                </TooltipWrapper>
                <span className="ml-2 font-bold text-orange-600">{formatPercentage(templateData.inflationRate)}</span>
              </div>
              <div>
                <TooltipWrapper tooltip="The percentage gap between your current salary and what it should be when adjusted for inflation to maintain the same purchasing power.">
                  <span className="font-medium border-b border-dotted border-gray-400">CPI Gap Percentage:</span>
                </TooltipWrapper>
                <span className="ml-2 font-bold text-red-600">{formatPercentage(templateData.cpiGapPercentage)}</span>
              </div>
              <div>
                <TooltipWrapper tooltip="The dollar amount representing the loss in purchasing power due to inflation since your last salary adjustment.">
                  <span className="font-medium border-b border-dotted border-gray-400">Purchasing Power Loss:</span>
                </TooltipWrapper>
                <span className="ml-2 font-bold text-red-600">{formatCurrency(templateData.purchasingPowerLoss)}</span>
              </div>
              <div>
                <TooltipWrapper tooltip="The total dollar amount needed to restore your salary to its original purchasing power, accounting for cumulative inflation.">
                  <span className="font-medium border-b border-dotted border-gray-400">Required Adjustment:</span>
                </TooltipWrapper>
                <span className="ml-2 font-bold text-green-600">{formatCurrency(templateData.cpiGapAmount)}</span>
              </div>
            </div>
          </div>

          {/* Key Contributions */}
          {templateData.achievements && templateData.achievements.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Key Achievements & Contributions</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                {templateData.achievements.map((achievement, index) => (
                  <li key={index}>{achievement}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Additional Responsibilities */}
          {templateData.responsibilities && templateData.responsibilities.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Expanded Responsibilities</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                {templateData.responsibilities.map((responsibility, index) => (
                  <li key={index}>{responsibility}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Market Justification */}
          <p>
            This adjustment request is not only justified by inflation impact but also reflects my continued value delivery and expanded contributions to the organization. The requested salary of {formatCurrency(templateData.requestedSalary)} represents a fair market adjustment that accounts for both economic factors and performance.
          </p>

          {/* Data Source Transparency */}
          <div className="bg-gray-50 p-4 rounded-lg border">
            <h4 className="font-medium text-gray-800 mb-2 flex items-center">
              <Info className="w-4 h-4 mr-2" />
              Data Sources & Methodology
            </h4>
            <div className="text-sm text-gray-600 space-y-1">
              <p>• <strong>Inflation Data:</strong> U.S. Bureau of Labor Statistics Consumer Price Index (CPI-U)</p>
              <p>• <strong>Analysis Period:</strong> From {formatDate(templateData.lastRaiseDate)} to present</p>
              <p>• <strong>Calculation Method:</strong> Compound inflation adjustment using official CPI data</p>
              <p>• <strong>Data Accuracy:</strong> Updated monthly with latest BLS publications</p>
            </div>
          </div>

          {/* Closing */}
          <p>
            I would welcome the opportunity to discuss this request in detail and provide any additional information you may need. I am confident that this adjustment reflects both market realities and my continued commitment to excellence at {templateData.companyName}.
          </p>

          <p>
            Thank you for your consideration. I look forward to our discussion.
          </p>

          <div className="mt-6">
            <p>Sincerely,</p>
            <div className="mt-4 font-medium">{templateData.employeeName}</div>
            <div className="text-gray-600">{templateData.employeeTitle}</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-50 px-8 py-4 border-t">
        <div className="text-xs text-gray-500 text-center">
          Generated by WageLift - AI-Powered Salary Analysis Platform | 
          Data sourced from U.S. Bureau of Labor Statistics | 
          Analysis Date: {formatDate(templateData.letterDate)}
        </div>
      </div>
    </div>
  )
}

// Export utility functions for external use
export { formatCurrency, formatPercentage, formatDate }
export type { RaiseLetterData } 