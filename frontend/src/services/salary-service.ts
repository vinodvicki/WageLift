/**
 * Salary Service
 * Business logic for salary calculations, comparisons, and CPI adjustments
 */

import type { SalaryEntry, SalaryComparison, CPICalculation, ApiResponse } from '../domain/types';

export class SalaryService {
  /**
   * Calculate salary increase percentage
   */
  calculateIncreasePercentage(currentSalary: number, requestedSalary: number): number {
    if (currentSalary <= 0) throw new Error('Current salary must be positive');
    return ((requestedSalary - currentSalary) / currentSalary) * 100;
  }

  /**
   * Calculate salary increase dollar amount
   */
  calculateIncreaseDollar(currentSalary: number, requestedSalary: number): number {
    return requestedSalary - currentSalary;
  }

  /**
   * Determine market position based on percentile
   */
  determineMarketPosition(percentileRank: number): 'Below Market' | 'Market Rate' | 'Above Market' {
    if (percentileRank < 25) return 'Below Market';
    if (percentileRank <= 75) return 'Market Rate';
    return 'Above Market';
  }

  /**
   * Calculate recommended salary based on CPI adjustment
   */
  calculateCPIAdjustedSalary(
    originalSalary: number,
    inflationRate: number,
    yearsElapsed: number
  ): number {
    return originalSalary * Math.pow(1 + inflationRate / 100, yearsElapsed);
  }

  /**
   * Generate salary justification based on data
   */
  generateSalaryJustification(
    cpiData?: CPICalculation,
    marketData?: SalaryComparison,
    achievements?: string[]
  ): string {
    const justifications: string[] = [];

    if (cpiData && cpiData.percentageGap > 0) {
      justifications.push(
        `Cost of living has increased by ${cpiData.inflationRate.toFixed(1)}% over ${cpiData.yearsElapsed} years, creating a ${cpiData.percentageGap.toFixed(1)}% gap in purchasing power.`
      );
    }

    if (marketData && marketData.percentileRank < 50) {
      justifications.push(
        `Current compensation is below market median (${marketData.percentileRank}th percentile) for ${marketData.jobTitle} in ${marketData.location}.`
      );
    }

    if (achievements && achievements.length > 0) {
      justifications.push(
        `Recent achievements include: ${achievements.slice(0, 3).join(', ')}.`
      );
    }

    return justifications.join(' ');
  }

  /**
   * Validate salary entry data
   */
  validateSalaryEntry(entry: Partial<SalaryEntry>): string[] {
    const errors: string[] = [];

    if (!entry.currentSalary || entry.currentSalary <= 0) {
      errors.push('Current salary must be a positive number');
    }

    if (!entry.jobTitle || entry.jobTitle.trim().length === 0) {
      errors.push('Job title is required');
    }

    if (!entry.company || entry.company.trim().length === 0) {
      errors.push('Company name is required');
    }

    if (!entry.location || entry.location.trim().length === 0) {
      errors.push('Location is required');
    }

    return errors;
  }

  /**
   * Format salary for display
   */
  formatSalary(amount: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  /**
   * Format percentage for display
   */
  formatPercentage(value: number, decimals: number = 1): string {
    return `${value.toFixed(decimals)}%`;
  }
} 