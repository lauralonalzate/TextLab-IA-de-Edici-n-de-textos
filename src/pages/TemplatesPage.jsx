import React from 'react'

const items = [
  { title:'Informe técnico', desc:'Estructura base para reportes técnicos.' },
  { title:'Proyecto final', desc:'Secciones para memoria de proyecto.' },
  { title:'Artículo APA', desc:'Plantilla alineada a APA 7.' },
]

export default function TemplatesPage() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold mb-4" style={{color:'var(--brand)'}}>Plantillas de informes académicos</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {items.map((it)=> (
            <div key={it.title} className="bg-white rounded-xl shadow p-4">
              <h3 className="font-semibold">{it.title}</h3>
              <p className="text-sm text-gray-600">{it.desc}</p>
              <button className="mt-3 px-3 py-2 rounded text-white" style={{background:'var(--brand)'}}>Usar plantilla</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
