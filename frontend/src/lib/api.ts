// src/lib/api.ts
import axios from 'axios'

const api = axios.create({ baseURL: '' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// --- AUTH ---
export const auth = {
  signup: (email: string, password: string) =>
    api.post('/api/auth/signup', { email, password }, {
      headers: { 'Content-Type': 'application/json' },
    }),
  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }, {
      headers: { 'Content-Type': 'application/json' },
    }),
}

// --- DOCUMENTS ---
export const documents = {
  upload: (file: File, sourceName?: string) => {
    const fd = new FormData()
    fd.append('file', file) // ključ MORA biti "file"
    if (sourceName) fd.append('source_name', sourceName)
    return api.post('/api/documents/upload', fd) // bez Content-Type
  },
  list: () => api.get('/api/documents'),
  get: (id: string) => api.get(`/api/documents/${id}`),
  delete: (id: string) => api.delete(`/api/documents/${id}`),
  deleteAll: () => api.delete('/api/documents'),
}

// --- CHAT/SEARCH ---
export const chat = {
  query: (query: string, top_k = 5) =>
    api.post('/api/chat', { query, top_k }, {
      headers: { 'Content-Type': 'application/json' },
    }),
  search: (query: string, top_k = 5) =>
    api.post('/api/search', { query, top_k }, {
      headers: { 'Content-Type': 'application/json' },
    }),
}

// --- INGEST (traži ga Settings.tsx) ---
export const ingest = {
  sql: (sourceName: string, query: string, connectionString?: string) =>
    api.post('/api/ingest/sql', {
      source_name: sourceName,
      query,
      connection_string: connectionString,
    }, {
      headers: { 'Content-Type': 'application/json' },
    }),
}

export default api
