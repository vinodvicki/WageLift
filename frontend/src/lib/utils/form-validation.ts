/**
 * Comprehensive form validation utilities for salary form
 * Provides validation rules, error handling, and user feedback
 */

// Validation result interface
export interface ValidationResult {
  isValid: boolean;
  error?: string;
  warning?: string;
  suggestion?: string;
}

// Field validation functions
export const validators = {
  // Salary validation with industry standards
  salary: (value: number): ValidationResult => {
    if (!value || value <= 0) {
      return { isValid: false, error: 'Salary is required and must be greater than 0' };
    }
    
    if (value < 20000) {
      return { 
        isValid: true, 
        warning: 'This salary seems low. Please verify the amount is correct.',
        suggestion: 'Consider if this is hourly wage that needs to be annualized'
      };
    }
    
    if (value > 2000000) {
      return { 
        isValid: true, 
        warning: 'This salary seems very high. Please verify the amount is correct.',
                 suggestion: 'Ensure you are entering annual salary, not total compensation'
      };
    }
    
    return { isValid: true };
  },

  // Job title validation
  jobTitle: (value: string): ValidationResult => {
    if (!value || value.trim().length === 0) {
      return { isValid: false, error: 'Job title is required' };
    }
    
    if (value.trim().length < 2) {
      return { isValid: false, error: 'Job title must be at least 2 characters long' };
    }
    
    if (value.length > 100) {
      return { isValid: false, error: 'Job title must be less than 100 characters' };
    }
    
    // Check for valid characters
    const validJobTitleRegex = /^[a-zA-Z0-9\\s\\-\\.\\/\\&\\(\\)]+$/;
    if (!validJobTitleRegex.test(value)) {
      return { 
        isValid: false, 
        error: 'Job title contains invalid characters',
        suggestion: 'Use only letters, numbers, spaces, and common punctuation'
      };
    }
    
    return { isValid: true };
  },

  // ZIP code validation
  zipCode: (value: string): ValidationResult => {
    if (!value || value.trim().length === 0) {
      return { isValid: false, error: 'ZIP code is required' };
    }
    
    // US ZIP code formats: 12345 or 12345-6789
    const zipRegex = /^\\d{5}(-\\d{4})?$/;
    if (!zipRegex.test(value.trim())) {
      return { 
        isValid: false, 
        error: 'Please enter a valid ZIP code',
        suggestion: 'Format: 12345 or 12345-6789'
      };
    }
    
    return { isValid: true };
  },

  // Date validation
  date: (value: Date | string, maxYearsAgo: number = 5): ValidationResult => {
    if (!value) {
      return { isValid: false, error: 'Date is required' };
    }
    
    const date = typeof value === 'string' ? new Date(value) : value;
    
    if (isNaN(date.getTime())) {
      return { isValid: false, error: 'Please enter a valid date' };
    }
    
    const now = new Date();
    const maxPastDate = new Date();
    maxPastDate.setFullYear(now.getFullYear() - maxYearsAgo);
    
    if (date > now) {
      return { isValid: false, error: 'Date cannot be in the future' };
    }
    
    if (date < maxPastDate) {
      return { 
        isValid: false, 
        error: `Date cannot be more than ${maxYearsAgo} years ago`,
        suggestion: 'If this is correct, please provide additional context in notes'
      };
    }
    
    return { isValid: true };
  },

  // Experience level validation
  experienceLevel: (value: string): ValidationResult => {
    const validLevels = ['entry', 'mid', 'senior', 'lead', 'executive'];
    
    if (!value) {
      return { isValid: false, error: 'Experience level is required' };
    }
    
    if (validLevels.indexOf(value) === -1) {
      return { 
        isValid: false, 
        error: 'Please select a valid experience level',
        suggestion: 'Choose from: Entry, Mid-level, Senior, Lead, or Executive'
      };
    }
    
    return { isValid: true };
  },

  // Company size validation
  companySize: (value: string): ValidationResult => {
    const validSizes = ['startup', 'small', 'medium', 'large', 'enterprise'];
    
    if (!value) {
      return { isValid: false, error: 'Company size is required' };
    }
    
    if (validSizes.indexOf(value) === -1) {
      return { 
        isValid: false, 
        error: 'Please select a valid company size',
        suggestion: 'Choose from the available options'
      };
    }
    
    return { isValid: true };
  },

  // Bonus validation
  bonus: (value: number, salary: number): ValidationResult => {
    if (value < 0) {
      return { isValid: false, error: 'Bonus amount cannot be negative' };
    }
    
    // Warning if bonus seems disproportionate to salary
    if (salary && value > salary * 2) {
      return { 
        isValid: true, 
        warning: 'This bonus amount seems very high compared to salary',
        suggestion: 'Please verify this includes all bonuses for the year'
      };
    }
    
    return { isValid: true };
  },
};

