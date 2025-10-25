import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { auth } from '../lib/api'

export default function Login() {
  const navigate = useNavigate()
  const [isSignup, setIsSignup] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = isSignup
        ? await auth.signup(email, password)
        : await auth.login(email, password)

      localStorage.setItem('token', response.data.access_token)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Multi-RAG</h1>
          <p className="text-slate-600">Multi-Agentni Sistem za Prošireno Pretraživanje</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-8">
          <h2 className="text-2xl font-bold mb-6 text-slate-900">
            {isSignup ? 'Kreiraj Račun' : 'Prijavi se'}
          </h2>

          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Lozinka
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 font-medium disabled:bg-blue-400"
            >
              {loading ? 'Obrađujem...' : isSignup ? 'Registruj se' : 'Prijavi se'}
            </button>
          </form>

          <div className="mt-4 text-center">
            <button
              onClick={() => setIsSignup(!isSignup)}
              className="text-blue-600 hover:underline text-sm"
            >
              {isSignup
                ? 'Već imaš račun? Prijavi se'
                : 'Trebaš račun? Registruj se'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
