'use client';

import React from 'react';

interface CPICalculationData {
  percentage_gap: number;
  dollar_gap: number;
  inflation_rate: number;
}

interface CPIResultsGaugeProps {
  cpiData: CPICalculationData;
  className?: string;
}

export const CPIResultsGauge: React.FC<CPIResultsGaugeProps> = ({
  cpiData,
  className = ''
}) => {
  const gaugeValue = Math.max(-100, Math.min(100, cpiData.percentage_gap));
  const needleRotation = (gaugeValue / 100) * 90;
  
  const getGaugeColor = () => {
    if (cpiData.percentage_gap >= 10) return '#10B981';
    if (cpiData.percentage_gap >= 0) return '#F59E0B';
    return '#EF4444';
  };

  const getStatusText = () => {
    if (cpiData.percentage_gap >= 10) return 'Excellent';
    if (cpiData.percentage_gap >= 0) return 'Good';
    return 'Behind';
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-8 ${className}`}>
      <div className="text-center mb-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Purchasing Power Status
        </h3>
      </div>

      <div className="flex flex-col items-center">
        <div className="relative">
          <svg width="300" height="180" viewBox="0 0 300 180">
            <path
              d="M 50 150 A 100 100 0 0 1 250 150"
              fill="none"
              stroke="#E5E7EB"
              strokeWidth="20"
            />
            <circle cx="150" cy="150" r="10" fill="#374151" />
            <line
              x1="150" y1="150" x2="150" y2="60"
              stroke="#374151" strokeWidth="4"
              transform={`rotate(${needleRotation} 150 150)`}
            />
          </svg>
        </div>

        <div className="text-center mt-6">
          <div 
            className="text-3xl font-bold mb-2"
            style={{ color: getGaugeColor() }}
          >
            {cpiData.percentage_gap >= 0 ? '+' : ''}{cpiData.percentage_gap.toFixed(1)}%
          </div>
          <div className="text-lg font-semibold text-gray-900">
            {getStatusText()}
          </div>
        </div>
      </div>
    </div>
  );
};

import React from 'react';

interface CPICalculationData {
  percentage_gap: number;
  dollar_gap: number;
  inflation_rate: number;
}

interface CPIResultsGaugeProps {
  cpiData: CPICalculationData;
  className?: string;
}

export const CPIResultsGauge: React.FC<CPIResultsGaugeProps> = ({
  cpiData,
  className = ''
}) => {
  const gaugeValue = Math.max(-100, Math.min(100, cpiData.percentage_gap));
  const needleRotation = (gaugeValue / 100) * 90;
  
  const getGaugeColor = () => {
    if (cpiData.percentage_gap >= 10) return '#10B981';
    if (cpiData.percentage_gap >= 0) return '#F59E0B';
    return '#EF4444';
  };

  const getStatusText = () => {
    if (cpiData.percentage_gap >= 10) return 'Excellent';
    if (cpiData.percentage_gap >= 0) return 'Good';
    return 'Behind';
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-8 ${className}`}>
      <div className="text-center mb-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Purchasing Power Status
        </h3>
      </div>

      <div className="flex flex-col items-center">
        <div className="relative">
          <svg width="300" height="180" viewBox="0 0 300 180">
            <path
              d="M 50 150 A 100 100 0 0 1 250 150"
              fill="none"
              stroke="#E5E7EB"
              strokeWidth="20"
            />
            <circle cx="150" cy="150" r="10" fill="#374151" />
            <line
              x1="150" y1="150" x2="150" y2="60"
              stroke="#374151" strokeWidth="4"
              transform={`rotate(${needleRotation} 150 150)`}
            />
          </svg>
        </div>

        <div className="text-center mt-6">
          <div 
            className="text-3xl font-bold mb-2"
            style={{ color: getGaugeColor() }}
          >
            {cpiData.percentage_gap >= 0 ? '+' : ''}{cpiData.percentage_gap.toFixed(1)}%
          </div>
          <div className="text-lg font-semibold text-gray-900">
            {getStatusText()}
          </div>
        </div>
      </div>
    </div>
  );
};
