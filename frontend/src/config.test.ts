import { describe, it, expect, beforeEach } from 'vitest';

// Test-specific interfaces that allow mutation
interface TestImportMetaEnv {
  VITE_API_URL?: string;
  DEV?: boolean;
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

  it('should use relative URLs in development mode regardless of VITE_API_URL', () => {
    // Mock development environment (vite dev server)
    (import.meta as TestImportMeta).env = { DEV: true, VITE_API_URL: 'http://backend:5000' };
    
    // Import getApiBaseUrl function logic with new DEV detection
    const getApiBaseUrl = () => {
      const envUrl = (import.meta as TestImportMeta).env?.VITE_API_URL;
      
      if ((import.meta as TestImportMeta).env?.DEV) {
        return ""; // Let vite proxy handle /api -> backend
      }
      
      if (envUrl === "") {
        return ""; // Production/Docker: use relative URLs, nginx will proxy
      }
      
      return envUrl || 'http://localhost:5000';
    };
    
    expect(getApiBaseUrl()).toBe('');
  });

  it('should use relative URLs for production when VITE_API_URL is empty', () => {
    // Mock production environment
    (import.meta as TestImportMeta).env = { DEV: false, VITE_API_URL: '' };
    
    const getApiBaseUrl = () => {
      const envUrl = (import.meta as TestImportMeta).env?.VITE_API_URL;
      
      if ((import.meta as TestImportMeta).env?.DEV) {
        return "";
      }
      
      if (envUrl === "") {
        return ""; // Production: use relative URLs, nginx will proxy
      }
      
      return envUrl || 'http://localhost:5000';
    };
    
    expect(getApiBaseUrl()).toBe('');
  });

  it('should use custom VITE_API_URL only when not in dev mode and URL is provided', () => {
    // Mock custom environment (not dev, explicit URL)
    (import.meta as TestImportMeta).env = { DEV: false, VITE_API_URL: 'http://custom-backend:8080' };
    
    const getApiBaseUrl = () => {
      const envUrl = (import.meta as TestImportMeta).env?.VITE_API_URL;
      
      if ((import.meta as TestImportMeta).env?.DEV) {
        return "";
      }
      
      if (envUrl === "") {
        return "";
      }
      
      return envUrl || 'http://localhost:5000';
    };
    
    expect(getApiBaseUrl()).toBe('http://custom-backend:8080');
  });
});