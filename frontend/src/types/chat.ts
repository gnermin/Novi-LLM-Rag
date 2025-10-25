// TypeScript tipovi za Chat API responses

export interface Citation {
  chunk_id: string
  document_id: string
  filename: string
  content: string
  score: number
  metadata?: Record<string, any>
}

export interface Verdict {
  ok: boolean
  needs_more: boolean
  notes?: string
}

export interface ChatResponse {
  answer: string
  citations: Citation[]
  query: string
  verdict?: Verdict
  summary?: string
}

export interface SearchResponse {
  results: Citation[]
  total: number
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  verdict?: Verdict
  summary?: string
}
