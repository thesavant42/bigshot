/**
 * Frontend debugging utilities for console logging and environment detection
 */

// Console debugging utilities with consistent formatting
export class FrontendDebugger {
  private static readonly PREFIX = '[BigShot Debug]';
  private static readonly STYLES = {
    header: 'background: #2196F3; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
    success: 'background: #4CAF50; color: white; padding: 2px 6px; border-radius: 3px;',
    warning: 'background: #FF9800; color: white; padding: 2px 6px; border-radius: 3px;',
    error: 'background: #F44336; color: white; padding: 2px 6px; border-radius: 3px;',
    info: 'background: #00BCD4; color: white; padding: 2px 6px; border-radius: 3px;',
    debug: 'color: #666; font-style: italic;'
  };

  static header(message: string): void {
    console.log(`%c${this.PREFIX} ${message}`, this.STYLES.header);
  }

  static success(message: string, data?: unknown): void {
    console.log(`%c${this.PREFIX} ✓ ${message}`, this.STYLES.success);
    if (data !== undefined) {
      console.log(data);
    }
  }

  static warning(message: string, data?: unknown): void {
    console.warn(`%c${this.PREFIX} ⚠ ${message}`, this.STYLES.warning);
    if (data !== undefined) {
      console.warn(data);
    }
  }

  static error(message: string, error?: unknown): void {
    console.error(`%c${this.PREFIX} ✗ ${message}`, this.STYLES.error);
    if (error !== undefined) {
      console.error(error);
    }
  }

  static info(message: string, data?: unknown): void {
    console.log(`%c${this.PREFIX} ${message}`, this.STYLES.info);
    if (data !== undefined) {
      console.log(data);
    }
  }

  static debug(message: string, data?: unknown): void {
    if (this.isDebugMode()) {
      console.log(`%c${this.PREFIX} ${message}`, this.STYLES.debug);
      if (data !== undefined) {
        console.log(data);
      }
    }
  }

  static group(title: string, collapsed: boolean = false): void {
    if (collapsed) {
      console.groupCollapsed(`%c${this.PREFIX} ${title}`, this.STYLES.header);
    } else {
      console.group(`%c${this.PREFIX} ${title}`, this.STYLES.header);
    }
  }

  static groupEnd(): void {
    console.groupEnd();
  }

  static table(data: unknown, title?: string): void {
    if (title) {
      this.info(title);
    }
    console.table(data);
  }

  private static isDebugMode(): boolean {
    return (
      import.meta.env.MODE === 'development' ||
      import.meta.env.DEV === true ||
      localStorage.getItem('bigshot-debug') === 'true' ||
      window.location.search.includes('debug=true')
    );
  }
}

// Environment detection and validation
export interface EnvironmentInfo {
  userAgent: string;
  platform: string;
  language: string;
  viewport: {
    width: number;
    height: number;
  };
  screen: {
    width: number;
    height: number;
    colorDepth: number;
  };
  connection?: {
    effectiveType?: string;
    downlink?: number;
    rtt?: number;
  };
  memory?: number;
  hardwareConcurrency: number;
  cookieEnabled: boolean;
  doNotTrack: string | null;
  online: boolean;
  timezone: string;
  timestamp: string;
}

export function getEnvironmentInfo(): EnvironmentInfo {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const nav = navigator as any; // Type assertion for experimental APIs
  
  return {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight
    },
    screen: {
      width: screen.width,
      height: screen.height,
      colorDepth: screen.colorDepth
    },
    connection: nav.connection ? {
      effectiveType: nav.connection.effectiveType,
      downlink: nav.connection.downlink,
      rtt: nav.connection.rtt
    } : undefined,
    memory: nav.deviceMemory,
    hardwareConcurrency: navigator.hardwareConcurrency,
    cookieEnabled: navigator.cookieEnabled,
    doNotTrack: navigator.doNotTrack,
    online: navigator.onLine,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    timestamp: new Date().toISOString()
  };
}

// Configuration validation
export interface ConfigValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  config: Record<string, unknown>;
}

export function validateFrontendConfig(): ConfigValidationResult {
  const result: ConfigValidationResult = {
    isValid: true,
    errors: [],
    warnings: [],
    config: {}
  };

  // Check required environment variables
  const requiredEnvVars = [
    'VITE_API_BASE_URL',
    'VITE_WS_URL'
  ];

  for (const envVar of requiredEnvVars) {
    const value = import.meta.env[envVar];
    result.config[envVar] = value;
    
    if (!value) {
      result.errors.push(`Required environment variable ${envVar} is not set`);
      result.isValid = false;
    } else {
      // Validate URL format
      if (envVar.includes('URL')) {
        try {
          new URL(value);
        } catch {
          result.errors.push(`Environment variable ${envVar} is not a valid URL: ${value}`);
          result.isValid = false;
        }
      }
    }
  }

  // Check optional environment variables
  const optionalEnvVars = [
    'VITE_APP_NAME',
    'VITE_APP_VERSION',
    'VITE_LOG_LEVEL'
  ];

  for (const envVar of optionalEnvVars) {
    const value = import.meta.env[envVar];
    result.config[envVar] = value;
    
    if (!value) {
      result.warnings.push(`Optional environment variable ${envVar} is not set`);
    }
  }

  // Check browser capabilities
  if (!window.fetch) {
    result.errors.push('Browser does not support fetch API');
    result.isValid = false;
  }

  if (!window.WebSocket) {
    result.errors.push('Browser does not support WebSocket API');
    result.isValid = false;
  }

  if (!window.localStorage) {
    result.warnings.push('Browser does not support localStorage');
  }

  return result;
}

