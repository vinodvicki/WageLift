/**
 * Environment Variable Validation
 * Ensures all required environment variables are present and valid
 */

export interface AppConfig {
  // API Configuration
  apiBaseUrl: string;
  
  // Auth0 Configuration
  auth0Domain: string;
  auth0ClientId: string;
  auth0Audience: string;
  
  // Feature Flags
  enableDebugMode: boolean;
  enableMetrics: boolean;
  enableErrorReporting: boolean;
  
  // External Services
  supabaseUrl?: string;
  supabaseAnonKey?: string;
  
  // Environment
  nodeEnv: 'development' | 'production' | 'test';
  appVersion: string;
}

export class ConfigValidationError extends Error {
  constructor(message: string, public missingVars: string[]) {
    super(message);
    this.name = 'ConfigValidationError';
  }
}

/**
 * Validate and parse environment variables
 */
export function validateEnvironment(): AppConfig {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Required environment variables
  const requiredVars = {
    NEXT_PUBLIC_API_BASE_URL: process.env['NEXT_PUBLIC_API_BASE_URL'],
    NEXT_PUBLIC_AUTH0_DOMAIN: process.env['NEXT_PUBLIC_AUTH0_DOMAIN'],
    NEXT_PUBLIC_AUTH0_CLIENT_ID: process.env['NEXT_PUBLIC_AUTH0_CLIENT_ID'],
    NEXT_PUBLIC_AUTH0_AUDIENCE: process.env['NEXT_PUBLIC_AUTH0_AUDIENCE'],
  };

  // Check for missing required variables
  for (const [key, value] of Object.entries(requiredVars)) {
    if (!value) {
      errors.push(`Missing required environment variable: ${key}`);
    }
  }

  // Optional environment variables with defaults
  const optionalVars = {
    NEXT_PUBLIC_SUPABASE_URL: process.env['NEXT_PUBLIC_SUPABASE_URL'],
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env['NEXT_PUBLIC_SUPABASE_ANON_KEY'],
    NODE_ENV: process.env['NODE_ENV'] || 'development',
    NEXT_PUBLIC_APP_VERSION: process.env['NEXT_PUBLIC_APP_VERSION'] || '1.0.0',
  };

  // Validate NODE_ENV
  const validEnvs = ['development', 'production', 'test'];
  if (!validEnvs.includes(optionalVars.NODE_ENV)) {
    errors.push(`Invalid NODE_ENV: ${optionalVars.NODE_ENV}. Must be one of: ${validEnvs.join(', ')}`);
  }

  // Validate URLs
  if (requiredVars.NEXT_PUBLIC_API_BASE_URL) {
    try {
      new URL(requiredVars.NEXT_PUBLIC_API_BASE_URL);
    } catch {
      errors.push('NEXT_PUBLIC_API_BASE_URL must be a valid URL');
    }
  }

  if (requiredVars.NEXT_PUBLIC_AUTH0_DOMAIN) {
    if (!requiredVars.NEXT_PUBLIC_AUTH0_DOMAIN.includes('.auth0.com') && 
        !requiredVars.NEXT_PUBLIC_AUTH0_DOMAIN.includes('.us.auth0.com') &&
        !requiredVars.NEXT_PUBLIC_AUTH0_DOMAIN.includes('.eu.auth0.com')) {
      warnings.push('AUTH0_DOMAIN should typically end with .auth0.com');
    }
  }

  // Check for Supabase configuration completeness
  const hasSupabaseUrl = !!optionalVars.NEXT_PUBLIC_SUPABASE_URL;
  const hasSupabaseKey = !!optionalVars.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  
  if (hasSupabaseUrl !== hasSupabaseKey) {
    warnings.push('Supabase configuration incomplete - both URL and ANON_KEY should be provided');
  }

  // Throw error if required variables are missing
  if (errors.length > 0) {
    throw new ConfigValidationError(
      `Environment validation failed:\n${errors.join('\n')}`,
      Object.keys(requiredVars).filter(key => !requiredVars[key as keyof typeof requiredVars])
    );
  }

  // Log warnings in development
  if (warnings.length > 0 && optionalVars.NODE_ENV === 'development') {
    console.warn('Environment validation warnings:');
    warnings.forEach(warning => console.warn(`- ${warning}`));
  }

  // Return validated configuration
  const config: AppConfig = {
    apiBaseUrl: requiredVars.NEXT_PUBLIC_API_BASE_URL!,
    auth0Domain: requiredVars.NEXT_PUBLIC_AUTH0_DOMAIN!,
    auth0ClientId: requiredVars.NEXT_PUBLIC_AUTH0_CLIENT_ID!,
    auth0Audience: requiredVars.NEXT_PUBLIC_AUTH0_AUDIENCE!,
    nodeEnv: optionalVars.NODE_ENV as 'development' | 'production' | 'test',
    appVersion: optionalVars.NEXT_PUBLIC_APP_VERSION,
    enableDebugMode: optionalVars.NODE_ENV === 'development',
    enableMetrics: optionalVars.NODE_ENV === 'production',
    enableErrorReporting: optionalVars.NODE_ENV === 'production',
  };

  if (optionalVars.NEXT_PUBLIC_SUPABASE_URL) {
    config.supabaseUrl = optionalVars.NEXT_PUBLIC_SUPABASE_URL;
  }

  if (optionalVars.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    config.supabaseAnonKey = optionalVars.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  }

  return config;
}

/**
 * Get validated configuration (cached)
 */
let cachedConfig: AppConfig | null = null;

export function getConfig(): AppConfig {
  if (!cachedConfig) {
    cachedConfig = validateEnvironment();
  }
  return cachedConfig;
}

/**
 * Reset configuration cache (useful for testing)
 */
export function resetConfigCache(): void {
  cachedConfig = null;
}

/**
 * Check if running in development mode
 */
export function isDevelopment(): boolean {
  return getConfig().nodeEnv === 'development';
}

/**
 * Check if running in production mode
 */
export function isProduction(): boolean {
  return getConfig().nodeEnv === 'production';
}

/**
 * Get API base URL with fallback
 */
export function getApiBaseUrl(): string {
  const config = getConfig();
  return config.apiBaseUrl || 'http://localhost:8000';
} 