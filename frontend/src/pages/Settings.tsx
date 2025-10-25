import { useState } from 'react'
import AppLayout from '../ui/AppLayout'
import { ingest } from '../lib/api'

export default function Settings() {
  const [sourceName, setSourceName] = useState('')
  const [query, setQuery] = useState('SELECT * FROM customers LIMIT 100')
  const [connectionString, setConnectionString] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await ingest.sql(
        sourceName,
        query,
        connectionString || undefined
      )
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'SQL ingestion failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="px-4">
        <h1 className="text-3xl font-bold text-slate-900 mb-6">Settings</h1>

        <div className="max-w-3xl">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-4">SQL Data Ingestion</h2>
            <p className="text-slate-600 mb-6">
              Connect to an external database and ingest data via SQL queries. The data will be
              processed, embedded, and made searchable through the RAG system.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Source Name
                </label>
                <input
                  type="text"
                  value={sourceName}
                  onChange={(e) => setSourceName(e.target.value)}
                  placeholder="e.g., Customers Database"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  SQL Query
                  <span className="text-slate-500 font-normal ml-2">(SELECT queries only)</span>
                </label>
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="SELECT * FROM table_name LIMIT 100"
                  rows={4}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none font-mono text-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Connection String
                  <span className="text-slate-500 font-normal ml-2">(Optional - uses EXTERNAL_DB_URL from env if not provided)</span>
                </label>
                <input
                  type="text"
                  value={connectionString}
                  onChange={(e) => setConnectionString(e.target.value)}
                  placeholder="postgresql://user:password@host:port/database"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none font-mono text-sm"
                />
              </div>

              {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg">
                  {error}
                </div>
              )}

              {result && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-semibold text-green-900 mb-2">Success!</h3>
                  <p className="text-sm text-green-800">{result.message}</p>
                  <p className="text-sm text-green-700 mt-2">
                    Document ID: {result.document_id}
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 font-medium disabled:bg-blue-400"
              >
                {loading ? 'Ingesting Data...' : 'Ingest Data'}
              </button>
            </form>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-semibold text-yellow-900 mb-2">Security Notice</h3>
            <p className="text-sm text-yellow-800">
              Only SELECT queries are allowed for security reasons. Destructive operations
              (DELETE, UPDATE, DROP) are blocked by the system.
            </p>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
