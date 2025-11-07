import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Completa todos los campos')
      return
    }
    setError('')
    localStorage.setItem('token', 'demo-token')
    navigate('/editor')
  }

  // 🔹 Modo invitado habilitado (para la demo)
  const handleGuestLogin = () => {
    localStorage.setItem('token', 'guest-token') // pasa ProtectedRoute
    localStorage.setItem('guest', 'true')        // marca modo invitado
    window.location.href = '/editor'
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow w-80">
        <h1 className="text-2xl font-bold mb-4" style={{ color: 'var(--brand)' }}>
          TextLab
        </h1>
        <input
          className="w-full p-2 border rounded mb-3"
          type="email"
          placeholder="Correo"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="w-full p-2 border rounded mb-3"
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
        <button className="w-full py-2 rounded text-white" style={{ background: 'var(--brand)' }}>
          Iniciar sesión
        </button>

        {/* 🔹 Botón para invitado */}
        <div className="mt-4 text-center">
          <button
            type="button"
            onClick={handleGuestLogin}
            className="text-sm text-blue-600 hover:underline"
          >
            Entrar como invitado
          </button>
        </div>
      </form>
    </div>
  )
}
