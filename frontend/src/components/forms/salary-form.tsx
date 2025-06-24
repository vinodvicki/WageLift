/**
 * Comprehensive salary form component with React Hook Form and Tailwind CSS
 * Implements mobile-first design with accessibility and validation
 */

'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  salaryFormSchema,
  type SalaryFormData,
  defaultSalaryFormValues,
  experienceLevels,
  companySizes,
  benefitsOptions,
  formFieldConfigs,
  formatSalary,
  parseSalary,
} from '@/lib/validations/salary-form';

// Props interface
interface SalaryFormProps {
  onSubmit: (data: SalaryFormData) => void;
  isLoading?: boolean;
  initialData?: Partial<SalaryFormData>;
}

// Main salary form component
export function SalaryForm({ onSubmit, isLoading = false, initialData }: SalaryFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<SalaryFormData>({
    resolver: zodResolver(salaryFormSchema),
    defaultValues: {
      ...defaultSalaryFormValues,
      ...initialData,
    },
  });

  const currentSalary = watch('currentSalary');

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Current Salary */}
          <div>
            <label htmlFor="currentSalary" className="block text-sm font-medium text-gray-700">
              Current Annual Salary *
            </label>
            <div className="mt-1 relative rounded-md shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span className="text-gray-500 sm:text-sm">$</span>
              </div>
              <input
                {...register('currentSalary', { valueAsNumber: true })}
                type="number"
                id="currentSalary"
                className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 rounded-md"
                placeholder="75000"
                min="20000"
                max="2000000"
                step="1000"
              />
            </div>
            {errors.currentSalary && (
              <p className="mt-1 text-sm text-red-600">{errors.currentSalary.message}</p>
            )}
            {currentSalary && (
              <p className="mt-1 text-sm text-gray-500">
                {formatCurrency(currentSalary)} annually
              </p>
            )}
          </div>

          {/* Last Raise Date */}
          <div>
            <label htmlFor="lastRaiseDate" className="block text-sm font-medium text-gray-700">
              Last Raise Date *
            </label>
            <input
              {...register('lastRaiseDate', { valueAsDate: true })}
              type="date"
              id="lastRaiseDate"
              className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
              max={new Date().toISOString().split('T')[0]}
            />
            {errors.lastRaiseDate && (
              <p className="mt-1 text-sm text-red-600">{errors.lastRaiseDate.message}</p>
            )}
          </div>

          {/* Job Title */}
          <div>
            <label htmlFor="jobTitle" className="block text-sm font-medium text-gray-700">
              Job Title *
            </label>
            <input
              {...register('jobTitle')}
              type="text"
              id="jobTitle"
              className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
              placeholder="Software Engineer"
            />
            {errors.jobTitle && (
              <p className="mt-1 text-sm text-red-600">{errors.jobTitle.message}</p>
            )}
          </div>

          {/* Location */}
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700">
              Location (ZIP Code) *
            </label>
            <input
              {...register('location')}
              type="text"
              id="location"
              className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
              placeholder="12345"
              pattern="[0-9]{5}(-[0-9]{4})?"
            />
            {errors.location && (
              <p className="mt-1 text-sm text-red-600">{errors.location.message}</p>
            )}
          </div>

          {/* Experience Level */}
          <div>
            <label htmlFor="experienceLevel" className="block text-sm font-medium text-gray-700">
              Experience Level *
            </label>
            <select
              {...register('experienceLevel')}
              id="experienceLevel"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="">Select experience level</option>
              <option value="entry">Entry Level (0-2 years)</option>
              <option value="mid">Mid Level (3-5 years)</option>
              <option value="senior">Senior Level (6-10 years)</option>
              <option value="executive">Executive Level (10+ years)</option>
            </select>
            {errors.experienceLevel && (
              <p className="mt-1 text-sm text-red-600">{errors.experienceLevel.message}</p>
            )}
          </div>

          {/* Company Size */}
          <div>
            <label htmlFor="companySize" className="block text-sm font-medium text-gray-700">
              Company Size *
            </label>
            <select
              {...register('companySize')}
              id="companySize"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="">Select company size</option>
              <option value="startup">Startup (1-50 employees)</option>
              <option value="small">Small (51-200 employees)</option>
              <option value="medium">Medium (201-1000 employees)</option>
              <option value="large">Large (1001-5000 employees)</option>
              <option value="enterprise">Enterprise (5000+ employees)</option>
            </select>
            {errors.companySize && (
              <p className="mt-1 text-sm text-red-600">{errors.companySize.message}</p>
            )}
          </div>
        </div>

        {/* Bonus Amount */}
        <div>
          <label htmlFor="bonusAmount" className="block text-sm font-medium text-gray-700">
            Annual Bonus Amount (Optional)
          </label>
          <div className="mt-1 relative rounded-md shadow-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              {...register('bonusAmount', { valueAsNumber: true })}
              type="number"
              id="bonusAmount"
              className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 rounded-md"
              placeholder="10000"
              min="0"
              max="1000000"
              step="1000"
            />
          </div>
          {errors.bonusAmount && (
            <p className="mt-1 text-sm text-red-600">{errors.bonusAmount.message}</p>
          )}
        </div>

        {/* Notes */}
        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
            Additional Notes (Optional)
          </label>
          <textarea
            {...register('notes')}
            id="notes"
            rows={3}
            className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            placeholder="Any additional context about your role, achievements, or circumstances..."
          />
          {errors.notes && (
            <p className="mt-1 text-sm text-red-600">{errors.notes.message}</p>
          )}
        </div>

        {/* Submit Button */}
        <div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Calculating...' : 'Calculate Salary Analysis'}
          </button>
        </div>
      </form>
    </div>
  );
} 