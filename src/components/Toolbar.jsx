import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Toolbar({ onSave, onExport, onAI, isGuest }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Modo invitado: sólo limpiar flag y volver a /login
    localStorage.removeItem("guest");
    // Si usas autenticación real: localStorage.removeItem("token");
    navigate("/login", { replace: true });
  };

  return (
    <div className="flex items-center justify-between px-6 py-4 border-b bg-white">
      {/* Marca + botón Plantillas */}
      <div className="flex items-center gap-3">
        <div className="text-2xl font-semibold text-blue-700">TextLab</div>
        <Link
          to="/plantillas"
          className="text-sm font-medium text-blue-600 hover:underline"
          title="Ver plantillas"
        >
          Plantillas
        </Link>
      </div>

      {/* Acciones */}
      <div className="flex items-center gap-2">
        <button
          onClick={onSave}
          className="px-4 py-2 rounded-md text-sm font-medium bg-white border hover:bg-gray-50"
        >
          Guardar
        </button>

        <button
          onClick={onAI}
          className="px-4 py-2 rounded-md text-sm font-medium bg-blue-600 text-white hover:bg-blue-700"
        >
          Corregir con IA
        </button>

        <button
          onClick={onExport}
          className="px-4 py-2 rounded-md text-sm font-medium bg-white border hover:bg-gray-50"
        >
          Exportar
        </button>

        <button
          onClick={handleLogout}
          className="px-4 py-2 rounded-md text-sm font-medium bg-red-600 text-white hover:bg-red-700"
          title={isGuest ? "Cerrar sesión (modo invitado)" : "Cerrar sesión"}
        >
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}
