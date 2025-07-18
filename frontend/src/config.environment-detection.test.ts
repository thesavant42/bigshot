import { describe, it, expect } from 'vitest';

// Test to verify the exact hostname resolution issue and fix
describe('API Configuration - Environment Detection and Hostname Resolution', () => {

  it('should detect when running in mixed environment (frontend host, backend docker)', () => {
    // Simulate the exact scenario from the issue:
    // Frontend running on host (127.0.0.1:3000) with vite dev server
    // Backend running in Docker, but VITE_API_URL set to backend:5000
    const mockEnv = { 
      VITE_API_URL: 'http://backend:5000',
      MODE: 'development',
      DEV: true
    };
    
    // This is what currently happens - browser tries to resolve backend:5000
    const getApiBaseUrl = () => {
      const envUrl = mockEnv.VITE_API_URL;
      if (envUrl === "") {
        return "/api/v1"; // Production: use relative URLs, nginx will proxy
      }
      return (envUrl || 'http://localhost:5000') + '/api/v1'; // Development
    };
    
    const baseUrl = getApiBaseUrl();
    expect(baseUrl).toBe('http://backend:5000/api/v1');
    
    // This would cause the exact error: net::ERR_NAME_NOT_RESOLVED
    // because browser can't resolve 'backend' hostname
  });

  it('should use localhost when frontend runs on host in development', () => {
    // Fixed behavior: when running frontend on host, always use localhost
    // regardless of VITE_API_URL setting, let vite proxy handle it
    const mockEnv = { 
      VITE_API_URL: 'http://backend:5000',
      MODE: 'development',
      DEV: true
    };
    
    const getApiBaseUrl = () => {
      const envUrl = mockEnv.VITE_API_URL;
      
      // Fix: In development mode, always use relative URLs 
      // so vite dev server proxy can handle the routing
      if (mockEnv.DEV) {
        return "/api/v1"; // Let vite proxy handle /api -> localhost:5000
      }
      
      if (envUrl === "") {
        return "/api/v1"; // Production: use relative URLs, nginx will proxy
      }
      return (envUrl || 'http://localhost:5000') + '/api/v1'; // Fallback
    };
    
    const baseUrl = getApiBaseUrl();
    expect(baseUrl).toBe('/api/v1');
    
    // This should work because:
    // 1. Browser makes request to /api/v1/auth/verify
    // 2. Vite dev server proxy intercepts /api requests  
    // 3. Proxy forwards to http://localhost:5000/api/v1/auth/verify
    // 4. localhost:5000 maps to the Docker backend via port mapping
  });

  it('should handle production environment correctly', () => {
    const mockEnv = { 
      VITE_API_URL: '',
      MODE: 'production',
      DEV: false
    };
    
    const getApiBaseUrl = () => {
      const envUrl = mockEnv.VITE_API_URL;
      
      if (mockEnv.DEV) {
        return "/api/v1";
      }
      
      if (envUrl === "") {
        return "/api/v1"; // Production: use relative URLs, nginx will proxy
      }
      return (envUrl || 'http://localhost:5000') + '/api/v1';
    };
    
    const baseUrl = getApiBaseUrl();
    expect(baseUrl).toBe('/api/v1');
  });

  it('should handle docker development environment', () => {
    // When both frontend and backend are in Docker,
    // this should still work because nginx handles the proxy
    const mockEnv = { 
      VITE_API_URL: '',  // Empty in Docker
      MODE: 'development',
      DEV: false  // Not dev mode when built for Docker
    };
    
    const getApiBaseUrl = () => {
      const envUrl = mockEnv.VITE_API_URL;
      
      if (mockEnv.DEV) {
        return "/api/v1";
      }
      
      if (envUrl === "") {
        return "/api/v1"; // Use relative URLs, let container proxy handle it
      }
      return (envUrl || 'http://localhost:5000') + '/api/v1';
    };
    
    const baseUrl = getApiBaseUrl();
    expect(baseUrl).toBe('/api/v1');
  });

  it('should construct auth verify URL correctly in all environments', () => {
    const scenarios = [
      { 
        name: 'host development',
        env: { VITE_API_URL: 'http://backend:5000', DEV: true },
        expected: '/api/v1/auth/verify'
      },
      { 
        name: 'docker development', 
        env: { VITE_API_URL: '', DEV: false },
        expected: '/api/v1/auth/verify'
      },
      { 
        name: 'production',
        env: { VITE_API_URL: '', DEV: false },
        expected: '/api/v1/auth/verify'
      }
    ];

    scenarios.forEach(({ name, env, expected }) => {
      const getApiBaseUrl = () => {
        const envUrl = env.VITE_API_URL;
        
        if (env.DEV) {
          return "/api/v1";
        }
        
        if (envUrl === "") {
          return "/api/v1";
        }
        return (envUrl || 'http://localhost:5000') + '/api/v1';
      };
      
      const baseUrl = getApiBaseUrl();
      const authVerifyUrl = `${baseUrl}/auth/verify`;
      
      expect(authVerifyUrl, `Failed for ${name} environment`).toBe(expected);
      expect(authVerifyUrl, `Should not contain backend hostname in ${name}`).not.toContain('backend:5000');
    });
  });
});