import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    proxy: {
      '/auth': 'http://localhost:5000',
      '/documents': 'http://localhost:5000',
      '/chat': 'http://localhost:5000',
      '/search': 'http://localhost:5000',
      '/ingest': 'http://localhost:5000',
      '/health': 'http://localhost:5000',
      '/api': 'http://localhost:5000'
    }
  }
})
