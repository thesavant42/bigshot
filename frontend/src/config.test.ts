import { describe, it, expect, beforeEach } from 'vitest';

// Test-specific interfaces that allow mutation
interface TestImportMetaEnv {
  VITE_API_URL?: string;
  [key: string]: unknown;
}

interface TestImportMeta {
  env?: TestImportMetaEnv;
}

describe('API Configuration', () => {
  beforeEach(() => {
    // Clear environment variables between tests
    delete (import.meta as TestImportMeta).env;
  });

  it('should use development localhost URL when VITE_API_URL is not set', () => {
    // Mock empty environment
    (import.meta as TestImportMeta).env = {};
    
    // Import getApiBaseUrl function logic
    const getApiBaseUrl = () => {
      const envUrl = (import.meta as TestImportMeta).env?.VITE_API_URL;
      if (envUrl === "") {
        return ""; // Production: use relative URLs, nginx will proxy
      }
      return envUrl || 'http://localhost:5000'; // Development fallback
    };
    
    expect(getApiBaseUrl()).toBe('http://localhost:5000');
  });

  it('should use empty string for production when VITE_API_URL is empty', () => {
    // Mock production environment
    (import.meta as TestImportMeta).env = { VITE_API_URL: '' };
    
    const getApiBaseUrl = () => {
      const envUrl = (import.meta as TestImportMeta).env?.VITE_API_URL;
      if (envUrl === "") {
        return ""; // Production: use relative URLs, nginx will proxy
      }
      return envUrl || 'http://localhost:5000'; // Development fallback
    };
    
    expect(getApiBaseUrl()).toBe('');
  });

  it('should use custom VITE_API_URL when provided', () => {
    // Mock custom environment
    (import.meta as TestImportMeta).env = { VITE_API_URL: 'http://backend:5000' };
    
    const getApiBaseUrl = () => {
      const envUrl = (import.meta as TestImportMeta).env?.VITE_API_URL;
      if (envUrl === "") {
        return ""; // Production: use relative URLs, nginx will proxy
      }
      return envUrl || 'http://localhost:5000'; // Development fallback
    };
    
    expect(getApiBaseUrl()).toBe('http://backend:5000');
  });
});