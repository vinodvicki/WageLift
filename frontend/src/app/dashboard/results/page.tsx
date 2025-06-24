/**
 * Results Page - CPI Gap Analysis Dashboard
 * Displays comprehensive salary and inflation analysis with interactive charts
 */

'use client';

import React from 'react'
import Link from 'next/link'

export default function ResultsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container-lg section-padding">
        <div className="text-center mb-8">
          <h1 className="heading-lg mb-4">Salary Analysis Results</h1>
          <p className="text-lead text-gray-600">
            Your comprehensive salary and inflation analysis
          </p>
        </div>

        {/* Sample Results Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card-elevated p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">$85,000</div>
            <div className="text-sm font-medium text-gray-900 mb-1">Current Salary</div>
            <div className="text-xs text-gray-600">Your current annual salary</div>
          </div>

          <div className="card-elevated p-6 text-center">
            <div className="text-3xl font-bold text-orange-600 mb-2">$92,500</div>
            <div className="text-sm font-medium text-gray-900 mb-1">Inflation-Adjusted</div>
            <div className="text-xs text-gray-600">What you should earn today</div>
          </div>

          <div className="card-elevated p-6 text-center">
            <div className="text-3xl font-bold text-red-600 mb-2">-$7,500</div>
            <div className="text-sm font-medium text-gray-900 mb-1">Gap Amount</div>
            <div className="text-xs text-gray-600">Behind inflation</div>
          </div>

          <div className="card-elevated p-6 text-center">
            <div className="text-3xl font-bold text-red-600 mb-2">-8.8%</div>
            <div className="text-sm font-medium text-gray-900 mb-1">Percentage Gap</div>
            <div className="text-xs text-gray-600">Purchasing power decline</div>
          </div>
        </div>

        {/* Analysis Summary */}
        <div className="card-elevated p-8 mb-8">
          <h2 className="heading-md mb-4">Analysis Summary</h2>
          <div className="prose prose-gray max-w-none">
            <p className="text-lg text-gray-700 mb-4">
              Based on inflation data since your last raise, your purchasing power has declined by approximately 8.8%. 
              To maintain the same standard of living, your salary should be $92,500.
            </p>
            <p className="text-gray-600">
              This analysis takes into account Consumer Price Index (CPI) data from the Bureau of Labor Statistics 
              and regional cost-of-living adjustments for your area.
            </p>
          </div>
        </div>

        {/* Market Comparison */}
        <div className="card-elevated p-8 mb-8">
          <h2 className="heading-md mb-4">Market Comparison</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 mb-2">25th Percentile</div>
              <div className="text-xl text-gray-600">$78,000</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-2">50th Percentile</div>
              <div className="text-xl text-gray-600">$89,000</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 mb-2">75th Percentile</div>
              <div className="text-xl text-gray-600">$105,000</div>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="card-elevated p-8 mb-8">
          <h2 className="heading-md mb-4">Recommendations</h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <span className="text-blue-600 text-sm font-bold">1</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Request an Inflation Adjustment</h3>
                <p className="text-gray-600">Ask for a $7,500 increase to match inflation since your last raise.</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <span className="text-blue-600 text-sm font-bold">2</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Aim for Market Rate</h3>
                <p className="text-gray-600">Consider requesting $89,000 to align with the 50th percentile for your role.</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <span className="text-blue-600 text-sm font-bold">3</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Generate a Professional Letter</h3>
                <p className="text-gray-600">Use our AI-powered tool to create a compelling raise request letter.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="text-center space-y-4">
          <Link href="/dashboard/raise-letter" className="btn-primary mr-4">
            Generate Raise Letter
          </Link>
          <Link href="/dashboard/salary" className="btn-secondary">
            Recalculate Analysis
          </Link>
        </div>
      </div>
    </div>
  )
} 