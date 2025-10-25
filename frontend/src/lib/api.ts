import axios from 'axios'
import type { ChatResponse, SearchResponse } from '../types/chat'

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const auth = {
  signup: (email: string, password: string) =>
    api.post('/auth/signup', { email, password }),
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
}

export const documents = {
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: () => api.get('/documents'),
  get: (id: string) => api.get(`/documents/${id}`),
}

export const chat = {
  query: (query: string, top_k: number = 5) =>
    api.post<ChatResponse>('/chat', { query, top_k }),
  search: (query: string, top_k: number = 5) =>
    api.post<SearchResponse>('/search', { query, top_k }),
}

export const ingest = {
  sql: (source_name: string, query: string, connection_string?: string) =>
    api.post('/ingest/sql', { source_name, query, connection_string }),
}

export default api
