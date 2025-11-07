import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Toolbar from '../components/Toolbar'
import Editor from '../components/Editor'
import StatsPanel from '../components/StatsPanel'

export default function EditorPage() {
  const [text, setText] = useState('')
  const [title, setTitle] = useState('')
  const navigate = useNavigate()

  const isGuest = localStorage.getItem('guest') === 'true'
  const showGuestBanner = isGuest

  // 🔹 Para la demo, habilitamos todo
  const canSave = true
  const canExport = true

  // Guardado
  const handleSave = () => {
    const payload = { title, textHtml: text, ts: Date.now() }
    localStorage.setItem('textlab_demo_doc', JSON.stringify(payload))
    alert('Guardado (demo) ✓ — Se guardó localmente.')
  }

  // Exportación
  const handleExport = () => {
    const plain = text.replace(/<[^>]+>/g, '')
    const name = (title?.trim() || 'documento') + '.txt'
    const blob = new Blob([plain], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-100 p-6">
      <Toolbar onSave={handleSave} onAI={() => alert('Corregir con IA (demo)')} onExport={handleExport} />

      <div className="flex-1 mt-4 grid grid-cols-1 md:grid-cols-[1fr_18rem] gap-6">
        <div className="bg-white p-4 rounded-xl shadow">
          {showGuestBanner && (
            <div className="bg-blue-50 text-blue-700 p-2 rounded mb-3 text-sm text-center">
              Modo invitado habilitado para la demostración — Guardar y Exportar activos.
            </div>
          )}

          <input
            className="w-full p-2 border rounded mb-3"
            placeholder="Título del documento"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          <Editor value={text} onChange={setText} />
        </div>

        <StatsPanel text={text} />
      </div>
    </div>
  )
}
