import React from "react";
import { useNavigate } from "react-router-dom";

const TEMPLATES = [
  {
    id: "carta",
    title: "Carta formal",
    description: "Estructura básica de carta formal.",
    html: `<p>Medellín, 11 de junio de 2025</p>
<p>Señor(a):<br><strong>Nombre del destinatario</strong><br>Empresa</p>
<p>Asunto: <em>Motivo de la carta</em></p>
<p>Respetado(a) Señor(a):</p>
<p>Me permito informar que ...</p>
<p>Cordialmente,<br><strong>Tu nombre</strong></p>`,
  },
  {
    id: "informe",
    title: "Informe académico",
    description: "Plantilla de informe con secciones.",
    html: `<h2>Resumen</h2><p>…</p><h2>Introducción</h2><p>…</p><h2>Metodología</h2><p>…</p><h2>Resultados</h2><p>…</p><h2>Conclusiones</h2><p>…</p>`,
  },
  {
    id: "acta",
    title: "Acta de reunión",
    description: "Formato breve con asistentes y conclusiones.",
    html: `<h2>Acta de reunión</h2><p><strong>Fecha:</strong> …</p><p><strong>Asistentes:</strong> …</p><h3>Agenda</h3><ul><li>Punto 1</li><li>Punto 2</li></ul><h3>Conclusiones</h3><p>…</p>`,
  },
];

export default function TemplatesPage() {
  const navigate = useNavigate();

  const useTemplate = (tpl) => {
    navigate("/editor", {
      replace: false,
      state: { fromTemplate: true, title: tpl.title, html: tpl.html },
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">Plantillas</h1>
      </div>

      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {TEMPLATES.map((tpl) => (
          <div
            key={tpl.id}
            className="border rounded-lg p-4 hover:shadow cursor-pointer bg-white"
            onClick={() => useTemplate(tpl)}
          >
            <h3 className="font-medium">{tpl.title}</h3>
            <p className="text-sm text-gray-600 mt-1">{tpl.description}</p>
            <div className="mt-3">
              <span className="inline-block text-blue-600 text-sm">
                Usar esta plantilla →
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
