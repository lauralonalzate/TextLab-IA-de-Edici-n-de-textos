import React from "react";

const Btn = ({ title, onClick, children }) => (
  <button
    type="button"
    title={title}
    onClick={onClick}
    className="px-2 py-1 rounded hover:bg-gray-100 border border-gray-200"
  >
    {children}
  </button>
);

// Ejecuta comandos nativos de formato sobre el contentEditable
const exec = (cmd, value = null) => document.execCommand(cmd, false, value);

export default function EditorToolbar({ onInsertImage, onCreateLink, onClear }) {
  return (
    <div className="flex flex-wrap gap-2 items-center p-2 bg-white border border-gray-200 rounded">
      {/* Estilo de párrafo / headings */}
      <select
        className="border rounded px-2 py-1"
        defaultValue="P"
        onChange={(e) => exec("formatBlock", e.target.value)}
        title="Estilo"
      >
        <option value="P">Normal</option>
        <option value="H1">H1</option>
        <option value="H2">H2</option>
        <option value="H3">H3</option>
        <option value="H4">H4</option>
      </select>

      <Btn title="Negrita" onClick={() => exec("bold")}><b>B</b></Btn>
      <Btn title="Cursiva" onClick={() => exec("italic")}><i>I</i></Btn>
      <Btn title="Subrayado" onClick={() => exec("underline")}><u>U</u></Btn>
      <Btn title="Tachado" onClick={() => exec("strikeThrough")}><s>S</s></Btn>

      <span className="w-px h-6 bg-gray-200 mx-1" />

      <Btn title="Lista con viñetas" onClick={() => exec("insertUnorderedList")}>• Lista</Btn>
      <Btn title="Lista numerada" onClick={() => exec("insertOrderedList")}>1. Lista</Btn>

      <span className="w-px h-6 bg-gray-200 mx-1" />

      <Btn title="Alinear izquierda" onClick={() => exec("justifyLeft")}>⟸</Btn>
      <Btn title="Centrar" onClick={() => exec("justifyCenter")}>⇔</Btn>
      <Btn title="Alinear derecha" onClick={() => exec("justifyRight")}>⟹</Btn>
      <Btn title="Justificar" onClick={() => exec("justifyFull")}>≋</Btn>

      <span className="w-px h-6 bg-gray-200 mx-1" />

      <Btn title="Color texto" onClick={() => {
        const c = window.prompt("Color (hex, nombre CSS o rgb):", "#111827");
        if (c) exec("foreColor", c);
      }}>A🎨</Btn>

      <Btn title="Enlace" onClick={onCreateLink}>🔗</Btn>
      <Btn title="Imagen" onClick={onInsertImage}>🖼️</Btn>

      <span className="w-px h-6 bg-gray-200 mx-1" />

      <Btn title="Deshacer" onClick={() => exec("undo")}>↶</Btn>
      <Btn title="Rehacer" onClick={() => exec("redo")}>↷</Btn>

      <Btn title="Limpiar formato" onClick={onClear}>🧹</Btn>
    </div>
  );
}
