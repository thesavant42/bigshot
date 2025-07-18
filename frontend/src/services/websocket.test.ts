import { describe, it, expect } from 'vitest';

// Recreate the getWebSocketUrl logic for testing
const getWebSocketUrl = (env: { DEV?: boolean; VITE_API_URL?: string }, windowOrigin: string) => {
  const envUrl = env.VITE_API_URL;
  
  // In development mode (vite dev server), always use current origin
  // This allows vite's proxy configuration to handle websocket routing
  // regardless of whether backend is on localhost or in Docker
  if (env.DEV) {
    return windowOrigin; // Let vite proxy handle /socket.io -> backend
  }
  
  // For production and Docker environments, use current origin
  // nginx will proxy these to the appropriate backend service
  if (envUrl === "") {
    return windowOrigin; // Production/Docker: use current origin, nginx will proxy
  }
  
  // Fallback for explicit URL override (rare cases)
  return envUrl || 'http://localhost:5000';
};

describe('WebSocket URL Resolution Logic', () => {
  describe('Development mode (DEV=true)', () => {
    it('should use current origin when VITE_API_URL is set to backend:5000', () => {
      const env = { DEV: true, VITE_API_URL: 'http://backend:5000' };
      const windowOrigin = 'http://localhost:3000';
      
      const result = getWebSocketUrl(env, windowOrigin);
      
      // Should use current origin, not backend:5000
      expect(result).toBe('http://localhost:3000');
      expect(result).not.toContain('backend:5000');
    });

    it('should use current origin when VITE_API_URL is empty', () => {
      const env = { DEV: true, VITE_API_URL: '' };
      const windowOrigin = 'http://localhost:3000';
      
      const result = getWebSocketUrl(env, windowOrigin);
      
      expect(result).toBe('http://localhost:3000');
    });

    it('should use current origin when running in Docker dev', () => {
      const env = { DEV: true, VITE_API_URL: 'http://backend:5000' };
      const windowOrigin = 'http://localhost:3000';
      
      const result = getWebSocketUrl(env, windowOrigin);
      
      // Vite proxy will handle the routing to backend
      expect(result).toBe('http://localhost:3000');
      expect(result).not.toContain('backend');
    });
  });

  describe('Production mode (DEV=false)', () => {
    it('should use current origin when VITE_API_URL is empty', () => {
      const env = { DEV: false, VITE_API_URL: '' };
      const windowOrigin = 'http://myapp.com';
      
      const result = getWebSocketUrl(env, windowOrigin);
      
      expect(result).toBe('http://myapp.com');
    });

    it('should never use backend:5000 in production', () => {
      const env = { DEV: false, VITE_API_URL: '' };
      const windowOrigin = 'https://production.example.com';
      
      const result = getWebSocketUrl(env, windowOrigin);
      
      expect(result).not.toContain('backend:5000');
      expect(result).toBe('https://production.example.com');
    });

    it('should use explicit VITE_API_URL when provided (override case)', () => {
      const env = { DEV: false, VITE_API_URL: 'https://api.example.com' };
      const windowOrigin = 'https://frontend.example.com';
      
      const result = getWebSocketUrl(env, windowOrigin);
      
      expect(result).toBe('https://api.example.com');
    });

    it('should work with Docker production deployment', () => {
      const env = { DEV: false, VITE_API_URL: '' };
      const windowOrigin = 'http://localhost';
      
      const result = getWebSocketUrl(env, windowOrigin);
      
      // nginx will proxy /socket.io/ to backend:5000 internally
      expect(result).toBe('http://localhost');
      expect(result).not.toContain('backend');
    });
  });

  describe('Edge cases', () => {
    it('should fallback to localhost when environment is undefined', () => {
      const env = { DEV: false, VITE_API_URL: undefined };
      const windowOrigin = 'http://localhost:3000';
      
      const result = getWebSocketUrl(env, windowOrigin);
      
      expect(result).toBe('http://localhost:5000');
    });

    it('should handle missing DEV flag gracefully', () => {
      const env = { VITE_API_URL: '' };
      const windowOrigin = 'http://localhost:3000';
      
      const result = getWebSocketUrl(env, windowOrigin);
      
      // Should default to production behavior
      expect(result).toBe('http://localhost:3000');
    });
  });

  describe('Comparison with old behavior', () => {
    it('old behavior would incorrectly use backend:5000 in development', () => {
      // This simulates the OLD problematic behavior
      const oldGetWebSocketUrl = (env: { VITE_API_URL?: string }) => {
        const envUrl = env.VITE_API_URL;
        if (envUrl === "") {
          return 'http://localhost:3000'; // This part was correct
        }
        return envUrl || 'http://localhost:5000'; // This would return backend:5000!
      };

      const env = { VITE_API_URL: 'http://backend:5000' };
      
      const oldResult = oldGetWebSocketUrl(env);
      const newResult = getWebSocketUrl({ DEV: true, ...env }, 'http://localhost:3000');
      
      // Old would use backend:5000 (broken), new uses localhost:3000 (correct)
      expect(oldResult).toContain('backend:5000');
      expect(newResult).toBe('http://localhost:3000');
      expect(newResult).not.toContain('backend:5000');
    });
  });
});