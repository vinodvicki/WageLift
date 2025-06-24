/**
 * Domain Types for WageLift Application
 * Core business entities and value objects
 */

// User Domain
export interface User {
  id: string;
  email: string;
  name: string;
  auth0Id: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface UserProfile {
  id: string;
  userId: string;
  jobTitle?: string;
  company?: string;
  department?: string;
  yearsAtCompany?: number;
  managerName?: string;
  location?: string;
}

// Salary Domain
export interface SalaryEntry {
  id: string;
  userId: string;
  currentSalary: number;
  effectiveDate: Date;
  jobTitle: string;
  company: string;
  location: string;
  isCurrent: boolean;
  createdAt: Date;
}

export interface SalaryComparison {
  jobTitle: string;
  location: string;
  percentiles: {
    p10: number;
    p25: number;
    p50: number;
    p75: number;
    p90: number;
  };
  percentileRank: number;
  marketPosition: 'Below Market' | 'Market Rate' | 'Above Market';
  benchmarkCount: number;
}

// CPI Domain
export interface CPICalculation {
  id: string;
  userId: string;
  currentSalary: number;
  adjustedSalary: number;
  percentageGap: number;
  dollarGap: number;
  inflationRate: number;
  yearsElapsed: number;
  calculationMethod: string;
  calculationDate: Date;
  historicalDate: Date;
}

// Document Domain
export interface Document {
  id: string;
  userId: string;
  title: string;
  content: string;
  documentType: 'raise_letter' | 'memo' | 'report';
  version: number;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
  tags?: string[];
}

export interface DocumentVersion {
  id: string;
  documentId: string;
  versionNumber: number;
  title: string;
  content: string;
  createdAt: Date;
  changeSummary?: string;
}

// Raise Letter Domain
export interface RaiseLetterData {
  employeeName: string;
  employeeTitle: string;
  companyName: string;
  managerName: string;
  currentSalary: number;
  requestedSalary: number;
  percentageIncrease: number;
  dollarIncrease: number;
  justification: string;
  achievements: string[];
  marketData?: SalaryComparison;
  cpiData?: CPICalculation;
}

export interface RaiseLetterRequest {
  userData: UserProfile;
  salaryData: SalaryEntry;
  cpiData?: CPICalculation;
  benchmarkData?: SalaryComparison;
  preferences: {
    tone: 'professional' | 'confident' | 'collaborative';
    length: 'brief' | 'standard' | 'detailed';
    keyAchievements?: string[];
    recentProjects?: string[];
    customPoints?: string[];
    requestedIncrease?: number;
  };
}

export interface RaiseLetterResponse {
  id: string;
  content: string;
  metadata: {
    tone: string;
    length: string;
    wordCount: number;
    generatedAt: Date;
    version: string;
  };
  success: boolean;
  message?: string;
}

// Email Domain
export interface EmailRequest {
  recipientEmail: string;
  recipientName?: string;
  subject?: string;
  includePdf: boolean;
  ccSender: boolean;
  customMessage?: string;
}

export interface EmailResponse {
  success: boolean;
  message: string;
  messageId?: string;
  sentAt: Date;
  recipients: string[];
}

// Error Domain
export interface DomainError {
  code: string;
  message: string;
  details?: Record<string, any> | undefined;
  timestamp: Date;
}

// API Response Wrapper
export interface ApiResponse<T> {
  data?: T;
  error?: DomainError;
  success: boolean;
  message?: string;
} 