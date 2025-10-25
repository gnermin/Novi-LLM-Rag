import { useState } from 'react'
import type { Message, Citation, Verdict } from '../types/chat'
import VerdictBadge from './VerdictBadge'
import AgentSteps from './AgentSteps'

interface ChatWindowProps {
  onSendMessage: (message: string) => Promise<{
    answer: string
    citations: Citation[]
    verdict?: Verdict
    summary?: string
  }>
}

export default function ChatWindow({ onSendMessage }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await onSendMessage(input)
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
        verdict: response.verdict,
        summary: response.summary,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Greška pri obradi upita. Molimo pokušajte ponovo.',
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[700px] bg-white rounded-2xl shadow-sm border border-slate-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <h2 className="font-semibold text-slate-900">Multi-Agent RAG Chat</h2>
        <p className="text-xs text-slate-600 mt-1">
          Powered by: Planner → Rewriter → RRF Search → Generation → Judge
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-slate-500 mt-20">
            <div className="text-6xl mb-4">💬</div>
            <p className="text-lg font-medium">Postavite pitanje o vašim dokumentima</p>
            <p className="text-sm mt-2 text-slate-400">
              Primjeri: "Šta je MPLS?", "Objasni QoS mehanizme"
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-md'
                  : 'bg-slate-50 text-slate-900 border border-slate-200'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-xs font-bold">
                    AI
                  </div>
                  <span className="text-xs font-semibold text-slate-700">Multi-Agent RAG</span>
                </div>
              )}

              <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>

              {/* Summary ako postoji */}
              {message.summary && (
                <div className="mt-3 pt-3 border-t border-slate-200">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-purple-700">📝 Sažetak:</span>
                  </div>
                  <p className="text-xs text-slate-600 italic">{message.summary}</p>
                </div>
              )}

              {/* Verdict Badge */}
              {message.verdict && <VerdictBadge verdict={message.verdict} />}

              {/* Citations */}
              {message.citations && message.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-200 space-y-2">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                    </svg>
                    <p className="text-xs font-semibold text-slate-700">
                      Izvori ({message.citations.length}):
                    </p>
                  </div>
                  {message.citations.map((citation, idx) => (
                    <div key={idx} className="text-xs bg-white rounded-lg p-3 border border-slate-200 hover:border-blue-300 transition-colors">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <div className="font-semibold text-blue-900 flex items-center gap-1">
                            <span className="text-blue-600">📄</span>
                            {citation.filename}
                          </div>
                          <div className="mt-1.5 text-slate-600 line-clamp-3 leading-relaxed">
                            {citation.content}
                          </div>
                        </div>
                        <div className="flex-shrink-0 px-2 py-1 bg-blue-50 rounded text-blue-700 font-mono text-[10px]">
                          {citation.score.toFixed(3)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="max-w-[85%]">
              <AgentSteps isProcessing={loading} />
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="border-t border-slate-200 p-4 bg-slate-50">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Postavite pitanje..."
            className="flex-1 px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none bg-white"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Procesuiram
              </span>
            ) : (
              'Pošalji'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
