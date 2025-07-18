/// <reference types="vite/client" />

// For production, use relative URLs (empty string) that nginx will proxy
// For development, use localhost with the correct port
const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl === "") {
    return ""; // Production: use relative URLs, nginx will proxy
  }
  return envUrl || 'http://localhost:5000'; // Development fallback
};

export const API_BASE_URL = getApiBaseUrl();