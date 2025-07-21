import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  server: {
    host: '0.0.0.0',  
    port: 3000,
    strictPort: true,
    hmr: {
      host: 'localhost',      // Connect HMR websocket to localhost instead of 0.0.0.0
      protocol: 'ws',         // Use ws protocol for HMR
      port: 3000              // Specify HMR websocket port
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://backend:5000',
        changeOrigin: true,
        secure: false,
      },
      '/socket.io': {
        target: process.env.VITE_API_URL || 'http://backend:5000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
  },
  plugins: [react()],
})