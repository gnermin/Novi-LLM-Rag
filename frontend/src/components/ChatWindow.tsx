import { useState } from 'react'

interface Citation {
  chunk_id: string
  document_id: string
  filename: string
  content: string
  score: number
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
}

interface ChatWindowProps {
  onSendMessage: (message: string) => Promise<{ answer: string; citations: Citation[] }>
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
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-2xl shadow-sm border border-slate-200">
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-slate-500 mt-20">
            <p className="text-lg">Ask a question about your documents</p>
            <p className="text-sm mt-2">Try: "What information is in my documents?"</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.citations && message.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-300 space-y-2">
                  <p className="text-xs font-semibold">Sources:</p>
                  {message.citations.map((citation, idx) => (
                    <div key={idx} className="text-xs bg-white rounded-lg p-2 text-slate-700">
                      <div className="font-semibold">{citation.filename}</div>
                      <div className="mt-1 line-clamp-2">{citation.content}</div>
                      <div className="text-slate-500 mt-1">Score: {citation.score.toFixed(3)}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl px-4 py-3 text-slate-600">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-slate-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:bg-blue-400"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}
