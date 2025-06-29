'use client';

import React from 'react';

interface CPICalculationData {
  percentage_gap: number;
  dollar_gap: number;
  inflation_rate: number;
  adjusted_salary: number;
  current_salary: number;
  original_salary: number;
}

interface CPIResultsSummaryProps {
  cpiData: CPICalculationData;
  className?: string;
}

export const CPIResultsSummary: React.FC<CPIResultsSummaryProps> = ({
  cpiData,
  className = ''
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const cards = [
    {
      title: 'Current Salary',
      value: formatCurrency(cpiData.current_salary),
      description: 'Your current annual salary',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200'
    },
    {
      title: 'Inflation-Adjusted',
      value: formatCurrency(cpiData.adjusted_salary),
      description: 'What you should earn today',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200'
    },
    {
      title: 'Gap Amount',
      value: formatCurrency(Math.abs(cpiData.dollar_gap)),
      description: cpiData.dollar_gap >= 0 ? 'Above inflation' : 'Behind inflation',
      color: cpiData.dollar_gap >= 0 ? 'text-green-600' : 'text-red-600',
      bgColor: cpiData.dollar_gap >= 0 ? 'bg-green-50' : 'bg-red-50',
      borderColor: cpiData.dollar_gap >= 0 ? 'border-green-200' : 'border-red-200'
    },
    {
      title: 'Percentage Gap',
      value: `${cpiData.percentage_gap >= 0 ? '+' : ''}${cpiData.percentage_gap.toFixed(1)}%`,
      description: 'Purchasing power change',
      color: cpiData.percentage_gap >= 0 ? 'text-green-600' : 'text-red-600',
      bgColor: cpiData.percentage_gap >= 0 ? 'bg-green-50' : 'bg-red-50',
      borderColor: cpiData.percentage_gap >= 0 ? 'border-green-200' : 'border-red-200'
    }
  ];

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}>
      {cards.map((card, index) => (
        <div
          key={index}
          className={`rounded-lg border p-6 ${card.bgColor} ${card.borderColor}`}
        >
          <div className="text-center">
            <div className={`text-2xl font-bold mb-2 ${card.color}`}>
              {card.value}
            </div>
            <div className="text-sm font-medium text-gray-900 mb-1">
              {card.title}
            </div>
            <div className="text-xs text-gray-600">
              {card.description}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
