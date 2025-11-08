export default function StatsPanel({ words = 0, readMinutes = 1, readability = 0 }) {
  return (
    <aside className="w-full md:w-80 p-4 border-l bg-gray-50/50">
      <div className="bg-white border rounded-lg p-4">
        <h3 className="font-semibold mb-2">Estadísticas del documento</h3>

        <div className="text-sm space-y-1">
          <div>
            <span className="font-medium">Palabras totales:</span> {words}
          </div>
          <div>
            <span className="font-medium">Tiempo estimado de lectura:</span> {readMinutes} min
          </div>
          <div>
            <span className="font-medium">Legibilidad:</span> {readability}%
          </div>
        </div>

        <p className="text-xs text-gray-500 mt-3">
          Estas métricas son estimaciones informativas.
        </p>
      </div>
    </aside>
  );
}
