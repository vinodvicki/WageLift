/**
 * Salary Percentile Chart Component
 * 
 * Displays interactive percentile visualization showing user's salary position
 * relative to market benchmarks from CareerOneStop API data.
 */

'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell
} from 'recharts';
import { formatSalary, type PercentileData, type SalaryComparisonResponse } from '@/lib/api/benchmark';

interface SalaryPercentileChartProps {
  comparisonData: SalaryComparisonResponse;
  className?: string;
}

interface ChartDataPoint {
  percentile: string;
  salary: number;
  isUserPosition: boolean;
  label: string;
}

export const SalaryPercentileChart: React.FC<SalaryPercentileChartProps> = ({
  comparisonData,
  className = ''
}) => {
  // Prepare chart data from percentiles
  const chartData: ChartDataPoint[] = React.useMemo(() => {
    const { percentiles, current_salary, percentile_rank } = comparisonData;
    
    const data: ChartDataPoint[] = [
      {
        percentile: '10th',
        salary: percentiles.p10 || 0,
        isUserPosition: false,
        label: '10th Percentile'
      },
      {
        percentile: '25th',
        salary: percentiles.p25 || 0,
        isUserPosition: false,
        label: '25th Percentile'
      },
      {
        percentile: '50th',
        salary: percentiles.p50 || 0,
        isUserPosition: false,
        label: 'Median (50th)'
      },
      {
        percentile: '75th',
        salary: percentiles.p75 || 0,
        isUserPosition: false,
        label: '75th Percentile'
      },
      {
        percentile: '90th',
        salary: percentiles.p90 || 0,
        isUserPosition: false,
        label: '90th Percentile'
      }
    ];

    // Add user's current salary as a reference point
    if (percentile_rank && percentile_rank > 0) {
      data.push({
        percentile: 'You',
        salary: current_salary,
        isUserPosition: true,
        label: `Your Salary (${percentile_rank.toFixed(0)}th percentile)`
      });
    }

    return data.sort((a, b) => a.salary - b.salary);
  }, [comparisonData]);

  // Custom tooltip for detailed information
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as ChartDataPoint;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.label}</p>
          <p className="text-lg font-bold text-blue-600">
            {formatSalary(data.salary)}
          </p>
          {data.isUserPosition && (
            <p className="text-sm text-gray-600 mt-1">
              Your current position in the market
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  // Get bar color based on whether it's user position
  const getBarColor = (isUserPosition: boolean) => {
    return isUserPosition ? '#f59e0b' : '#3b82f6'; // Orange for user, blue for market
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Salary Percentile Distribution
        </h3>
        <p className="text-sm text-gray-600">
          Your salary compared to market benchmarks for{' '}
          <span className="font-medium">{comparisonData.job_title}</span> in{' '}
          <span className="font-medium">{comparisonData.location}</span>
        </p>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 60
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis 
              dataKey="percentile"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis 
              tickFormatter={(value) => formatSalary(value)}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="salary" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={getBarColor(entry.isUserPosition)}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded"></div>
          <span className="text-gray-600">Market Percentiles</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-amber-500 rounded"></div>
          <span className="text-gray-600">Your Position</span>
        </div>
      </div>

      {/* Market Position Summary */}
      {comparisonData.market_position && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">
              Market Position:
            </span>
            <span className={`text-sm font-semibold px-2 py-1 rounded ${
              comparisonData.market_position === 'Above Average' 
                ? 'bg-green-100 text-green-800'
                : comparisonData.market_position === 'Average'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {comparisonData.market_position}
            </span>
          </div>
          {comparisonData.percentile_rank && (
            <p className="text-xs text-gray-600 mt-1">
              You earn more than {comparisonData.percentile_rank.toFixed(0)}% of professionals in this role
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default SalaryPercentileChart; 