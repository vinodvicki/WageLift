/**
 * Custom hook for salary form management with advanced validation
 * Provides form state, validation, and submission handling
 */

'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useForm, UseFormReturn } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  salaryFormSchema,
  type SalaryFormData,
  defaultSalaryFormValues,
  validateJobTitle,
  validateZipCode,
  formatSalary,
  parseSalary,
} from '@/lib/validations/salary-form';

// Hook options interface
interface UseSalaryFormOptions {
  initialData?: Partial<SalaryFormData>;
  onSubmit?: (data: SalaryFormData) => Promise<void>;
  onError?: (error: Error) => void;
  validateOnMount?: boolean;
  enableAutoSave?: boolean;
  autoSaveDelay?: number;
}

// Hook return type
interface UseSalaryFormReturn extends UseFormReturn<SalaryFormData> {
  // Form state
  isSubmitting: boolean;
  submitError: string | null;
  validationErrors: Record<string, string>;
  
  // Display values for formatted inputs
  salaryDisplay: string;
  bonusDisplay: string;
  
  // Handlers
  handleSalaryChange: (value: string) => void;
  handleBonusChange: (value: string) => void;
  handleSubmitForm: (data: SalaryFormData) => Promise<void>;
  clearErrors: () => void;
  resetForm: () => void;
  
  // Validation helpers
  validateField: (fieldName: keyof SalaryFormData, value: any) => Promise<boolean>;
  isFieldValid: (fieldName: keyof SalaryFormData) => boolean;
  getFieldError: (fieldName: keyof SalaryFormData) => string | undefined;
  
  // Form progress
  completionPercentage: number;
  completedFields: number;
  totalRequiredFields: number;
}

// Required fields for progress calculation
const REQUIRED_FIELDS: (keyof SalaryFormData)[] = [
  'currentSalary',
  'lastRaiseDate',
  'jobTitle',
  'location',
  'experienceLevel',
  'companySize',
];

// Async validation functions
const asyncValidators = {
  jobTitle: async (value: string): Promise<string | undefined> => {
    if (!value || value.length < 3) return undefined;
    
    // Simulate API call to validate job title
    await new Promise(resolve => setTimeout(resolve, 300));
    
    if (!validateJobTitle(value)) {
      return 'Job title not recognized. Please enter a valid job title.';
    }
    
    return undefined;
  },
  
  location: async (value: string): Promise<string | undefined> => {
    if (!value) return undefined;
    
    // Validate ZIP code format
    if (!validateZipCode(value)) {
      return 'Please enter a valid ZIP code (e.g., 12345 or 12345-6789)';
    }
    
    // Simulate API call to validate location
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Mock validation - in real app, this would call a geocoding API
    const invalidZipCodes = ['00000', '99999', '12345'];
    if (invalidZipCodes.indexOf(value) !== -1) {
      return 'ZIP code not found. Please enter a valid ZIP code.';
    }
    
    return undefined;
  },
  
  currentSalary: async (value: number): Promise<string | undefined> => {
    if (!value) return undefined;
    
    // Check against industry standards
    if (value < 25000) {
      return 'Salary seems low. Please verify the amount is correct.';
    }
    
    if (value > 1500000) {
      return 'Salary seems high. Please verify the amount is correct.';
    }
    
    return undefined;
  },
};

