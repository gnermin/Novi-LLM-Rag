import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5000,
    strictPort: true,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/documents': 'http://localhost:8000',
      '/chat': 'http://localhost:8000',
      '/search': 'http://localhost:8000',
      '/ingest': 'http://localhost:8000',
      '/health': 'http://localhost:8000'
    }
  }
})