// Cross-field validation functions
export const crossValidators = {
  // Validate salary vs experience level
  salaryExperience: (salary: number, experienceLevel: string): ValidationResult => {
    const baselines = {
      'entry': { min: 35000, max: 80000 },
      'mid': { min: 60000, max: 120000 },
      'senior': { min: 90000, max: 180000 },
      'lead': { min: 120000, max: 250000 },
      'executive': { min: 150000, max: 500000 },
    };
    
    const baseline = baselines[experienceLevel as keyof typeof baselines];
    if (!baseline) return { isValid: true };
    
    if (salary < baseline.min) {
      return {
        isValid: true,
        warning: `Salary seems low for ${experienceLevel} level`,
        suggestion: `Typical range: $${baseline.min.toLocaleString()} - $${baseline.max.toLocaleString()}`
      };
    }
    
    if (salary > baseline.max) {
      return {
        isValid: true,
        warning: `Salary seems high for ${experienceLevel} level`,
        suggestion: 'This may indicate exceptional performance or specialized skills'
      };
    }
    
    return { isValid: true };
  },
  
  // Validate bonus vs company size
  bonusCompanySize: (bonus: number, companySize: string, salary: number): ValidationResult => {
    if (!bonus || bonus === 0) return { isValid: true };
    
    const bonusPercentage = (bonus / salary) * 100;
    const expectedRanges = {
      'startup': { typical: 5, max: 15 },
      'small': { typical: 8, max: 20 },
      'medium': { typical: 10, max: 25 },
      'large': { typical: 12, max: 30 },
      'enterprise': { typical: 15, max: 40 },
    };
    
    const range = expectedRanges[companySize as keyof typeof expectedRanges];
    if (!range) return { isValid: true };
    
    if (bonusPercentage > range.max) {
      return {
        isValid: true,
        warning: `${bonusPercentage.toFixed(1)}% bonus is unusually high for ${companySize} companies`,
        suggestion: `Typical range: 0-${range.max}% of salary`
      };
    }
    
    return { isValid: true };
  },
};

// Form validation orchestrator
export interface FormValidationResult {
  isValid: boolean;
  fieldErrors: Record<string, string>;
  fieldWarnings: Record<string, string>;
  fieldSuggestions: Record<string, string>;
  crossFieldWarnings: string[];
}

export const validateSalaryForm = (data: any): FormValidationResult => {
  const result: FormValidationResult = {
    isValid: true,
    fieldErrors: {},
    fieldWarnings: {},
    fieldSuggestions: {},
    crossFieldWarnings: [],
  };
  
  // Validate individual fields
  const fieldValidations = [
    { field: 'currentSalary', validator: validators.salary, value: data.currentSalary },
    { field: 'jobTitle', validator: validators.jobTitle, value: data.jobTitle },
    { field: 'location', validator: validators.zipCode, value: data.location },
    { field: 'lastRaiseDate', validator: validators.date, value: data.lastRaiseDate },
    { field: 'experienceLevel', validator: validators.experienceLevel, value: data.experienceLevel },
    { field: 'companySize', validator: validators.companySize, value: data.companySize },
  ];
  
  fieldValidations.forEach(({ field, validator, value }) => {
    const validation = validator(value);
    
    if (!validation.isValid) {
      result.isValid = false;
      if (validation.error) {
        result.fieldErrors[field] = validation.error;
      }
    }
    
    if (validation.warning) {
      result.fieldWarnings[field] = validation.warning;
    }
    
    if (validation.suggestion) {
      result.fieldSuggestions[field] = validation.suggestion;
    }
  });
  
  // Validate bonus if provided
  if (data.bonusAmount && data.bonusAmount > 0) {
    const bonusValidation = validators.bonus(data.bonusAmount, data.currentSalary);
    if (!bonusValidation.isValid) {
      result.isValid = false;
      if (bonusValidation.error) {
        result.fieldErrors['bonusAmount'] = bonusValidation.error;
      }
    }
    if (bonusValidation.warning) {
      result.fieldWarnings['bonusAmount'] = bonusValidation.warning;
    }
  }
  
  // Cross-field validations
  if (data.currentSalary && data.experienceLevel) {
    const crossValidation = crossValidators.salaryExperience(data.currentSalary, data.experienceLevel);
    if (crossValidation.warning) {
      result.crossFieldWarnings.push(crossValidation.warning);
      if (crossValidation.suggestion) {
        result.crossFieldWarnings.push(crossValidation.suggestion);
      }
    }
  }
  
  if (data.bonusAmount && data.companySize && data.currentSalary) {
    const bonusCrossValidation = crossValidators.bonusCompanySize(
      data.bonusAmount, 
      data.companySize, 
      data.currentSalary
    );
    if (bonusCrossValidation.warning) {
      result.crossFieldWarnings.push(bonusCrossValidation.warning);
    }
  }
  
  return result;
};

// Validation error formatting utilities
export const formatValidationError = (error: string, field: string): string => {
  const fieldLabels: Record<string, string> = {
    currentSalary: 'Current Salary',
    jobTitle: 'Job Title',
    location: 'Location (ZIP Code)',
    lastRaiseDate: 'Last Raise Date',
    experienceLevel: 'Experience Level',
    companySize: 'Company Size',
    bonusAmount: 'Bonus Amount',
  };
  
  const label = fieldLabels[field] || field;
  return `${label}: ${error}`;
};

export const formatValidationWarning = (warning: string): string => {
  return `⚠️ ${warning}`;
};

export const formatValidationSuggestion = (suggestion: string): string => {
  return `💡 ${suggestion}`;
};

// Real-time validation debouncer
export const createDebouncedValidator = (validator: Function, delay: number = 300) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: any[]) => {
    return new Promise((resolve) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        resolve(validator(...args));
      }, delay);
    });
  };
}; 