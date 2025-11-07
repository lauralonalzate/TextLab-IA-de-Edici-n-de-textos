import React from 'react'

export default function StatsPanel({ text }) {
  const plain = (text || '').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim()
  const words = plain ? plain.split(' ').length : 0
  const minutes = Math.max(1, Math.ceil(words / 200))
  const readability = Math.min(100, Math.round((words / 500) * 100))

  return (
    <aside className="bg-gray-50 p-4 rounded-xl shadow w-full md:w-72 h-fit">
      <h3 className="font-semibold text-gray-800 mb-2">Estadísticas del documento</h3>
      <ul className="space-y-1 text-sm">
        <li>Palabras totales: <strong>{words}</strong></li>
        <li>Tiempo estimado de lectura: <strong>{minutes} min</strong></li>
        <li>Legibilidad: <strong>{readability}%</strong></li>
      </ul>
      <p className="mt-3 text-xs text-gray-500 italic">Estas métricas son estimaciones informativas.</p>
    </aside>
  )
}
