/**
 * Frontend Performance Metrics for WageLift
 * 
 * Provides comprehensive client-side monitoring including:
 * - Page load performance
 * - API call latency
 * - User interactions
 * - Error tracking
 * - Memory usage
 */

import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

// Types for metrics
interface MetricEntry {
  name: string;
  value: number;
  delta: number;
  id: string;
  rating: 'good' | 'needs-improvement' | 'poor';
  timestamp: number;
  url: string;
  userAgent: string;
}

interface PerformanceMetrics {
  pageLoadTime: number;
  domContentLoaded: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  firstInputDelay: number;
  timeToFirstByte: number;
}

interface UserInteraction {
  type: string;
  target: string;
  timestamp: number;
  page: string;
  userId?: string;
}

interface ApiMetrics {
  endpoint: string;
  method: string;
  duration: number;
  status: number;
  timestamp: number;
  userId?: string;
  correlationId?: string;
}

interface ErrorMetrics {
  message: string;
  stack?: string;
  url: string;
  lineNumber?: number;
  columnNumber?: number;
  timestamp: number;
  userId?: string;
  userAgent: string;
}

// Global metrics collector
class MetricsCollector {
  private metrics: MetricEntry[] = [];
  private interactions: UserInteraction[] = [];
  private apiCalls: ApiMetrics[] = [];
  private errors: ErrorMetrics[] = [];
  private userId?: string;
  
  constructor() {
    this.setupWebVitals();
    this.setupErrorTracking();
    this.setupApiInterception();
    this.setupUserInteractionTracking();
  }
  
  setUserId(userId: string) {
    this.userId = userId;
  }
  
  private setupWebVitals() {
    // Collect Core Web Vitals
    getCLS(this.handleMetric.bind(this));
    getFID(this.handleMetric.bind(this));
    getFCP(this.handleMetric.bind(this));
    getLCP(this.handleMetric.bind(this));
    getTTFB(this.handleMetric.bind(this));
  }
  
  private handleMetric(metric: any) {
    const entry: MetricEntry = {
      name: metric.name,
      value: metric.value,
      delta: metric.delta,
      id: metric.id,
      rating: metric.rating,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent
    };
    
    this.metrics.push(entry);
    this.sendMetric(entry);
  }
  
  private setupErrorTracking() {
    // Global error handler
    window.addEventListener('error', (event) => {
      const errorMetric: ErrorMetrics = {
        message: event.message,
        stack: event.error?.stack,
        url: event.filename || window.location.href,
        lineNumber: event.lineno,
        columnNumber: event.colno,
        timestamp: Date.now(),
        userId: this.userId,
        userAgent: navigator.userAgent
      };
      
      this.errors.push(errorMetric);
      this.sendError(errorMetric);
    });
    
    // Unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      const errorMetric: ErrorMetrics = {
        message: `Unhandled Promise Rejection: ${event.reason}`,
        stack: event.reason?.stack,
        url: window.location.href,
        timestamp: Date.now(),
        userId: this.userId,
        userAgent: navigator.userAgent
      };
      
