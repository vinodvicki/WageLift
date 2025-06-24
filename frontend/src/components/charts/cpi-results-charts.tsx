/**
 * CPI Results Charts Component
 * Beautiful data visualizations for salary and inflation analysis using Recharts
 */

'use client';

import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface CPICalculationData {
  adjusted_salary: number;
  percentage_gap: number;
  dollar_gap: number;
  original_salary: number;
  current_salary: number;
  inflation_rate: number;
  years_elapsed: number;
  calculation_method: string;
  calculation_date: string;
  historical_date: string;
  current_date: string;
}

interface SalaryEntry {
  id: string;
  current_salary: number;
  created_at: string;
}

interface CPIResultsChartsProps {
  cpiData: CPICalculationData;
  salaryHistory: SalaryEntry[];
  selectedTimeframe: string;
  className?: string;
}

// Custom tooltip component for better formatting
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
        <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            <span className="font-medium">{entry.name}:</span>{' '}
            {entry.name.includes('Salary') || entry.name.includes('Gap') 
              ? `$${entry.value.toLocaleString()}`
              : `${entry.value.toFixed(1)}%`
            }
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// Format currency for axis labels
const formatCurrency = (value: number) => {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(1)}M`;
  } else if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`;
  }
  return `$${value.toLocaleString()}`;
};

// Format percentage for axis labels
const formatPercentage = (value: number) => `${value.toFixed(1)}%`;

export const CPIResultsCharts: React.FC<CPIResultsChartsProps> = ({
  cpiData,
  salaryHistory,
  selectedTimeframe,
  className = ''
}) => {
  const salaryComparisonData = [
    {
      category: 'Original',
      value: cpiData.original_salary
    },
    {
      category: 'Adjusted',
      value: cpiData.adjusted_salary
    },
    {
      category: 'Current',
      value: cpiData.current_salary
    }
  ];

  // Prepare data for trend analysis (simplified for demo)
  const trendData = React.useMemo(() => {
    const data = [];
    const startYear = new Date(cpiData.historical_date).getFullYear();
    const endYear = new Date(cpiData.current_date).getFullYear();
    const yearsDiff = endYear - startYear;
    
    for (let i = 0; i <= yearsDiff; i++) {
      const year = startYear + i;
      const progress = i / yearsDiff;
      
      // Calculate interpolated values
      const currentSalary = cpiData.original_salary + 
        (cpiData.current_salary - cpiData.original_salary) * progress;
      const adjustedSalary = cpiData.original_salary * 
        Math.pow(1 + (cpiData.inflation_rate / 100) / yearsDiff, i);
      
      data.push({
        year: year.toString(),
        'Current Salary': Math.round(currentSalary),
        'Inflation-Adjusted Salary': Math.round(adjustedSalary),
        'Purchasing Power Gap': Math.round(adjustedSalary - currentSalary)
      });
    }
    
    return data;
  }, [cpiData]);

  // Prepare purchasing power data
  const purchasingPowerData = [
    {
      period: cpiData.historical_date.split('-')[0],
      purchasingPower: 100,
      inflation: 0
    },
    {
      period: cpiData.current_date.split('-')[0],
      purchasingPower: 100 + cpiData.percentage_gap,
      inflation: cpiData.inflation_rate
    }
  ];

  return (
    <div className={`space-y-8 ${className}`}>
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Salary Comparison
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={salaryComparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis tickFormatter={formatCurrency} />
              <Tooltip formatter={(value) => formatCurrency(value as number)} />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Salary Trend Line Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Salary vs Inflation Trend
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="year" 
                tick={{ fontSize: 12 }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis 
                tickFormatter={formatCurrency}
                tick={{ fontSize: 12 }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="Current Salary" 
                stroke="#3B82F6" 
                strokeWidth={3}
                dot={{ r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="Inflation-Adjusted Salary" 
                stroke="#F59E0B" 
                strokeWidth={3}
                strokeDasharray="5 5"
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Track how your salary growth compares to inflation over time.
        </p>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
          <div className="text-2xl font-bold text-blue-600 mb-2">
            {cpiData.years_elapsed.toFixed(1)}
          </div>
          <div className="text-sm font-medium text-gray-900 mb-1">Years Analyzed</div>
          <div className="text-xs text-gray-600">Time period covered</div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
          <div className="text-2xl font-bold text-orange-600 mb-2">
            {cpiData.inflation_rate.toFixed(1)}%
          </div>
          <div className="text-sm font-medium text-gray-900 mb-1">Total Inflation</div>
          <div className="text-xs text-gray-600">Cumulative rate</div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
          <div className={`text-2xl font-bold mb-2 ${
            cpiData.percentage_gap >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {cpiData.percentage_gap >= 0 ? '+' : ''}{cpiData.percentage_gap.toFixed(1)}%
          </div>
          <div className="text-sm font-medium text-gray-900 mb-1">Salary Gap</div>
          <div className="text-xs text-gray-600">vs inflation</div>
        </div>
      </div>
    </div>
  );
}; 