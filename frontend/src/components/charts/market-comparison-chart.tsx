/**
 * Market Comparison Chart Component
 * 
 * Combines CPI analysis with salary benchmark data to provide comprehensive
 * market insights and salary positioning visualization.
 */

'use client';

import React from 'react';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine
} from 'recharts';
import { formatSalary, type SalaryComparisonResponse } from '@/lib/api/benchmark';

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

interface MarketComparisonChartProps {
  cpiData: CPICalculationData;
  benchmarkData: SalaryComparisonResponse;
  className?: string;
}

interface ChartDataPoint {
  category: string;
  salary: number;
  type: 'benchmark' | 'cpi' | 'user';
  description: string;
}

export const MarketComparisonChart: React.FC<MarketComparisonChartProps> = ({
  cpiData,
  benchmarkData,
  className = ''
}) => {
  // Prepare combined chart data
  const chartData: ChartDataPoint[] = React.useMemo(() => {
    const data: ChartDataPoint[] = [];

    // Add benchmark percentiles
    if (benchmarkData.percentiles.p25) {
      data.push({
        category: '25th Percentile',
        salary: benchmarkData.percentiles.p25,
        type: 'benchmark',
        description: 'Bottom quarter of market'
      });
    }

    if (benchmarkData.percentiles.p50) {
      data.push({
        category: 'Market Median',
        salary: benchmarkData.percentiles.p50,
        type: 'benchmark',
        description: 'Market median salary'
      });
    }

    if (benchmarkData.percentiles.p75) {
      data.push({
        category: '75th Percentile',
        salary: benchmarkData.percentiles.p75,
        type: 'benchmark',
        description: 'Top quarter of market'
      });
    }

    // Add CPI-adjusted salary
    data.push({
      category: 'Inflation-Adjusted',
      salary: cpiData.adjusted_salary,
      type: 'cpi',
      description: 'What you should earn based on inflation'
    });

    // Add user's current salary
    data.push({
      category: 'Your Current',
      salary: cpiData.current_salary,
      type: 'user',
      description: 'Your current salary'
    });

    return data.sort((a, b) => a.salary - b.salary);
  }, [cpiData, benchmarkData]);

  // Custom tooltip for detailed information
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as ChartDataPoint;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg max-w-sm">
          <p className="font-semibold text-gray-900">{data.category}</p>
          <p className="text-lg font-bold text-blue-600 mb-2">
            {formatSalary(data.salary)}
          </p>
          <p className="text-sm text-gray-600">{data.description}</p>
          {data.type === 'user' && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                Gap to inflation-adjusted: {formatSalary(Math.abs(cpiData.dollar_gap))}
                {cpiData.dollar_gap < 0 ? ' behind' : ' ahead'}
              </p>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  // Get bar color based on type
  const getBarColor = (type: string) => {
    switch (type) {
      case 'benchmark': return '#6366f1'; // Indigo for market benchmarks
      case 'cpi': return '#f59e0b'; // Orange for CPI-adjusted
      case 'user': return '#10b981'; // Green for user's salary
      default: return '#6b7280';
    }
  };

  // Calculate insights
  const insights = React.useMemo(() => {
    const insights: string[] = [];
    
    const medianSalary = benchmarkData.percentiles.p50;
    const userSalary = cpiData.current_salary;
    const adjustedSalary = cpiData.adjusted_salary;

    if (medianSalary) {
      const marketGap = userSalary - medianSalary;
      if (marketGap > 0) {
        insights.push(`You earn ${formatSalary(marketGap)} above market median`);
      } else {
        insights.push(`You earn ${formatSalary(Math.abs(marketGap))} below market median`);
      }
    }

    if (cpiData.dollar_gap < 0) {
      insights.push(`Inflation has reduced your purchasing power by ${formatSalary(Math.abs(cpiData.dollar_gap))}`);
    } else {
      insights.push(`Your salary has outpaced inflation by ${formatSalary(cpiData.dollar_gap)}`);
    }

    if (benchmarkData.percentile_rank) {
      insights.push(`You rank in the ${benchmarkData.percentile_rank.toFixed(0)}th percentile of your profession`);
    }

    return insights;
  }, [cpiData, benchmarkData]);

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Market Position Analysis
        </h3>
        <p className="text-sm text-gray-600">
          Your salary compared to market benchmarks and inflation adjustments
        </p>
      </div>

      <div className="h-80 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
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
              dataKey="category"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis 
              tickFormatter={(value) => formatSalary(value)}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar 
              dataKey="salary" 
              radius={[4, 4, 0, 0]}
              fill={(entry: any) => getBarColor(entry.type)}
            />
            {/* Reference line for median */}
            {benchmarkData.percentiles.p50 && (
              <ReferenceLine 
                y={benchmarkData.percentiles.p50} 
                stroke="#6366f1" 
                strokeDasharray="2 2"
                label={{ value: "Market Median", position: "topRight" }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center justify-center gap-4 mb-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-indigo-500 rounded"></div>
          <span className="text-gray-600">Market Benchmarks</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-amber-500 rounded"></div>
          <span className="text-gray-600">Inflation-Adjusted</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-emerald-500 rounded"></div>
          <span className="text-gray-600">Your Salary</span>
        </div>
      </div>

      {/* Key Insights */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Key Insights</h4>
        <div className="space-y-2">
          {insights.map((insight, index) => (
            <div key={index} className="flex items-start gap-2">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <p className="text-sm text-gray-700">{insight}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {benchmarkData.recommendations && benchmarkData.recommendations.length > 0 && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Recommendations</h4>
          <div className="space-y-1">
            {benchmarkData.recommendations.map((recommendation, index) => (
              <p key={index} className="text-sm text-blue-800">
                • {recommendation}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketComparisonChart; 