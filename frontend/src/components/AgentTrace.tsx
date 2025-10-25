import { formatDate } from '../lib/utils'

interface AgentLog {
  agent: string
  status: string
  message: string
  timestamp: string
  metadata?: any
}

interface AgentTraceProps {
  logs: AgentLog[]
  metadata?: any
}

export default function AgentTrace({ logs, metadata }: AgentTraceProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <span className="text-green-500">✓</span>
      case 'failed':
        return <span className="text-red-500">✗</span>
      case 'processing':
        return <span className="text-blue-500">⟳</span>
      default:
        return <span className="text-gray-500">○</span>
    }
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">Agent Pipeline Trace</h3>
      
      {metadata && (
        <div className="bg-slate-50 rounded-lg p-4 mb-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {metadata.chunks !== undefined && (
            <div>
              <div className="text-slate-600">Chunks</div>
              <div className="font-semibold text-slate-900">{metadata.chunks}</div>
            </div>
          )}
          {metadata.text_length !== undefined && (
            <div>
              <div className="text-slate-600">Text Length</div>
              <div className="font-semibold text-slate-900">{metadata.text_length}</div>
            </div>
          )}
          {metadata.rows_fetched !== undefined && (
            <div>
              <div className="text-slate-600">Rows Fetched</div>
              <div className="font-semibold text-slate-900">{metadata.rows_fetched}</div>
            </div>
          )}
        </div>
      )}

      <div className="space-y-3">
        {logs.map((log, index) => (
          <div key={index} className="flex items-start gap-3">
            <div className="text-2xl">{getStatusIcon(log.status)}</div>
            <div className="flex-1">
              <div className="flex items-baseline justify-between">
                <span className="font-medium text-slate-900">{log.agent}</span>
                <span className="text-xs text-slate-500">{formatDate(log.timestamp)}</span>
              </div>
              <p className="text-sm text-slate-600">{log.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
