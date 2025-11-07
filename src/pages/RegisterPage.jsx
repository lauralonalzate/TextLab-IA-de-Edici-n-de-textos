import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!email || !password) { setMsg('Completa todos los campos'); return }
    setMsg('Usuario creado (simulado). Ahora inicia sesión.')
    setTimeout(()=>navigate('/login'), 900)
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow w-80">
        <h1 className="text-2xl font-bold mb-4" style={{color:'var(--brand)'}}>Crear cuenta</h1>
        <input className="w-full p-2 border rounded mb-3" type="email" placeholder="Correo" value={email} onChange={e=>setEmail(e.target.value)} />
        <input className="w-full p-2 border rounded mb-3" type="password" placeholder="Contraseña" value={password} onChange={e=>setPassword(e.target.value)} />
        {msg && <p className="text-sm mb-3">{msg}</p>}
        <button className="w-full py-2 rounded text-white" style={{background:'var(--brand)'}}>Registrarme</button>
        <p className="text-center text-sm mt-3">
          ¿Ya tienes cuenta?{' '}
          <span className="text-blue-600 cursor-pointer" onClick={()=>navigate('/login')}>
            Inicia sesión
          </span>
        </p>
      </form>
    </div>
  )
}
