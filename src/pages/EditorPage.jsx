import React, { useState, useEffect } from 'react'
import Toolbar from '../components/Toolbar'
import Editor from '../components/Editor'
import StatsPanel from '../components/StatsPanel'
import { useNavigate } from 'react-router-dom'

export default function EditorPage() {
  const [text, setText] = useState('')
  const [guest, setGuest] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (localStorage.getItem('guest') === 'true') {
      setGuest(true)
    }
  }, [])

  return (
    <div className="flex flex-col min-h-screen bg-gray-100 p-6">
      <Toolbar
        onSave={() => {
          if (guest) return alert('Modo invitado: no se puede guardar.')
          alert('Guardar (pendiente de backend)')
        }}
        onAI={() => alert('Corregir con IA (pendiente de backend)')}
        onExport={() => {
          if (guest) return alert('Modo invitado: no se puede exportar.')
          alert('Exportar (pendiente de backend)')
        }}
      />
      <div className="flex-1 mt-4 grid grid-cols-1 md:grid-cols-[1fr_18rem] gap-6">
        <div className="bg-white p-4 rounded-xl shadow">
          {guest && (
            <div className="bg-yellow-100 text-yellow-800 p-2 rounded-lg mb-3 text-center text-sm">
              Estás en modo invitado. Los documentos no se guardarán permanentemente.
            </div>
          )}
          <Editor value={text} onChange={setText} />
        </div>
        <StatsPanel text={text} />
      </div>
      <div className="mt-4 text-sm">
        <button onClick={() => navigate('/plantillas')} className="underline">
          Ir a plantillas
        </button>
      </div>
    </div>
  )
}