// Performance monitoring utilities
export class PerformanceMonitor {
  private static marks = new Map<string, number>();

  static mark(name: string): void {
    this.marks.set(name, performance.now());
    FrontendDebugger.debug(`Performance mark: ${name}`);
  }

  static measure(name: string, startMark: string): number {
    const startTime = this.marks.get(startMark);
    if (!startTime) {
      FrontendDebugger.warning(`Start mark '${startMark}' not found`);
      return 0;
    }

    const duration = performance.now() - startTime;
    FrontendDebugger.debug(`Performance measure: ${name} = ${duration.toFixed(2)}ms`);
    return duration;
  }

  static getNavigationTiming(): Record<string, number> {
    const timing = performance.timing;
    return {
      domainLookup: timing.domainLookupEnd - timing.domainLookupStart,
      connect: timing.connectEnd - timing.connectStart,
      request: timing.responseStart - timing.requestStart,
      response: timing.responseEnd - timing.responseStart,
      domProcessing: timing.domComplete - timing.domLoading,
      total: timing.loadEventEnd - timing.navigationStart
    };
  }
}

// Debug package creation for frontend
export async function createFrontendDebugInfo(): Promise<Record<string, unknown>> {
  const debugInfo = {
    timestamp: new Date().toISOString(),
    environment: getEnvironmentInfo(),
    config: validateFrontendConfig(),
    performance: {
      navigation: PerformanceMonitor.getNavigationTiming(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      memory: (performance as any).memory ? {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
      } : undefined
    },
    localStorage: Object.keys(localStorage).reduce((acc, key) => {
      // Only include non-sensitive localStorage items
      if (!key.includes('token') && !key.includes('password') && !key.includes('secret')) {
        acc[key] = localStorage.getItem(key);
      } else {
        acc[key] = '***REDACTED***';
      }
      return acc;
    }, {} as Record<string, string | null>),
    sessionStorage: Object.keys(sessionStorage).reduce((acc, key) => {
      // Only include non-sensitive sessionStorage items
      if (!key.includes('token') && !key.includes('password') && !key.includes('secret')) {
        acc[key] = sessionStorage.getItem(key);
      } else {
        acc[key] = '***REDACTED***';
      }
      return acc;
    }, {} as Record<string, string | null>),
    errors: getStoredErrors(),
    console: getConsoleHistory()
  };

  return debugInfo;
}

// Error storage for debugging
let storedErrors: Array<{timestamp: string, error: unknown, stack?: string}> = [];

export function storeError(error: unknown, context?: string): void {
  const errorInfo = {
    timestamp: new Date().toISOString(),
    error: error instanceof Error ? error.toString() : String(error),
    stack: error instanceof Error ? error.stack : undefined,
    context,
    url: window.location.href
  };
  
  storedErrors.push(errorInfo);
  
  // Keep only last 50 errors
  if (storedErrors.length > 50) {
    storedErrors = storedErrors.slice(-50);
  }
  
  FrontendDebugger.error(`Error stored: ${error instanceof Error ? error.toString() : String(error)}`, errorInfo);
}

export function getStoredErrors(): Array<{timestamp: string, error: unknown, stack?: string}> {
  return [...storedErrors];
}

export function clearStoredErrors(): void {
  storedErrors = [];
  FrontendDebugger.info('Stored errors cleared');
}

// Console history (simplified version for debugging)
let consoleHistory: Array<{timestamp: string, level: string, message: string}> = [];

// Override console methods to capture history
const originalConsole = {
  log: console.log,
  warn: console.warn,
  error: console.error,
  info: console.info
};

if (import.meta.env.MODE === 'development') {
  ['log', 'warn', 'error', 'info'].forEach(level => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (console as any)[level] = function(...args: unknown[]) {
      // Store in history
      consoleHistory.push({
        timestamp: new Date().toISOString(),
        level,
        message: args.map(arg => 
          typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ')
      });
      
      // Keep only last 100 entries
      if (consoleHistory.length > 100) {
        consoleHistory = consoleHistory.slice(-100);
      }
      
      // Call original
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (originalConsole as any)[level].apply(console, args);
    };
  });
}

export function getConsoleHistory(): Array<{timestamp: string, level: string, message: string}> {
  return [...consoleHistory];
}

export function clearConsoleHistory(): void {
  consoleHistory = [];
  FrontendDebugger.info('Console history cleared');
}

// Auto-initialize debugging
export function initializeFrontendDebugging(): void {
  FrontendDebugger.header('Frontend Debugging Initialized');
  
  // Log environment info
  FrontendDebugger.group('Environment Information');
  FrontendDebugger.table(getEnvironmentInfo());
  FrontendDebugger.groupEnd();
  
  // Validate configuration
  const configValidation = validateFrontendConfig();
  FrontendDebugger.group('Configuration Validation');
  
  if (configValidation.isValid) {
    FrontendDebugger.success('Configuration is valid');
  } else {
    FrontendDebugger.error('Configuration has errors', configValidation.errors);
  }
  
  if (configValidation.warnings.length > 0) {
    FrontendDebugger.warning('Configuration warnings', configValidation.warnings);
  }
  
  FrontendDebugger.table(configValidation.config);
  FrontendDebugger.groupEnd();
  
  // Setup error handling
  window.addEventListener('error', (event) => {
    storeError(event.error, 'Global error handler');
  });
  
  window.addEventListener('unhandledrejection', (event) => {
    storeError(event.reason, 'Unhandled promise rejection');
  });
  
  FrontendDebugger.success('Frontend debugging setup complete');
}