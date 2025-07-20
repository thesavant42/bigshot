import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0', // Allow external connections in Docker
    watch: {
      usePolling: true, // Enable polling for Docker volumes
      interval: 500,    // Poll every 500ms for faster detection
      binaryInterval: 1000, // Binary files polling interval
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
      },
      '/socket.io': {
        target: process.env.VITE_API_URL || 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
  },
})
