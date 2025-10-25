import { Link } from 'react-router-dom'
import AppLayout from '../ui/AppLayout'

export default function Home() {
  return (
    <AppLayout>
      <div className="px-4 py-12">
        <div className="text-center mb-12">
          <div className="inline-block px-4 py-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full text-sm font-semibold text-blue-900 mb-4">
            Multi-Agent RAG System v1.0
          </div>
          <h1 className="text-5xl font-bold text-slate-900 mb-4">
            Multi-Agentni RAG Sistem
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Obrađujte dokumente sa AI agentima, uvozite SQL podatke i razgovarajte sa svojom bazom znanja koristeći naprednu multi-agentnu RAG arhitekturu.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto mb-12">
          <Link
            to="/documents"
            className="group bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all border border-slate-200 hover:border-blue-300"
          >
            <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mb-2">Učitaj Dokumente</h3>
            <p className="text-slate-600">
              Učitajte PDF, DOCX, Excel, CSV i slike. Gledajte kako naši multi-agentni pipeline ih obrađuje sa OCR-om, dijeljenjem i embeddingom.
            </p>
          </Link>

          <Link
            to="/chat"
            className="group bg-gradient-to-br from-blue-600 to-purple-600 p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all border border-blue-700"
          >
            <div className="w-14 h-14 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Multi-Agent RAG Chat</h3>
            <p className="text-blue-100">
              Postavite pitanja i dobijte AI odgovore sa citatima, evaluacijom kvaliteta i iterativnim poboljšanjima.
            </p>
          </Link>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-8 max-w-5xl mx-auto border border-slate-200 mb-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-6 flex items-center gap-3">
            <span className="text-3xl">🚀</span>
            Napredne Mogućnosti
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-5 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200">
              <div className="text-2xl mb-3">🎯</div>
              <h3 className="font-semibold text-slate-900 mb-2">Multi-Agent Query Pipeline</h3>
              <p className="text-sm text-slate-700 leading-relaxed">
                5 specijalizovanih agenata: Planner, Rewriter, Generation, Judge i Summarizer rade zajedno za optimalne rezultate.
              </p>
            </div>
            <div className="p-5 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200">
              <div className="text-2xl mb-3">🔍</div>
              <h3 className="font-semibold text-slate-900 mb-2">RRF Hibridna Pretraga</h3>
              <p className="text-sm text-slate-700 leading-relaxed">
                Reciprocal Rank Fusion kombinuje BM25 text search i pgvector similarity za najbolje rezultate pretrage.
              </p>
            </div>
            <div className="p-5 bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200">
              <div className="text-2xl mb-3">⚖️</div>
              <h3 className="font-semibold text-slate-900 mb-2">Quality Judge & Iteration</h3>
              <p className="text-sm text-slate-700 leading-relaxed">
                Judge agent evaluira svaki odgovor i automatski iterira sa više konteksta ako detektuje nedostatke.
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl shadow-sm p-8 max-w-5xl mx-auto border border-slate-200">
          <h2 className="text-2xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <span className="text-2xl">⚡</span>
            Dodatne Funkcionalnosti
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <span>📊</span>
                SQL Uvoz Podataka
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Povežite se sa vanjskim bazama podataka i uvezite podatke putem SELECT upita za RAG pretragu i analizu.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <span>🔐</span>
                Sigurnost i Skalabilnost
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                JWT autentikacija, bcrypt hashing, PostgreSQL sa pgvector, optimizovano za Replit Autoscale deployment.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
