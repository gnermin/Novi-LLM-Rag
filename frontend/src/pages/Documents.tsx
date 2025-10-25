import { useState, useEffect } from 'react'
import AppLayout from '../ui/AppLayout'
import FileDropzone from '../components/FileDropzone'
import AgentTrace from '../components/AgentTrace'
import { documents } from '../lib/api'
import { formatBytes, formatDate, getStatusColor } from '../lib/utils'

interface Document {
  id: string
  filename: string
  status: string
  mime_type?: string
  file_size?: number
  metadata: any
  created_at: string
  agent_logs?: any[]
}

export default function Documents() {
  const [docs, setDocs] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
  const [error, setError] = useState('')

  const fetchDocuments = async () => {
    try {
      const response = await documents.list()
      setDocs(response.data.documents)
    } catch (err: any) {
      console.error('Error fetching documents:', err)
    }
  }

  useEffect(() => {
    fetchDocuments()
    const interval = setInterval(fetchDocuments, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleFileSelect = async (file: File) => {
    setUploading(true)
    setError('')

    try {
      const response = await documents.upload(file)
      setDocs([response.data, ...docs])
      setSelectedDoc(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <AppLayout>
      <div className="px-4">
        <h1 className="text-3xl font-bold text-slate-900 mb-6">Documents</h1>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <FileDropzone onFileSelect={handleFileSelect} uploading={uploading} />

            {error && (
              <div className="bg-red-50 text-red-600 p-4 rounded-lg">
                {error}
              </div>
            )}

            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">Your Documents</h2>
              
              {docs.length === 0 ? (
                <p className="text-slate-500 text-center py-8">No documents yet. Upload one to get started!</p>
              ) : (
                <div className="space-y-3">
                  {docs.map((doc) => (
                    <div
                      key={doc.id}
                      onClick={() => setSelectedDoc(doc)}
                      className={`p-4 rounded-lg border cursor-pointer transition-all ${
                        selectedDoc?.id === doc.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-slate-900">{doc.filename}</h3>
                          <div className="flex items-center gap-4 mt-2 text-sm text-slate-600">
                            {doc.file_size && <span>{formatBytes(doc.file_size)}</span>}
                            <span>{formatDate(doc.created_at)}</span>
                          </div>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(doc.status)}`}>
                          {doc.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div>
            {selectedDoc && (
              <AgentTrace
                logs={selectedDoc.agent_logs || []}
                metadata={selectedDoc.metadata}
              />
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
