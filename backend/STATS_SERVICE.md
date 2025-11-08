# Servicio de Estadísticas - TextLab

## Descripción

Servicio completo para calcular y almacenar métricas de documentos, incluyendo conteos básicos, tiempo de lectura y métricas de legibilidad.

## Métricas Calculadas

### Básicas
- **word_count**: Número de palabras
- **character_count**: Número de caracteres (con espacios)
- **character_count_no_spaces**: Número de caracteres (sin espacios)
- **paragraph_count**: Número de párrafos
- **sentence_count**: Número de oraciones

### Tiempo de Lectura
- **reading_time_minutes**: Tiempo estimado en minutos (200 wpm)
- **reading_time_seconds**: Tiempo estimado en segundos
- **reading_time_display**: Formato legible (ej: "5 minutes")

### Promedios
- **average_words_per_sentence**: Promedio de palabras por oración
- **average_sentences_per_paragraph**: Promedio de oraciones por párrafo

### Legibilidad (textstat)
- **flesch_reading_ease**: Índice de facilidad de lectura (0-100)
- **flesch_kincaid_grade**: Nivel de grado escolar
- **automated_readability_index**: Índice de legibilidad automatizado
- **coleman_liau_index**: Índice Coleman-Liau
- **dale_chall_readability_score**: Puntuación Dale-Chall

## Endpoints

### POST `/api/v1/documents/{id}/stats`

Calcula estadísticas de un documento (síncrono).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (202 Accepted):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "document_id": "123e4567-e89b-12d3-a456-426614174001",
  "stats": {
    "word_count": 1500,
    "character_count": 8500,
    "paragraph_count": 10,
    "reading_time_minutes": 7.5,
    "reading_time_display": "7 minutes",
    "flesch_reading_ease": 65.5,
    "flesch_kincaid_grade": 8.2
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET `/api/v1/documents/{id}/stats`

Obtiene las últimas estadísticas de un documento.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "document_id": "123e4567-e89b-12d3-a456-426614174001",
  "stats": {
    "word_count": 1500,
    "character_count": 8500,
    "reading_time_minutes": 7.5
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET `/api/v1/stats/overview`

Panel de estadísticas globales (solo admin/teacher).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, default: 1): Número de página
- `per_page` (int, default: 10, max: 100): Elementos por página

**Response (200 OK):**
```json
{
  "total_documents": 100,
  "total_users": 25,
  "average_words_per_document": 1250.5,
  "total_words": 125050,
  "documents_by_user": [
    {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_email": "user@example.com",
      "document_count": 10,
      "total_words": 15000
    }
  ],
  "recent_activity": {
    "documents_created_last_7_days": 15,
    "documents_created_last_30_days": 50
  }
}
```

## Uso del Servicio

### Calcular Estadísticas

```python
from app.services.stats_service import stats_service

content = "Your document content here..."
stats = stats_service.calculate_stats(content)

print(f"Word count: {stats['word_count']}")
print(f"Reading time: {stats['reading_time_display']}")
print(f"Flesch Reading Ease: {stats['flesch_reading_ease']}")
```

### Tarea Celery (Opcional)

```python
from app.tasks.stats_tasks import calculate_document_stats

# Enqueue task
task = calculate_document_stats.delay(document_id)

# Check result
result = task.get()
```

## Tiempo de Lectura

El tiempo de lectura se calcula usando **200 palabras por minuto** (wpm), que es la velocidad promedio de lectura.

- 200 palabras = 1 minuto
- 1000 palabras = 5 minutos
- 5000 palabras = 25 minutos

## Métricas de Legibilidad

### Flesch Reading Ease
- **90-100**: Muy fácil (5to grado)
- **80-89**: Fácil (6to grado)
- **70-79**: Bastante fácil (7mo grado)
- **60-69**: Estándar (8vo-9no grado)
- **50-59**: Bastante difícil (10mo-12mo grado)
- **30-49**: Difícil (Universidad)
- **0-29**: Muy difícil (Postgrado)

### Flesch-Kincaid Grade Level
Indica el nivel de grado escolar necesario para entender el texto.

## Almacenamiento

Las estadísticas se guardan en la tabla `document_stats` con:
- `document_id`: ID del documento
- `stats`: JSONB con todas las métricas
- `created_at`: Timestamp de cuando se calcularon

Esto permite:
- Historial de estadísticas (si el documento cambia)
- Consultas rápidas sin recalcular
- Análisis de tendencias

## Ejemplo de Uso

```bash
# 1. Calcular estadísticas
curl -X POST "http://localhost:8000/api/v1/documents/{id}/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Consultar estadísticas
curl -X GET "http://localhost:8000/api/v1/documents/{id}/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Ver overview (admin/teacher)
curl -X GET "http://localhost:8000/api/v1/stats/overview?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Tests

Ejecutar tests:

```bash
pytest tests/test_stats.py -v
```

Los tests cubren:
- Cálculo de estadísticas básicas
- Tiempo de lectura
- Métricas de legibilidad
- Endpoints de API
- Panel de overview
- Control de acceso

## Notas

- El cálculo es rápido, por lo que se hace síncronamente
- Las estadísticas se guardan con timestamp para historial
- El panel de overview está paginado para mejor rendimiento
- Solo admin y teacher pueden ver el overview

