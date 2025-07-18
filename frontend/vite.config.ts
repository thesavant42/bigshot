import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
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
