# Servicio de Corrección de Texto - TextLab

## Descripción

Servicio asíncrono de análisis de texto que detecta errores de ortografía, gramática y estilo. Utiliza LanguageTool y reglas de estilo personalizadas.

## Arquitectura

- **Servicio NLP**: `app/services/nlp_service.py` - Análisis de texto
- **Tarea Celery**: `app/tasks/nlp_tasks.py` - Ejecución asíncrona
- **Modelo**: `DocumentAnalysis` - Almacenamiento de resultados
- **Endpoints**: FastAPI para iniciar y consultar análisis

## Endpoints

### 1. Iniciar Análisis
**POST** `/api/v1/documents/{id}/analyze`

Inicia un análisis asíncrono del documento. Retorna inmediatamente con un job ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (202 Accepted):**
```json
{
  "job_id": "abc123-def456-ghi789",
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "message": "Analysis task queued successfully"
}
```

**Errores:**
- `400 Bad Request`: ID de documento inválido
- `403 Forbidden`: Sin permisos o no autenticado
- `404 Not Found`: Documento no encontrado

### 2. Obtener Análisis
**GET** `/api/v1/documents/{id}/analysis`

Obtiene el último análisis realizado del documento.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "suggestions": [
    {
      "start": 10,
      "end": 20,
      "error_type": "SPELLING",
      "suggestion": "tecnología",
      "rule_id": "SPELLING_RULE_1",
      "confidence": 0.9
    },
    {
      "start": 50,
      "end": 60,
      "error_type": "STYLE",
      "suggestion": "Consider breaking this long sentence into shorter ones.",
      "rule_id": "LONG_SENTENCE",
      "confidence": 0.7
    }
  ],
  "stats": {
    "total_suggestions": 2,
    "spelling_errors": 1,
    "grammar_errors": 0,
    "style_issues": 1
  },
  "text_length": 150,
  "text_hash": "abc123...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Errores:**
- `400 Bad Request`: ID de documento inválido
- `403 Forbidden`: Sin permisos o no autenticado
- `404 Not Found`: Documento o análisis no encontrado

## Tipos de Errores

### SPELLING
Errores de ortografía detectados por LanguageTool.

### GRAMMAR
Errores gramaticales detectados por LanguageTool.

### STYLE
Problemas de estilo detectados por reglas personalizadas:
- **LONG_SENTENCE**: Oraciones muy largas (>150 caracteres)
- **PASSIVE_VOICE**: Uso de voz pasiva (detección básica)

## Caché de Análisis

El servicio implementa caché basado en hash del texto:

- Cada análisis calcula un hash SHA-256 del texto
- Si el texto no ha cambiado (mismo hash), se reutiliza el análisis existente
- Esto evita re-analizar documentos sin cambios

## Uso del Servicio

### Análisis Síncrono (en proceso)

```python
from app.services.nlp_service import nlp_service

text = "Este es un texto con errores de ortografia."
suggestions = nlp_service.analyze_text(text)

for suggestion in suggestions:
    print(f"Error en posición {suggestion['start']}-{suggestion['end']}: {suggestion['suggestion']}")
```

### Análisis Asíncrono (Celery)

```python
from app.tasks.nlp_tasks import analyze_document_text

# Enqueue task
task = analyze_document_text.delay(document_id)

# Check status
result = task.get()  # Wait for result
```

## Configuración

### LanguageTool

El servicio intenta usar LanguageTool si está disponible:

```bash
pip install language-tool-python
```

Si LanguageTool no está disponible, el servicio usa análisis mock para testing.

### Idiomas Soportados

Por defecto: `es-ES` (Español de España)

Otros idiomas disponibles:
- `en-US` (Inglés)
- `pt-BR` (Portugués de Brasil)
- Y otros según LanguageTool

## Ejemplo de Uso Completo

```bash
# 1. Crear documento
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Documento",
    "content": "Este es un texto con algunos errores de ortografia y gramatica."
  }'

# 2. Iniciar análisis
curl -X POST "http://localhost:8000/api/v1/documents/DOCUMENT_ID/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Consultar resultados (después de que Celery complete)
curl -X GET "http://localhost:8000/api/v1/documents/DOCUMENT_ID/analysis" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Estructura de Sugerencias

Cada sugerencia contiene:

- **start**: Posición inicial del error en el texto
- **end**: Posición final del error
- **error_type**: Tipo de error (SPELLING, GRAMMAR, STYLE)
- **suggestion**: Sugerencia de corrección
- **rule_id**: ID de la regla que detectó el error
- **confidence**: Nivel de confianza (0.0 - 1.0)

## Tests

Ejecutar tests del servicio NLP:

```bash
pytest tests/test_nlp_service.py -v
pytest tests/test_document_analysis.py -v
```

Los tests incluyen:
- Análisis de texto básico
- Detección de errores
- Análisis de estilo
- Caché de análisis
- Endpoints de API

## Notas

- El análisis se ejecuta en background (no bloquea la request)
- Los resultados se guardan en la base de datos
- El servicio funciona sin LanguageTool (usa mock para testing)
- El caché evita re-analizar texto sin cambios

