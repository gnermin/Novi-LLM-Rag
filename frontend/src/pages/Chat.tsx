import AppLayout from '../ui/AppLayout'
import ChatWindow from '../components/ChatWindow'
import { chat } from '../lib/api'

export default function Chat() {
  const handleSendMessage = async (message: string) => {
    const response = await chat.query(message, 5)
    return response.data
  }

  return (
    <AppLayout>
      <div className="px-4 py-6">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-4xl font-bold text-slate-900 mb-3">Multi-Agent RAG Chat</h1>
            <p className="text-slate-600">
              Postavite pitanja o vašim dokumentima pomoću naprednog multi-agentnog sistema
            </p>
          </div>

          {/* Info Cards */}
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">🎯</span>
                <h3 className="font-semibold text-blue-900">Planner & Rewriter</h3>
              </div>
              <p className="text-sm text-blue-800">
                Planner optimizuje strategiju pretrage, a Rewriter parafrazira upit u više varijanti za bolji recall.
              </p>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">🔍</span>
                <h3 className="font-semibold text-purple-900">RRF Search</h3>
              </div>
              <p className="text-sm text-purple-800">
                Reciprocal Rank Fusion kombinuje vector i text search rezultate za optimalne performanse.
              </p>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">⚖️</span>
                <h3 className="font-semibold text-green-900">Judge & Quality</h3>
              </div>
              <p className="text-sm text-green-800">
                Judge agent evaluira kvalitet odgovora i opciono iterira za dodatni kontekst ako je potrebno.
              </p>
            </div>
          </div>

          {/* Chat Window */}
          <ChatWindow onSendMessage={handleSendMessage} />

          {/* Technical Details */}
          <div className="mt-6 bg-slate-50 border border-slate-200 rounded-xl p-5">
            <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <span className="text-xl">⚙️</span>
              Tehnički detalji
            </h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-700">
              <div>
                <strong>Query Pipeline:</strong>
                <ol className="list-decimal list-inside mt-1 space-y-1 text-slate-600">
                  <li>Planner kreira strategiju</li>
                  <li>Rewriter generiše query varijante</li>
                  <li>Multi-query federated search</li>
                  <li>RRF merge rezultata</li>
                  <li>Generation odgovora sa GPT-4o-mini</li>
                  <li>Judge evaluacija i opciona iteracija</li>
                </ol>
              </div>
              <div>
                <strong>Konfiguracija:</strong>
                <ul className="list-disc list-inside mt-1 space-y-1 text-slate-600">
                  <li>Model: GPT-4o-mini</li>
                  <li>Rewrites: 2 varijante upita</li>
                  <li>Top-K: 5 najboljih rezultata</li>
                  <li>RRF parametar k=60</li>
                  <li>Hybrid search: Vector + BM25</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
