# Servicio de Exportación - TextLab

## Descripción

Servicio completo para exportar documentos a PDF y DOCX con formato académico, plantillas institucionales y cumplimiento APA 7.

## Funcionalidades

1. **Exportación a PDF**: Usando ReportLab
2. **Exportación a DOCX**: Usando python-docx
3. **Formato APA 7**: Referencias con sangría francesa, interlineado doble
4. **Plantillas Institucionales**: Headers con logo, fuentes personalizadas
5. **Estadísticas**: Conteo de palabras, métricas de legibilidad (textstat)
6. **Exportación Asíncrona**: Via Celery workers

## Endpoints

### POST `/api/v1/documents/{id}/export`

Crea un trabajo de exportación asíncrono.

**Request:**
```json
{
  "format": "pdf",
  "include_stats": true,
  "template_id": "institutional_template_1"
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "document_id": "123e4567-e89b-12d3-a456-426614174001",
  "status": "queued",
  "message": "Export job queued successfully"
}
```

### GET `/api/v1/export_jobs/{job_id}`

Obtiene el estado de un trabajo de exportación.

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "document_id": "123e4567-e89b-12d3-a456-426614174001",
  "user_id": "123e4567-e89b-12d3-a456-426614174002",
  "status": "done",
  "result_path": "document_xxx_20240101_120000.pdf",
  "created_at": "2024-01-01T12:00:00Z",
  "finished_at": "2024-01-01T12:01:00Z"
}
```

### GET `/api/v1/downloads/{filename}`

Descarga el archivo exportado.

**Response:**
- Archivo PDF o DOCX
- Headers apropiados para descarga
- Control de acceso (solo owner o admin)

## Formato APA 7

### Referencias con Sangría Francesa

**DOCX:**
- `first_line_indent = -0.5 inches` (-18pt)
- `left_indent = 0.5 inches` (36pt)
- Interlineado doble

**PDF:**
- `leftIndent = 36pt`
- `firstLineIndent = -18pt`
- Interlineado doble (leading = 24pt para fuente 12pt)

### Ejemplo Visual

```
    Smith, J. (2020). Introduction to Psychology. Academic Press.
    Jones, M., & Brown, K. (2019). Advanced Research Methods. 
        Journal of Psychology, 45(3), 123-145.
```

## Opciones de Exportación

- **format**: `"pdf"` o `"docx"`
- **include_stats**: Incluir estadísticas del documento
- **template_id**: ID de plantilla institucional a usar

## Estadísticas Incluidas

Cuando `include_stats: true`:
- Word Count (conteo de palabras)
- Character Count (conteo de caracteres)
- Paragraph Count (conteo de párrafos)
- Flesch Reading Ease (si textstat disponible)
- Flesch-Kincaid Grade Level
- Automated Readability Index

## Tarea Celery

### `export_document(job_id)`

Ejecuta la exportación en background:

1. Recupera el trabajo de exportación
2. Obtiene documento y referencias
3. Genera archivo (PDF o DOCX)
4. Guarda en almacenamiento local
5. Actualiza estado del trabajo

## Almacenamiento

Por defecto, los archivos se guardan en:
- Directorio: `exports/`
- Nombre: `document_{document_id}_{timestamp}.{format}`

## Control de Acceso

- Solo el propietario del documento o admin puede exportar
- Solo el propietario del trabajo o admin puede descargar
- Validación de nombres de archivo (previene path traversal)

## Tests

Ejecutar tests:

```bash
pytest tests/test_export.py -v
```

Los tests cubren:
- Creación de trabajos de exportación
- Validación de formatos
- Control de acceso
- Generación de archivos (si librerías disponibles)

## Dependencias

- `python-docx`: Para generación de DOCX
- `reportlab`: Para generación de PDF
- `textstat`: Para métricas de legibilidad
- `Pillow`: Para procesamiento de imágenes (logos)

## Ejemplo de Uso

```bash
# 1. Crear trabajo de exportación
curl -X POST "http://localhost:8000/api/v1/documents/{id}/export" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "include_stats": true
  }'

# 2. Consultar estado
curl -X GET "http://localhost:8000/api/v1/export_jobs/{job_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Descargar archivo (cuando status = "done")
curl -X GET "http://localhost:8000/api/v1/downloads/{filename}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o document.pdf
```

## Notas Técnicas

### Sangría Francesa en DOCX

```python
para_format.first_line_indent = Inches(-0.5)  # -18pt
para_format.left_indent = Inches(0.5)  # 36pt
para_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
```

### Sangría Francesa en PDF

```python
ref_style = ParagraphStyle(
    'Reference',
    leftIndent=36,      # 36pt left indent
    firstLineIndent=-18,  # -18pt first line (hanging)
    leading=24,         # Double spacing
)
```

El servicio de exportación está completo y listo para usar.

