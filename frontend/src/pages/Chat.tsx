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
      <div className="px-4">
        <h1 className="text-3xl font-bold text-slate-900 mb-6">RAG Chat</h1>
        
        <div className="max-w-4xl mx-auto">
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h2 className="font-semibold text-blue-900 mb-2">Kako radi</h2>
            <p className="text-sm text-blue-800">
              Postavite pitanja o vašim učitanim dokumentima i SQL podacima. Sistem koristi hibridnu pretragu
              (BM25 + vektorsku sličnost) da pronađe relevantne informacije i generiše odgovore sa citatima.
            </p>
          </div>

          <ChatWindow onSendMessage={handleSendMessage} />
        </div>
      </div>
    </AppLayout>
  )
}
