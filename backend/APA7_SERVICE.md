# Servicio APA 7 - TextLab

## Descripción

Módulo completo para generación y validación de citas y referencias según el estilo APA 7th edition.

## Funcionalidades

1. **Generación de Citas In-text**: Formatea citas para uso dentro del texto
2. **Generación de Referencias**: Crea entradas de bibliografía con sangría francesa
3. **Parsing de Referencias**: Extrae componentes de texto libre de referencias
4. **Validación de Coherencia**: Compara citas y referencias para detectar inconsistencias

## Tipos de Fuentes Soportados

- **Libro (book)**: Libros completos
- **Artículo (article)**: Artículos de revista académica
- **Web (web/website)**: Sitios web y páginas online
- **Capítulo (chapter)**: Capítulos de libros editados

## Endpoints

### POST `/api/v1/documents/{id}/apa/generate-references`

Genera una lista completa de referencias formateadas.

**Request:**
```json
{
  "references": [
    {
      "authors": ["Smith, J."],
      "year": 2020,
      "title": "Introduction to Psychology",
      "type": "book"
    }
  ],
  "format": "text"
}
```

**Response:**
```json
{
  "reference_list": "\tSmith, J. (2020). Introduction to Psychology.",
  "format": "text"
}
```

### GET `/api/v1/documents/{id}/apa/validate`

Valida coherencia entre citas y referencias.

**Response:**
```json
{
  "citations_without_reference": [],
  "references_without_citations": [],
  "imperfect_matches": []
}
```

### POST `/api/v1/documents/apa/parse-reference`

Parsea texto libre de referencia en componentes estructurados.

**Request:**
```json
{
  "raw_text": "Smith, J. (2020). Introduction to Psychology. Academic Press."
}
```

**Response:**
```json
{
  "parsed": {
    "authors": ["Smith, J."],
    "year": 2020,
    "title": "Introduction to Psychology",
    "publisher": "Academic Press",
    "type": "book"
  }
}
```

## Uso del Servicio

### Generar Cita

```python
from app.services.apa_service import apa7_service

parsed_ref = {
    "authors": ["Smith, J.", "Jones, M."],
    "year": 2020
}
citation = apa7_service.generate_citation(parsed_ref)
# Resultado: "(Smith & Jones, 2020)"
```

### Generar Referencia

```python
parsed_ref = {
    "authors": ["Smith, J."],
    "year": 2020,
    "title": "Introduction to Psychology",
    "publisher": "Academic Press",
    "type": "book"
}
reference = apa7_service.generate_reference(parsed_ref)
# Resultado: "Smith, J. (2020). Introduction to Psychology. Academic Press."
```

### Parsear Texto

```python
raw_text = "Smith, J. (2020). Introduction to Psychology. Academic Press."
parsed = apa7_service.parse_reference_text(raw_text)
# Resultado: dict con authors, year, title, etc.
```

### Validar Coherencia

```python
citations = [...]  # Lista de citas
references = [...]  # Lista de referencias
validation = apa7_service.validate_coherence(citations, references)
# Resultado: dict con inconsistencias encontradas
```

## Tarea Celery

### `validate_apa_coherence`

Ejecuta validación de coherencia en background.

```python
from app.tasks.apa_tasks import validate_apa_coherence

task = validate_apa_coherence.delay(document_id)
result = task.get()
```

## Formatos de Salida

- **text**: Texto plano con tabulación para sangría francesa
- **html**: HTML con CSS para sangría francesa
- **latex**: LaTeX con comando `\hangindent`

## Reglas APA 7 Implementadas

### Citas In-text

- 1 autor: `(Smith, 2020)`
- 2 autores: `(Smith & Jones, 2020)`
- 3-5 autores: `(Smith, Jones, & Brown, 2020)`
- 6+ autores: `(Smith et al., 2020)`
- Sin año: `(Smith, n.d.)`

### Referencias

- Formato básico: `Author, A. A. (Year). Title. Source.`
- Sangría francesa para todas las entradas
- DOI incluido cuando está disponible
- URLs para recursos web

## Tests

Ejecutar tests:

```bash
pytest tests/test_apa_service.py -v
```

Los tests cubren:
- Generación de citas (1, 2, múltiples autores)
- Generación de referencias (libro, artículo, web, capítulo)
- Parsing de texto libre
- Validación de coherencia
- Formatos de salida (text, HTML, LaTeX)

## Integración con Base de Datos

Los campos `parsed` en las tablas `citations` y `references` almacenan los datos parseados como JSONB:

```python
# Almacenar referencia parseada
reference.parsed = {
    "authors": ["Smith, J."],
    "year": 2020,
    "title": "Introduction to Psychology",
    "type": "book"
}
```

Esto permite:
- Regenerar citas y referencias cuando sea necesario
- Validar coherencia entre citas y referencias
- Actualizar formato si cambian las reglas APA

