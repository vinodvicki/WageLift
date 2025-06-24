/**
 * CPI Gap Display Component for WageLift
 * Shows inflation-adjusted salary gaps with visual indicators
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  InformationCircleIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import { 
  useCPIApi,
  type CPICalculationData,
  type CPICalculationRequest,
  formatCurrency,
  formatPercentage,
  formatInflationRate,
  getGapStatus,
  getGapStatusMessage,
  handleCPIApiError
} from '@/lib/api/cpi';

// Component Props
interface CPIGapDisplayProps {
  originalSalary: number;
  currentSalary: number;
  historicalDate: string;
  currentDate?: string;
  className?: string;
  showDetails?: boolean;
  autoCalculate?: boolean;
}

interface GapVisualizationProps {
  data: CPICalculationData;
  isLoading?: boolean;
}

// Gap Status Visual Component Props
interface GapStatusIndicatorProps {
  status: 'positive' | 'negative' | 'neutral';
  percentageGap: number;
  dollarGap: number;
  className?: string;
}

const GapStatusIndicator: React.FC<GapStatusIndicatorProps> = ({ 
  status, 
  percentageGap, 
  dollarGap, 
  className 
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'positive':
        return {
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          textColor: 'text-green-800',
          label: 'Above Inflation',
          description: 'Your salary is keeping up with inflation',
          icon: '↗'
        };
      case 'negative':
        return {
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-800',
          label: 'Below Inflation',
          description: 'Your salary is losing purchasing power',
          icon: '↘'
        };
      case 'neutral':
        return {
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          textColor: 'text-gray-800',
          label: 'On Pace with Inflation',
          description: 'Your salary matches inflation expectations',
          icon: '→'
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={clsx(
      'flex items-center space-x-3 p-4 rounded-lg border',
      config.bgColor,
      config.borderColor,
      className
    )}>
      <div className={clsx(
        'flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold',
        config.bgColor,
        config.textColor
      )}>
        {config.icon}
      </div>
      <div className="flex-1">
        <h3 className={clsx('font-semibold text-sm', config.textColor)}>
          {config.label}
        </h3>
        <p className={clsx('text-xs', config.textColor, 'opacity-80')}>
          {config.description}
        </p>
      </div>
      <div className="text-right">
        <div className={clsx('font-bold text-lg', config.textColor)}>
          {formatPercentage(percentageGap)}
        </div>
        <div className={clsx('text-sm font-medium', config.textColor)}>
          {formatCurrency(Math.abs(dollarGap))}
        </div>
      </div>
    </div>
  );
};

// Main Gap Visualization Component
const GapVisualization: React.FC<GapVisualizationProps> = ({ 
  data, 
  isLoading = false
}) => {
  const gapStatus = getGapStatus(data.percentage_gap);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-20 bg-gray-200 rounded-lg"></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="animate-pulse h-16 bg-gray-200 rounded-lg"></div>
          <div className="animate-pulse h-16 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Main Status Indicator */}
      <GapStatusIndicator
        status={gapStatus}
        percentageGap={data.percentage_gap}
        dollarGap={data.dollar_gap}
      />

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Inflation-Adjusted Salary */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-blue-600 text-xl">🧮</span>
            <h4 className="font-semibold text-gray-900">Inflation-Adjusted Salary</h4>
          </div>
          <div className="space-y-2">
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(data.adjusted_salary)}
            </div>
            <div className="text-sm text-gray-600">
              Based on {formatInflationRate(data.inflation_rate)} inflation over {data.years_elapsed.toFixed(1)} years
            </div>
          </div>
        </div>

        {/* Current vs Expected */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-purple-600 text-xl">📊</span>
            <h4 className="font-semibold text-gray-900">Salary Comparison</h4>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Current Salary:</span>
              <span className="font-semibold">{formatCurrency(data.current_salary)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Expected (Inflation-Adjusted):</span>
              <span className="font-semibold">{formatCurrency(data.adjusted_salary)}</span>
            </div>
            <div className="border-t pt-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-900">Difference:</span>
                <span className={clsx(
                  'font-bold',
                  gapStatus === 'positive' ? 'text-green-600' :
                  gapStatus === 'negative' ? 'text-red-600' : 'text-gray-600'
                )}>
                  {data.dollar_gap >= 0 ? '+' : ''}{formatCurrency(data.dollar_gap)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Gap Message */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <InformationCircleIcon className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            {getGapStatusMessage(data.percentage_gap, data.dollar_gap)}
          </div>
        </div>
      </div>
    </div>
  );
};

// Calculation Metrics Component
const CalculationMetrics: React.FC<{
  data: CPICalculationData;
  className?: string;
}> = ({ data, className }) => {
  return (
    <div className={clsx('bg-gray-50 rounded-lg p-4', className)}>
      <h4 className="font-medium text-gray-900 mb-3">Calculation Details</h4>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-600">Time Period:</span>
          <div className="font-medium">{data.years_elapsed.toFixed(1)} years</div>
        </div>
        <div>
          <span className="text-gray-600">Inflation Rate:</span>
          <div className="font-medium">{formatInflationRate(data.inflation_rate)}</div>
        </div>
        <div>
          <span className="text-gray-600">Method:</span>
          <div className="font-medium capitalize">{data.calculation_method}</div>
        </div>
        <div>
          <span className="text-gray-600">Calculated:</span>
          <div className="font-medium">{new Date(data.calculation_date).toLocaleDateString()}</div>
        </div>
      </div>
    </div>
  );
};

// Main CPI Gap Display Component
export const CPIGapDisplay: React.FC<CPIGapDisplayProps> = ({
  originalSalary,
  currentSalary,
  historicalDate,
  currentDate,
  className,
  showDetails = true,
  autoCalculate = true
}) => {
  const [calculationData, setCalculationData] = useState<CPICalculationData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { calculateSalaryGap } = useCPIApi();

  const performCalculation = async () => {
    if (!originalSalary || !currentSalary || !historicalDate) {
      setError('Missing required data for calculation');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const request: CPICalculationRequest = {
        original_salary: originalSalary,
        current_salary: currentSalary,
        historical_date: historicalDate,
        current_date: currentDate
      };

      const response = await calculateSalaryGap(request);
      setCalculationData(response.data);
    } catch (err) {
      setError(handleCPIApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (autoCalculate && originalSalary && currentSalary && historicalDate) {
      performCalculation();
    }
  }, [originalSalary, currentSalary, historicalDate, currentDate, autoCalculate]);

  return (
    <div className={clsx('space-y-6', className)}>
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Inflation Impact Analysis
        </h2>
        <p className="text-gray-600">
          See how inflation has affected your purchasing power over time
        </p>
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-start">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-red-800 mb-1">
                Calculation Error
              </h3>
              <p className="text-sm text-red-700 whitespace-pre-line">{error}</p>
              <button
                onClick={performCalculation}
                className="mt-3 inline-flex items-center px-3 py-1.5 text-sm font-medium text-red-700 bg-white border border-red-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Manual Calculate Button (if not auto-calculating) */}
      {!autoCalculate && !calculationData && !isLoading && !error && (
        <div className="text-center">
          <button
            onClick={performCalculation}
            className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <span className="mr-2">🧮</span>
            Calculate Inflation Impact
          </button>
        </div>
      )}

      {/* Results */}
      {(calculationData || isLoading) && (
        <div className="space-y-6">
          <GapVisualization 
            data={calculationData!} 
            isLoading={isLoading}
          />
          
          {/* Detailed Metrics */}
          {showDetails && calculationData && (
            <CalculationMetrics data={calculationData} />
          )}
        </div>
      )}

      {/* Success State for No Data */}
      {!isLoading && !error && !calculationData && autoCalculate && (
        <div className="text-center py-8">
          <CheckCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Calculate</h3>
          <p className="text-gray-600">
            Provide salary information to see your inflation impact analysis
          </p>
        </div>
      )}
    </div>
  );
};

export default CPIGapDisplay; 