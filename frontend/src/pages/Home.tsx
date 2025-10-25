import { Link } from 'react-router-dom'
import AppLayout from '../ui/AppLayout'

export default function Home() {
  return (
    <AppLayout>
      <div className="px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-slate-900 mb-4">
            Multi-Agentni RAG Sistem
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Obrađujte dokumente sa AI agentima, uvozite SQL podatke i razgovarajte sa svojom bazom znanja koristeći naprednu RAG tehnologiju.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-12">
          <Link
            to="/documents"
            className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow border border-slate-200"
          >
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow border border-slate-200"
          >
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mb-2">RAG Chat</h3>
            <p className="text-slate-600">
              Postavite pitanja i dobijte AI odgovore sa citatima iz vaših dokumenata i uvezenih izvora podataka.
            </p>
          </Link>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-8 max-w-4xl mx-auto border border-slate-200">
          <h2 className="text-3xl font-bold text-slate-900 mb-6">Mogućnosti</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">Multi-Agentni Pipeline</h3>
              <p className="text-sm text-slate-600">
                MIME detekcija, ekstrakcija teksta, OCR, dijeljenje, embedding i indeksiranje agenata rade zajedno.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">SQL Uvoz</h3>
              <p className="text-sm text-slate-600">
                Povežite se sa vanjskim bazama podataka i uvezite podatke putem SQL upita za RAG pretragu.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">Hibridna Pretraga</h3>
              <p className="text-sm text-slate-600">
                BM25 + pgvector sličnost pretraga za optimalne performanse pretraživanja.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
