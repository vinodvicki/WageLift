/**
 * Tests for raise letter template utilities
 */

import {
  RaiseLetterData,
  defaultTemplateData,
  formatCurrency,
  formatPercentage,
  formatDate,
  generateTemplateDataFromCPI,
  validateTemplateData,
  getTemplateStatus,
  generateBasicHTMLTemplate
} from '../raise-letter-utils'

describe('Raise Letter Template Utilities', () => {
  describe('formatCurrency', () => {
    it('should format currency correctly', () => {
      expect(formatCurrency(75000)).toBe('$75,000')
      expect(formatCurrency(100000)).toBe('$100,000')
      expect(formatCurrency(50000.99)).toBe('$50,001')
    })
  })

  describe('formatPercentage', () => {
    it('should format percentage correctly', () => {
      expect(formatPercentage(8.5)).toBe('8.5%')
      expect(formatPercentage(10)).toBe('10.0%')
      expect(formatPercentage(0.5)).toBe('0.5%')
    })
  })

  describe('formatDate', () => {
    it('should format dates correctly', () => {
      expect(formatDate('2024-01-15')).toMatch(/January 15, 2024/)
      expect(formatDate('[PLACEHOLDER]')).toBe('[PLACEHOLDER]')
      expect(formatDate('invalid')).toBe('invalid')
    })
  })

  describe('generateTemplateDataFromCPI', () => {
    it('should generate template data from CPI analysis', () => {
      const cpiData = {
        current_salary: 80000,
        adjusted_salary: 88000,
        dollar_gap: -8000,
        percentage_gap: -10
      }

      const userInfo = {
        name: 'John Doe',
        email: 'john@example.com'
      }

      const result = generateTemplateDataFromCPI(cpiData, userInfo)

      expect(result.employeeName).toBe('John Doe')
      expect(result.employeeEmail).toBe('john@example.com')
      expect(result.currentSalary).toBe(80000)
      expect(result.requestedSalary).toBe(88000)
      expect(result.inflationRate).toBe(10)
      expect(result.cpiGapAmount).toBe(8000)
    })
  })

  describe('validateTemplateData', () => {
    it('should validate complete template data', () => {
      const validData: RaiseLetterData = {
        employeeName: 'John Doe',
        employeeTitle: 'Software Engineer',
        employeeEmail: 'john@example.com',
        managerName: 'Jane Smith',
        managerTitle: 'Engineering Manager',
        companyName: 'TechCorp',
        currentSalary: 80000,
        lastRaiseDate: '2022-01-01',
        requestedSalary: 88000,
        inflationRate: 10,
        cpiGapPercentage: 10,
        cpiGapAmount: 8000,
        purchasingPowerLoss: 8000,
        letterDate: '2024-01-15',
        proposedEffectiveDate: '2024-02-15'
      }

      const errors = validateTemplateData(validData)
      expect(errors).toHaveLength(0)
    })

    it('should return errors for invalid data', () => {
      const invalidData = {
        employeeName: '[PLACEHOLDER]',
        currentSalary: 0
      }

      const errors = validateTemplateData(invalidData)
      expect(errors.length).toBeGreaterThan(0)
      expect(errors).toContain('Employee name is required')
      expect(errors).toContain('Manager name is required')
      expect(errors).toContain('Company name is required')
      expect(errors).toContain('Valid current salary is required')
    })
  })

  describe('getTemplateStatus', () => {
    it('should return correct status for valid data', () => {
      const validData: RaiseLetterData = {
        employeeName: 'John Doe',
        employeeTitle: 'Software Engineer',
        employeeEmail: 'john@example.com',
        managerName: 'Jane Smith',
        managerTitle: 'Engineering Manager',
        companyName: 'TechCorp',
        currentSalary: 80000,
        lastRaiseDate: '2022-01-01',
        requestedSalary: 88000,
        inflationRate: 10,
        cpiGapPercentage: 10,
        cpiGapAmount: 8000,
        purchasingPowerLoss: 8000,
        letterDate: '2024-01-15',
        proposedEffectiveDate: '2024-02-15'
      }

      const status = getTemplateStatus(validData)
      expect(status.isValid).toBe(true)
      expect(status.hasPlaceholders).toBe(false)
      expect(status.readyForGeneration).toBe(true)
    })

    it('should detect placeholders', () => {
      const status = getTemplateStatus(defaultTemplateData)
      expect(status.hasPlaceholders).toBe(true)
      expect(status.readyForGeneration).toBe(false)
    })
  })

  describe('generateBasicHTMLTemplate', () => {
    it('should generate valid HTML template', () => {
      const data: RaiseLetterData = {
        employeeName: 'John Doe',
        employeeTitle: 'Software Engineer',
        employeeEmail: 'john@example.com',
        managerName: 'Jane Smith',
        managerTitle: 'Engineering Manager',
        companyName: 'TechCorp',
        currentSalary: 80000,
        lastRaiseDate: '2022-01-01',
        requestedSalary: 88000,
        inflationRate: 10,
        cpiGapPercentage: 10,
        cpiGapAmount: 8000,
        purchasingPowerLoss: 8000,
        letterDate: '2024-01-15',
        proposedEffectiveDate: '2024-02-15'
      }

      const html = generateBasicHTMLTemplate(data)
      
      expect(html).toContain('<!DOCTYPE html>')
      expect(html).toContain('John Doe')
      expect(html).toContain('Jane Smith')
      expect(html).toContain('TechCorp')
      expect(html).toContain('$80,000')
      expect(html).toContain('$88,000')
      expect(html).toContain('Salary Adjustment Request')
    })
  })
}) 