// src/components/ProtectedRoute.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";

/**
 * DEMO_INVITADO:
 *  - true  → permite pasar al editor sin token (para demostración).
 *  - false → exige autenticación normal (comportamiento original).
 */
const DEMO_INVITADO = true;

export default function ProtectedRoute({ children }) {
  const location = useLocation();

  if (DEMO_INVITADO) {
    // Permitir todo durante la demo (invitado sin restricciones)
    return children;
  }

  // Autenticación normal (tu lógica de token/localStorage, etc.)
  const token = localStorage.getItem("token");
  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