// Main hook implementation
export const useSalaryForm = (options: UseSalaryFormOptions = {}): UseSalaryFormReturn => {
  const {
    initialData,
    onSubmit,
    onError,
    validateOnMount = false,
    enableAutoSave = false,
    autoSaveDelay = 2000,
  } = options;

  // Form state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [salaryDisplay, setSalaryDisplay] = useState('');
  const [bonusDisplay, setBonusDisplay] = useState('');

  // Form setup
  const form = useForm<SalaryFormData>({
    resolver: zodResolver(salaryFormSchema),
    defaultValues: {
      ...defaultSalaryFormValues,
      ...initialData,
    },
    mode: 'onBlur',
    reValidateMode: 'onChange',
  });

  const {
    watch,
    setValue,
    setError,
    clearErrors: clearFormErrors,
    reset,
    formState: { errors, touchedFields, isValid },
  } = form;

  // Watch form values
  const watchedValues = watch();
  const currentSalary = watch('currentSalary');
  const bonusAmount = watch('bonusAmount');

  // Initialize display values
  useEffect(() => {
    if (currentSalary) {
      setSalaryDisplay(formatSalary(currentSalary));
    }
    if (bonusAmount) {
      setBonusDisplay(formatSalary(bonusAmount));
    }
  }, [currentSalary, bonusAmount]);

  // Handle salary input formatting
  const handleSalaryChange = useCallback((value: string) => {
    const numericValue = parseSalary(value);
    setSalaryDisplay(formatSalary(numericValue));
    setValue('currentSalary', numericValue, { 
      shouldValidate: true, 
      shouldDirty: true 
    });
  }, [setValue]);

  // Handle bonus input formatting
  const handleBonusChange = useCallback((value: string) => {
    const numericValue = parseSalary(value);
    setBonusDisplay(formatSalary(numericValue));
    setValue('bonusAmount', numericValue, { 
      shouldValidate: true, 
      shouldDirty: true 
    });
  }, [setValue]);

  // Async field validation
  const validateField = useCallback(async (
    fieldName: keyof SalaryFormData, 
    value: any
  ): Promise<boolean> => {
    const validator = asyncValidators[fieldName as keyof typeof asyncValidators];
    if (!validator) return true;

    try {
      const error = await validator(value);
      if (error) {
        setValidationErrors(prev => ({ ...prev, [fieldName]: error }));
        setError(fieldName, { type: 'async', message: error });
        return false;
      } else {
        setValidationErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors[fieldName];
          return newErrors;
        });
        return true;
      }
    } catch (error) {
      console.error(`Validation error for ${fieldName}:`, error);
      return false;
    }
  }, [setError]);

  // Check if field is valid
  const isFieldValid = useCallback((fieldName: keyof SalaryFormData): boolean => {
    return !errors[fieldName] && !validationErrors[fieldName];
  }, [errors, validationErrors]);

  // Get field error message
  const getFieldError = useCallback((fieldName: keyof SalaryFormData): string | undefined => {
    return errors[fieldName]?.message || validationErrors[fieldName];
  }, [errors, validationErrors]);

  // Calculate form completion
  const { completionPercentage, completedFields, totalRequiredFields } = useMemo(() => {
    const completed = REQUIRED_FIELDS.filter(field => {
      const value = watchedValues[field];
      return value !== undefined && value !== null && value !== '';
    }).length;
    
    const total = REQUIRED_FIELDS.length;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    return {
      completionPercentage: percentage,
      completedFields: completed,
      totalRequiredFields: total,
    };
  }, [watchedValues]);

  // Form submission handler
  const handleSubmitForm = useCallback(async (data: SalaryFormData) => {
    if (!onSubmit) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Run async validations before submission
      const validationPromises = Object.keys(data).map((field) => 
        validateField(field as keyof SalaryFormData, data[field as keyof SalaryFormData])
      );
      
      const validationResults = await Promise.all(validationPromises);
      const hasValidationErrors = validationResults.some(result => !result);
      
      if (hasValidationErrors) {
        throw new Error('Please fix validation errors before submitting');
      }

      await onSubmit(data);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
      setSubmitError(errorMessage);
      onError?.(error instanceof Error ? error : new Error(errorMessage));
    } finally {
      setIsSubmitting(false);
    }
  }, [onSubmit, onError, validateField]);

  // Clear all errors
  const clearErrors = useCallback(() => {
    clearFormErrors();
    setValidationErrors({});
    setSubmitError(null);
  }, [clearFormErrors]);

  // Reset form
  const resetForm = useCallback(() => {
    reset();
    setSalaryDisplay('');
    setBonusDisplay('');
    clearErrors();
  }, [reset, clearErrors]);

  // Auto-save functionality
  useEffect(() => {
    if (!enableAutoSave) return;

    const timeoutId = setTimeout(() => {
      const formData = watchedValues;
      // Save to localStorage or call API
      localStorage.setItem('salary-form-draft', JSON.stringify(formData));
    }, autoSaveDelay);

    return () => clearTimeout(timeoutId);
  }, [watchedValues, enableAutoSave, autoSaveDelay]);

  // Validate on mount if requested
  useEffect(() => {
    if (validateOnMount) {
      form.trigger();
    }
  }, [validateOnMount, form]);

  return {
    ...form,
    isSubmitting,
    submitError,
    validationErrors,
    salaryDisplay,
    bonusDisplay,
    handleSalaryChange,
    handleBonusChange,
    handleSubmitForm,
    clearErrors,
    resetForm,
    validateField,
    isFieldValid,
    getFieldError,
    completionPercentage,
    completedFields,
    totalRequiredFields,
  };
};

export default useSalaryForm; 