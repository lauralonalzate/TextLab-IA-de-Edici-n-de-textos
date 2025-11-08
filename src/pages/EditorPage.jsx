import React, { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, Link } from "react-router-dom";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import Toolbar from "../components/Toolbar";
import StatsPanel from "../components/StatsPanel";

export default function EditorPage() {
  const location = useLocation();
  const quillRef = useRef(null);

  const [title, setTitle] = useState("");
  const [value, setValue] = useState("");
  const isGuest = Boolean(localStorage.getItem("guest"));

  // Cargar datos si vienen desde /plantillas
  useEffect(() => {
    if (location.state?.fromTemplate) {
      if (location.state.title) setTitle(location.state.title);
      if (location.state.html) setValue(location.state.html);
    }
  }, [location.state]);

  const modules = useMemo(
    () => ({
      toolbar: [
        [{ header: [false, 1, 2, 3] }],
        ["bold", "italic", "underline"],
        [{ list: "bullet" }, { list: "ordered" }],
        [{ align: [] }],
        ["link", "image"],
        ["clean"],
      ],
    }),
    []
  );

  // Acciones
  const handleSave = () => {
    const doc = { title, html: value, updatedAt: new Date().toISOString() };
    localStorage.setItem("textlab_doc_demo", JSON.stringify(doc));
    alert("Documento guardado localmente (demo).");
  };

  const handleAI = () => {
    // Placeholder: aquí iría tu integración IA (si aplica en la demo).
    alert("Corrección con IA (demo).");
  };

  const handleExport = () => {
    // Exportar a .doc conservando formato (HTML embebido)
    const blob = new Blob(
      [
        `<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>${value}</body></html>`,
      ],
      { type: "application/msword" }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title || "documento"}.doc`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Métricas simples
  const plainText = useMemo(
    () =>
      value
        .replace(/<[^>]+>/g, " ")
        .replace(/\s+/g, " ")
        .trim(),
    [value]
  );
  const words = plainText ? plainText.split(" ").length : 0;
  const readMin = Math.max(1, Math.ceil(words / 200));

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <Toolbar
        onSave={handleSave}
        onExport={handleExport}
        onAI={handleAI}
        isGuest={isGuest}
      />

      {/* Cuerpo */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editor */}
        <div className="flex-1 p-6 overflow-auto">
          {/* Título */}
          <input
            className="w-full border rounded-md px-3 py-2 mb-3"
            placeholder="Título del documento…"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          {/* Editor */}
          <div className="bg-white border rounded-md">
            <ReactQuill
              ref={quillRef}
              theme="snow"
              modules={modules}
              value={value}
              onChange={setValue}
              placeholder="Escribe tu texto aquí…"
            />
          </div>

          {/* Aviso modo invitado */}
          {isGuest && (
            <p className="text-xs text-gray-500 mt-2">
              *Modo invitado sin restricciones activado para la demostración.
            </p>
          )}

          {/* Link como en tu UI anterior (abajo a la izquierda) */}
          <div className="mt-4">
            <Link
              to="/plantillas"
              className="text-sm text-blue-600 hover:underline"
            >
              Ir a plantillas
            </Link>
          </div>
        </div>

        {/* Panel de estadísticas a la derecha (tarjeta blanca) */}
        <StatsPanel words={words} readMinutes={readMin} readability={0} />
      </div>
    </div>
  );
}
