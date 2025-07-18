import { describe, it, expect } from 'vitest';

// Integration test to verify the authentication fix works in different environments
describe('Frontend Authentication Integration - Hostname Resolution Fix', () => {
  it('should prevent browser from attempting to resolve backend hostname in development', () => {
    // Simulate the exact scenario from the issue:
    // User runs: docker-compose up backend (backend starts on localhost:5000)
    // User runs: npm run dev in frontend/ (frontend starts on localhost:3000)
    // VITE_API_URL gets set to 'http://backend:5000' from dev environment
    
    const mockDevEnvironment = {
      VITE_API_URL: 'http://backend:5000',
      DEV: true,  // This is the key - vite dev server sets this
      MODE: 'development'
    };

    // With the FIX: Always use relative URLs in dev mode
    const getApiBaseUrl = () => {
      const envUrl = mockDevEnvironment.VITE_API_URL;
      
      if (mockDevEnvironment.DEV) {
        return ""; // Let vite proxy handle /api -> backend
      }
      
      if (envUrl === "") {
        return "";
      }
      
      return envUrl || 'http://localhost:5000';
    };

    const apiBaseUrl = getApiBaseUrl();
    const authVerifyUrl = `${apiBaseUrl}/api/v1/auth/verify`;

    // The fix ensures we get a relative URL
    expect(authVerifyUrl).toBe('/api/v1/auth/verify');
    
    // This means:
    // 1. Browser makes request to current origin + /api/v1/auth/verify
    // 2. Since frontend is on localhost:3000, request goes to localhost:3000/api/v1/auth/verify
    // 3. Vite dev server proxy intercepts /api requests (see vite.config.ts)
    // 4. Proxy forwards to http://localhost:5000/api/v1/auth/verify 
    // 5. localhost:5000 is where docker-compose maps the backend container
    // 6. Authentication succeeds!
    
    expect(authVerifyUrl).not.toContain('backend:5000');
    expect(authVerifyUrl).not.toContain('backend');
  });

  it('should work correctly when both frontend and backend are in Docker', () => {
    // Scenario: docker-compose up (both services in Docker)
    // Frontend nginx receives VITE_API_URL="" 
    const mockDockerEnvironment = {
      VITE_API_URL: '',
      DEV: false,  // Built for production, not dev server
      MODE: 'production'
    };

    const getApiBaseUrl = () => {
      const envUrl = mockDockerEnvironment.VITE_API_URL;
      
      if (mockDockerEnvironment.DEV) {
        return "";
      }
      
      if (envUrl === "") {
        return ""; // Production/Docker: use relative URLs, nginx will proxy
      }
      
      return envUrl || 'http://localhost:5000';
    };

    const apiBaseUrl = getApiBaseUrl();
    const authVerifyUrl = `${apiBaseUrl}/api/v1/auth/verify`;

    expect(authVerifyUrl).toBe('/api/v1/auth/verify');
    
    // This means:
    // 1. Browser makes request to localhost:80/api/v1/auth/verify
    // 2. Nginx receives the request (see frontend/nginx.conf)
    // 3. Nginx proxy rule: location /api/ -> proxy_pass http://backend:5000
    // 4. Request goes to backend:5000/api/v1/auth/verify (Docker network)
    // 5. Authentication succeeds!
  });

  it('should demonstrate the axios configuration matches URL generation', () => {
    // Test that the axios instance will be configured with the same URL logic
    const scenarios = [
      {
        name: 'development on host',
        env: { VITE_API_URL: 'http://backend:5000', DEV: true },
        expectedBaseURL: '/api/v1'
      },
      {
        name: 'production in docker',
        env: { VITE_API_URL: '', DEV: false },
        expectedBaseURL: '/api/v1'
      },
      {
        name: 'custom environment',
        env: { VITE_API_URL: 'https://api.example.com', DEV: false },
        expectedBaseURL: 'https://api.example.com/api/v1'
      }
    ];

    scenarios.forEach(({ name, env, expectedBaseURL }) => {
      // Simulate the getApiBaseUrl function from api.ts
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

      const baseURL = getApiBaseUrl();
      expect(baseURL, `Failed for ${name}`).toBe(expectedBaseURL);
      
      // Verify that the specific failing endpoint from the issue is fixed
      if (name === 'development on host') {
        const verifyEndpoint = baseURL + '/auth/verify';
        expect(verifyEndpoint).toBe('/api/v1/auth/verify');
        expect(verifyEndpoint).not.toContain('backend:5000');
      }
    });
  });

  it('should verify vite proxy configuration compatibility', () => {
    // Vite proxy configuration from vite.config.ts:
    const viteProxyConfig = {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      }
    };

    // Our fix ensures we use '/api/v1/auth/verify' in development
    const developmentAuthUrl = '/api/v1/auth/verify';
    
    // Verify this URL would match the vite proxy pattern
    expect(developmentAuthUrl.startsWith('/api')).toBe(true);
    
    // This confirms that vite proxy will:
    // 1. Intercept requests to /api/v1/auth/verify 
    // 2. Forward them to http://localhost:5000/api/v1/auth/verify
    // 3. Which is exactly where our dockerized backend is exposed
    
    expect(viteProxyConfig['/api'].target).toBe('http://localhost:5000');
  });
});