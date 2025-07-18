/// <reference types="vite/client" />

// Smart environment detection for API base URL configuration
// Handles different deployment scenarios:
// 1. Development on host (vite dev server) - use relative URLs for proxy
// 2. Production in Docker - use relative URLs for nginx proxy  
// 3. Development in Docker - use relative URLs for nginx proxy
const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  
  // In development mode (vite dev server), always use relative URLs
  // This allows vite's proxy configuration to handle backend routing
  // regardless of whether backend is on localhost or in Docker
  if (import.meta.env.DEV) {
    return ""; // Let vite proxy handle /api -> backend
  }
  
  // For production and Docker environments, use relative URLs
  // nginx will proxy these to the appropriate backend service
  if (envUrl === "") {
    return ""; // Production/Docker: use relative URLs, nginx will proxy
  }
  
  // Fallback for explicit URL override (rare cases)
  return envUrl || 'http://localhost:5000';
};

export const API_BASE_URL = getApiBaseUrl();