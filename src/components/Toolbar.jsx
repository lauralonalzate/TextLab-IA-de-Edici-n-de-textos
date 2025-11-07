import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function Toolbar({ onSave, onAI, onExport }) {
  const navigate = useNavigate()

  const handleLogout = () => {
  if (confirm('¿Deseas cerrar sesión?')) {
    localStorage.removeItem('token')
    localStorage.removeItem('guest')
    navigate('/login')
  }
}


  return (
    <div className="flex justify-between items-center p-4 bg-white shadow-sm rounded-xl">
      <h1 className="text-2xl font-bold" style={{ color: 'var(--brand)' }}>
        TextLab
      </h1>

      <div className="flex items-center gap-3 flex-wrap">
        <button onClick={onSave} className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">
          Guardar
        </button>
        <button
          onClick={onAI}
          className="px-4 py-2 rounded-lg text-white"
          style={{ background: 'var(--brand)' }}
        >
          Corregir con IA
        </button>
        <button onClick={onExport} className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">
          Exportar
        </button>
        {/* 🔐 Cerrar sesión */}
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
        >
          Cerrar sesión
        </button>
      </div>
    </div>
  )
}
