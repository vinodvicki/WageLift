/**
 * Salary Dashboard Page for WageLift
 */

'use client';

import React from 'react';

export default function SalaryDashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            WageLift Salary Calculator
          </h1>
          <p className="text-gray-600 mb-6">
            Calculate your purchasing power loss due to inflation and create evidence-based raise requests.
          </p>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h2 className="text-lg font-semibold text-blue-900 mb-2">
              🚧 Dashboard Under Construction
            </h2>
            <p className="text-blue-800">
              The full salary calculation dashboard is being restored. Please check back shortly.
            </p>
          </div>
          
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
              <h3 className="text-lg font-semibold mb-2">Salary Analysis</h3>
              <p className="text-blue-100">Compare your compensation with market rates</p>
            </div>
            
            <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
              <h3 className="text-lg font-semibold mb-2">CPI Calculator</h3>
              <p className="text-green-100">Calculate inflation impact on your purchasing power</p>
            </div>
            
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
              <h3 className="text-lg font-semibold mb-2">Raise Letter</h3>
              <p className="text-purple-100">Generate professional raise request letters</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 