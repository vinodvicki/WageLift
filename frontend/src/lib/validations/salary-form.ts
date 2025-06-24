/**
 * Salary form validation schema with comprehensive rules
 * Supports financial data validation and user input constraints
 */

import { z } from 'zod';

// Job titles for validation (expandable via API)
export const jobTitles = [
  'Software Engineer',
  'Senior Software Engineer',
  'Staff Software Engineer',
  'Principal Software Engineer',
  'Engineering Manager',
  'Senior Engineering Manager',
  'Data Scientist',
  'Senior Data Scientist',
  'Product Manager',
  'Senior Product Manager',
  'Designer',
  'Senior Designer',
  'Marketing Manager',
  'Sales Manager',
  'Account Executive',
  'Business Analyst',
  'Project Manager',
  'DevOps Engineer',
  'QA Engineer',
  'Technical Writer',
] as const;

// Experience levels
export const experienceLevels = [
  { value: 'entry', label: 'Entry Level (0-2 years)' },
  { value: 'mid', label: 'Mid Level (3-5 years)' },
  { value: 'senior', label: 'Senior Level (6-10 years)' },
  { value: 'executive', label: 'Executive Level (10+ years)' },
] as const;

// Company sizes
export const companySizes = [
  { value: 'startup', label: 'Startup (1-50 employees)' },
  { value: 'small', label: 'Small (51-200 employees)' },
  { value: 'medium', label: 'Medium (201-1000 employees)' },
  { value: 'large', label: 'Large (1001-5000 employees)' },
  { value: 'enterprise', label: 'Enterprise (5000+ employees)' },
] as const;

// Benefits options
export const benefitsOptions = [
  { value: 'health_insurance', label: 'Health Insurance' },
  { value: 'dental_vision', label: 'Dental & Vision' },
  { value: 'retirement_401k', label: '401(k) Matching' },
  { value: 'pto', label: 'Paid Time Off' },
  { value: 'flexible_schedule', label: 'Flexible Schedule' },
  { value: 'remote_work', label: 'Remote Work Options' },
  { value: 'stock_options', label: 'Stock Options/Equity' },
  { value: 'bonus', label: 'Performance Bonus' },
  { value: 'professional_development', label: 'Professional Development' },
  { value: 'tuition_reimbursement', label: 'Tuition Reimbursement' },
] as const;

// Salary form validation schema
export const salaryFormSchema = z.object({
  // Current salary with realistic bounds
  currentSalary: z
    .number({
      required_error: 'Current salary is required',
      invalid_type_error: 'Please enter a valid salary amount',
    })
    .min(20_000, 'Salary must be at least $20,000')
    .max(2_000_000, 'Salary must be less than $2,000,000')
    .positive('Salary must be a positive number'),

  // Last raise date
  lastRaiseDate: z
    .date({
      required_error: 'Please select your last raise date',
      invalid_type_error: 'Please enter a valid date',
    })
    .max(new Date(), 'Date cannot be in the future')
    .refine(
      (date: Date) => {
        const fiveYearsAgo = new Date();
        fiveYearsAgo.setFullYear(fiveYearsAgo.getFullYear() - 5);
        return date >= fiveYearsAgo;
      },
      'Date cannot be more than 5 years ago'
    ),

  // Job title with validation
  jobTitle: z
    .string({
      required_error: 'Job title is required',
    })
    .min(3, 'Job title must be at least 3 characters')
    .max(100, 'Job title must be less than 100 characters')
    .refine(
      (val: string) => val.trim().length > 0,
      'Job title cannot be empty'
    ),

  // Location (ZIP code)
  location: z
    .string({
      required_error: 'Location is required',
    })
    .regex(
      /^\d{5}(-\d{4})?$/,
      'Please enter a valid ZIP code (e.g., 12345 or 12345-6789)'
    ),

  // Experience level
  experienceLevel: z.enum(
    ['entry', 'mid', 'senior', 'executive'],
    {
      required_error: 'Please select your experience level',
      invalid_type_error: 'Please select a valid experience level',
    }
  ),

  // Company size
  companySize: z.enum(
    ['startup', 'small', 'medium', 'large', 'enterprise'],
    {
      required_error: 'Please select your company size',
      invalid_type_error: 'Please select a valid company size',
    }
  ),

  // Benefits (optional multi-select)
  benefits: z
    .array(z.string())
    .optional()
    .default([]),

  // Bonus amount (optional)
  bonusAmount: z
    .number()
    .min(0, 'Bonus amount cannot be negative')
    .max(1_000_000, 'Bonus amount must be less than $1,000,000')
    .optional()
    .or(z.literal('')),

  // Equity details (optional, for executive level)
  equityDetails: z
    .string()
    .max(500, 'Equity details must be less than 500 characters')
    .optional(),

  // Additional notes (optional)
  notes: z
    .string()
    .max(1000, 'Notes must be less than 1000 characters')
    .optional(),
});

// Infer TypeScript type from schema
export type SalaryFormData = z.infer<typeof salaryFormSchema>;

// Default values for form initialization
export const defaultSalaryFormValues: Partial<SalaryFormData> = {
  benefits: [],
  bonusAmount: undefined,
  equityDetails: '',
  notes: '',
};

// Validation helpers
export const validateJobTitle = (title: string): boolean => {
  return jobTitles.some(validTitle => 
    validTitle.toLowerCase().includes(title.toLowerCase()) ||
    title.toLowerCase().includes(validTitle.toLowerCase())
  );
};

export const validateZipCode = (zipCode: string): boolean => {
  return /^\d{5}(-\d{4})?$/.test(zipCode);
};

// Salary formatting helper
export const formatSalary = (value: number | string): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return '';
  return numValue.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
};

// Parse salary from formatted string
export const parseSalary = (formattedValue: string): number => {
  const numericValue = formattedValue.replace(/[^0-9.]/g, '');
  return parseFloat(numericValue) || 0;
};

// Form field configurations
export const formFieldConfigs = {
  currentSalary: {
    label: 'Current Annual Salary',
    placeholder: 'Enter your current salary',
    helpText: 'Your current base salary before taxes and deductions',
    required: true,
  },
  lastRaiseDate: {
    label: 'Last Raise Date',
    placeholder: 'Select date',
    helpText: 'When did you receive your last salary increase?',
    required: true,
  },
  jobTitle: {
    label: 'Job Title',
    placeholder: 'e.g., Software Engineer',
    helpText: 'Your current job title or role',
    required: true,
  },
  location: {
    label: 'Location (ZIP Code)',
    placeholder: '12345',
    helpText: 'ZIP code where you work for local market analysis',
    required: true,
  },
  experienceLevel: {
    label: 'Experience Level',
    helpText: 'Your professional experience level',
    required: true,
  },
  companySize: {
    label: 'Company Size',
    helpText: 'Number of employees at your company',
    required: true,
  },
  benefits: {
    label: 'Benefits Package',
    helpText: 'Select all benefits you receive (optional)',
    required: false,
  },
  bonusAmount: {
    label: 'Annual Bonus',
    placeholder: 'Enter bonus amount',
    helpText: 'Average annual bonus or incentive pay (optional)',
    required: false,
  },
  equityDetails: {
    label: 'Equity Details',
    placeholder: 'Stock options, RSUs, etc.',
    helpText: 'Details about equity compensation (optional)',
    required: false,
  },
  notes: {
    label: 'Additional Notes',
    placeholder: 'Any additional information...',
    helpText: 'Additional context about your compensation (optional)',
    required: false,
  },
} as const; 