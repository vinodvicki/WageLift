'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { errorService, ErrorCode } from '@/services/error-service';
import { useToastHelpers } from '@/components/ui/toast';
import { Save, AlertCircle } from 'lucide-react';

interface CrashProofFormProps<T> {
  children: (props: {
    values: T;
    errors: Record<string, string>;
    touched: Record<string, boolean>;
    isSubmitting: boolean;
    isDirty: boolean;
    setValue: (field: keyof T, value: any) => void;
    setError: (field: string, error: string) => void;
    handleSubmit: (e: React.FormEvent) => void;
    resetForm: () => void;
  }) => React.ReactNode;
  initialValues: T;
  onSubmit: (values: T) => Promise<void> | void;
  validate?: (values: T) => Record<string, string>;
  autoSaveInterval?: number;
  storageKey?: string;
  maxRetries?: number;
}

export function CrashProofForm<T extends Record<string, any>>({
  children,
  initialValues,
  onSubmit,
  validate,
  autoSaveInterval = 5000,
  storageKey = 'crash-proof-form',
  maxRetries = 3,
}: CrashProofFormProps<T>) {
  const toast = useToastHelpers();
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const retryCount = useRef(0);
  const autoSaveTimer = useRef<NodeJS.Timeout>();

  // Load saved form data on mount
  useEffect(() => {
    try {
      const savedData = localStorage.getItem(storageKey);
      if (savedData) {
        const parsed = JSON.parse(savedData);
        if (parsed.timestamp && Date.now() - parsed.timestamp < 24 * 60 * 60 * 1000) {
          setValues(parsed.values);
          setIsDirty(true);
          toast.info('Form data restored', 'Your previous progress has been loaded.');
        }
      }
    } catch (error) {
      console.error('Failed to load saved form data:', error);
    }
  }, [storageKey, toast]);

  // Auto-save functionality
  useEffect(() => {
    if (isDirty && autoSaveInterval > 0) {
      if (autoSaveTimer.current) {
        clearTimeout(autoSaveTimer.current);
      }

      autoSaveTimer.current = setTimeout(() => {
        try {
          localStorage.setItem(
            storageKey,
            JSON.stringify({
              values,
              timestamp: Date.now(),
            })
          );
          setLastSaved(new Date());
        } catch (error) {
          console.error('Failed to auto-save form data:', error);
        }
      }, autoSaveInterval);
    }

    return () => {
      if (autoSaveTimer.current) {
        clearTimeout(autoSaveTimer.current);
      }
    };
  }, [values, isDirty, autoSaveInterval, storageKey]);

  const setValue = useCallback((field: keyof T, value: any) => {
    setValues(prev => ({
      ...prev,
      [field]: value,
    }));
    setTouched(prev => ({
      ...prev,
      [field as string]: true,
    }));
    setIsDirty(true);
    
    // Clear field error when value changes
    if (errors[field as string]) {
      setErrors(prev => {
        const next = { ...prev };
        delete next[field as string];
        return next;
      });
    }
  }, [errors]);

  const setError = useCallback((field: string, error: string) => {
    setErrors(prev => ({
      ...prev,
      [field]: error,
    }));
  }, []);

  const validateForm = useCallback(() => {
    if (!validate) return {};
    
    const validationErrors = validate(values);
    setErrors(validationErrors);
    return validationErrors;
  }, [validate, values]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate all fields
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      toast.error('Validation failed', 'Please fix the errors before submitting.');
      return;
    }

    setIsSubmitting(true);
    retryCount.current = 0;

    const submitWithRetry = async (): Promise<void> => {
      try {
        await onSubmit(values);
        
        // Clear saved data on successful submit
        localStorage.removeItem(storageKey);
        setIsDirty(false);
        toast.success('Success', 'Your form has been submitted successfully.');
        
      } catch (error) {
        const wageLiftError = errorService.handleError(error, 'Form submission');
        
        // Retry if the error is retryable and we haven't exceeded max retries
        if (wageLiftError.retryable && retryCount.current < maxRetries) {
          retryCount.current++;
          toast.warning(
            'Retrying submission',
            `Attempt ${retryCount.current + 1} of ${maxRetries + 1}`
          );
          
          // Exponential backoff
          await new Promise(resolve => 
            setTimeout(resolve, Math.pow(2, retryCount.current) * 1000)
          );
          
          return submitWithRetry();
        }
        
        // Show user-friendly error message
        toast.error(
          'Submission failed',
          errorService.getUserFriendlyMessage(wageLiftError)
        );
        
        throw error;
      }
    };

    try {
      await submitWithRetry();
    } finally {
      setIsSubmitting(false);
    }
  }, [values, validateForm, onSubmit, storageKey, maxRetries, toast]);

  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsDirty(false);
    localStorage.removeItem(storageKey);
    toast.info('Form reset', 'All fields have been cleared.');
  }, [initialValues, storageKey, toast]);

  return (
    <div className="relative">
      {/* Auto-save indicator */}
      {isDirty && lastSaved && (
        <div className="absolute -top-8 right-0 flex items-center text-sm text-gray-500">
          <Save className="h-4 w-4 mr-1" />
          Last saved: {lastSaved.toLocaleTimeString()}
        </div>
      )}

      {/* Form content */}
      {children({
        values,
        errors,
        touched,
        isSubmitting,
        isDirty,
        setValue,
        setError,
        handleSubmit,
        resetForm,
      })}

      {/* Global form error indicator */}
      {Object.keys(errors).length > 0 && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-start">
          <AlertCircle className="h-5 w-5 text-red-400 mr-2 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-red-700">
            Please fix the errors above before submitting.
          </div>
        </div>
      )}
    </div>
  );
}

// Example usage component
export function ExampleCrashProofForm() {
  return (
    <CrashProofForm
      initialValues={{
        name: '',
        email: '',
        message: '',
      }}
      validate={(values) => {
        const errors: Record<string, string> = {};
        if (!values['name']) errors['name'] = 'Name is required';
        if (!values['email']) errors['email'] = 'Email is required';
        if (values['email'] && !values['email'].includes('@')) {
          errors['email'] = 'Invalid email address';
        }
        if (!values['message']) errors['message'] = 'Message is required';
        return errors;
      }}
      onSubmit={async (values) => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000));
        console.log('Form submitted:', values);
      }}
    >
      {({ values, errors, touched, isSubmitting, setValue, handleSubmit }) => (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Name
            </label>
            <input
              type="text"
              value={values['name']}
              onChange={(e) => setValue('name', e.target.value)}
              className={`mt-1 block w-full rounded-md border ${
                errors['name'] && touched['name']
                  ? 'border-red-300'
                  : 'border-gray-300'
              } px-3 py-2`}
            />
            {errors['name'] && touched['name'] && (
              <p className="mt-1 text-sm text-red-600">{errors['name']}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
        </form>
      )}
    </CrashProofForm>
  );
}