      this.errors.push(errorMetric);
      this.sendError(errorMetric);
    });
  }
  
  private setupApiInterception() {
    // Intercept fetch calls
    const originalFetch = window.fetch;
    
    window.fetch = async (...args) => {
      const startTime = performance.now();
      const url = args[0] as string;
      const options = args[1] || {};
      const method = options.method || 'GET';
      
      try {
        const response = await originalFetch(...args);
        const duration = performance.now() - startTime;
        
        const apiMetric: ApiMetrics = {
          endpoint: url,
          method: method.toUpperCase(),
          duration,
          status: response.status,
          timestamp: Date.now(),
          userId: this.userId,
          correlationId: this.generateCorrelationId()
        };
        
        this.apiCalls.push(apiMetric);
        this.sendApiMetric(apiMetric);
        
        return response;
      } catch (error) {
        const duration = performance.now() - startTime;
        
        const apiMetric: ApiMetrics = {
          endpoint: url,
          method: method.toUpperCase(),
          duration,
          status: 0, // Network error
          timestamp: Date.now(),
          userId: this.userId,
          correlationId: this.generateCorrelationId()
        };
        
        this.apiCalls.push(apiMetric);
        this.sendApiMetric(apiMetric);
        
        throw error;
      }
    };
  }
  
  private setupUserInteractionTracking() {
    // Track clicks
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      const interaction: UserInteraction = {
        type: 'click',
        target: this.getElementSelector(target),
        timestamp: Date.now(),
        page: window.location.pathname,
        userId: this.userId
      };
      
      this.interactions.push(interaction);
      this.sendInteraction(interaction);
    });
    
    // Track form submissions
    document.addEventListener('submit', (event) => {
      const target = event.target as HTMLFormElement;
      const interaction: UserInteraction = {
        type: 'form_submit',
        target: this.getElementSelector(target),
        timestamp: Date.now(),
        page: window.location.pathname,
        userId: this.userId
      };
      
      this.interactions.push(interaction);
      this.sendInteraction(interaction);
    });
  }
  
  private getElementSelector(element: HTMLElement): string {
    // Generate a selector for the element
    if (element.id) return `#${element.id}`;
    if (element.className) return `.${element.className.split(' ')[0]}`;
    return element.tagName.toLowerCase();
  }
  
  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  // Page navigation tracking
  trackPageView(page: string, loadTime?: number) {
    const pageMetric = {
      type: 'page_view',
      page,
      loadTime: loadTime || performance.now(),
      timestamp: Date.now(),
      userId: this.userId
    };
    
    this.sendPageView(pageMetric);
  }
  
  // Manual performance tracking
  trackPerformance(name: string, duration: number, metadata?: any) {
    const performanceMetric = {
      name,
      duration,
      metadata,
      timestamp: Date.now(),
      userId: this.userId,
      page: window.location.pathname
    };
    
    this.sendPerformanceMetric(performanceMetric);
  }
  
  // Auth-specific tracking
  trackAuthEvent(event: string, success: boolean, duration?: number) {
    const authMetric = {
      type: 'auth_event',
      event,
      success,
      duration,
      timestamp: Date.now(),
      userId: this.userId,
      page: window.location.pathname
    };
    
    this.sendAuthMetric(authMetric);
  }
  
  // Business event tracking
  trackBusinessEvent(event: string, metadata?: any) {
    const businessMetric = {
      type: 'business_event',
      event,
      metadata,
      timestamp: Date.now(),
      userId: this.userId,
      page: window.location.pathname
    };
    
    this.sendBusinessMetric(businessMetric);
  }
  
  // Send metrics to backend
  private async sendMetric(metric: MetricEntry) {
    try {
      await fetch('/api/metrics/web-vitals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metric)
      });
    } catch (error) {
      console.warn('Failed to send web vital metric:', error);
    }
  }
  
  private async sendError(error: ErrorMetrics) {
    try {
      await fetch('/api/metrics/errors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(error)
      });
    } catch (err) {
      console.warn('Failed to send error metric:', err);
    }
  }
  
  private async sendApiMetric(metric: ApiMetrics) {
    try {
      await fetch('/api/metrics/api-calls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metric)
      });
    } catch (error) {
      console.warn('Failed to send API metric:', error);
    }
  }
  
  private async sendInteraction(interaction: UserInteraction) {
    try {
      await fetch('/api/metrics/interactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(interaction)
      });
    } catch (error) {
      console.warn('Failed to send interaction metric:', error);
    }
  }
  
  private async sendPageView(pageView: any) {
    try {
      await fetch('/api/metrics/page-views', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pageView)
      });
    } catch (error) {
      console.warn('Failed to send page view metric:', error);
    }
  }
  
  private async sendPerformanceMetric(metric: any) {
    try {
      await fetch('/api/metrics/performance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metric)
      });
    } catch (error) {
      console.warn('Failed to send performance metric:', error);
    }
  }
  
  private async sendAuthMetric(metric: any) {
    try {
      await fetch('/api/metrics/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metric)
      });
    } catch (error) {
      console.warn('Failed to send auth metric:', error);
    }
  }
  
  private async sendBusinessMetric(metric: any) {
    try {
      await fetch('/api/metrics/business', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metric)
      });
    } catch (error) {
      console.warn('Failed to send business metric:', error);
    }
  }
  
  // Get current metrics summary
  getMetricsSummary() {
    return {
      webVitals: this.metrics,
      apiCalls: this.apiCalls,
      userInteractions: this.interactions,
      errors: this.errors,
      memoryUsage: this.getMemoryUsage(),
      connectionType: this.getConnectionInfo()
    };
  }
  
  private getMemoryUsage() {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      return {
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit
      };
    }
    return null;
  }
  
  private getConnectionInfo() {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      return {
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt
      };
    }
    return null;
  }
}

// React hooks for metrics
export function useMetrics() {
  return {
    trackPageView: (page: string, loadTime?: number) => 
      metricsCollector.trackPageView(page, loadTime),
    
    trackPerformance: (name: string, duration: number, metadata?: any) => 
      metricsCollector.trackPerformance(name, duration, metadata),
    
    trackAuthEvent: (event: string, success: boolean, duration?: number) => 
      metricsCollector.trackAuthEvent(event, success, duration),
    
    trackBusinessEvent: (event: string, metadata?: any) => 
      metricsCollector.trackBusinessEvent(event, metadata),
    
    setUserId: (userId: string) => 
      metricsCollector.setUserId(userId),
    
    getMetricsSummary: () => 
      metricsCollector.getMetricsSummary()
  };
}

// Performance monitoring HOC
export function withPerformanceMonitoring<T extends object>(
  WrappedComponent: React.ComponentType<T>,
  componentName: string
) {
  return function MonitoredComponent(props: T) {
    const startTime = performance.now();
    
    React.useEffect(() => {
      const mountTime = performance.now() - startTime;
      metricsCollector.trackPerformance(`${componentName}_mount`, mountTime);
      
      return () => {
        const totalTime = performance.now() - startTime;
        metricsCollector.trackPerformance(`${componentName}_unmount`, totalTime);
      };
    }, []);
    
    return React.createElement(WrappedComponent, props);
  };
}

// Global metrics collector instance
export const metricsCollector = new MetricsCollector();

// Initialize metrics on page load
if (typeof window !== 'undefined') {
  // Track initial page load
  window.addEventListener('load', () => {
    const loadTime = performance.now();
    metricsCollector.trackPageView(window.location.pathname, loadTime);
  });
  
  // Track navigation changes (for SPA)
  let currentPath = window.location.pathname;
  const observer = new MutationObserver(() => {
    if (window.location.pathname !== currentPath) {
      currentPath = window.location.pathname;
      metricsCollector.trackPageView(currentPath);
    }
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

export default metricsCollector; 