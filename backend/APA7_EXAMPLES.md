# Ejemplos de Uso - Módulo APA7

## Ejemplo 1: Libro

### Input (Parsed Reference)
```json
{
  "authors": ["Smith, J.", "Jones, M."],
  "year": 2020,
  "title": "Introduction to Psychology",
  "publisher": "Academic Press",
  "location": "New York",
  "type": "book"
}
```

### Output (In-text Citation)
```
(Smith & Jones, 2020)
```

### Output (Reference List Entry)
```
Smith, J., & Jones, M. (2020). Introduction to Psychology. New York: Academic Press.
```

### Output con Sangría Francesa (HTML)
```html
<p style="text-indent: -36px; padding-left: 36px;">Smith, J., & Jones, M. (2020). Introduction to Psychology. New York: Academic Press.</p>
```

---

## Ejemplo 2: Artículo de Revista

### Input (Parsed Reference)
```json
{
  "authors": ["Brown, K.", "White, L."],
  "year": 2019,
  "title": "Cognitive Development in Children",
  "source": "Journal of Psychology",
  "volume": "45",
  "issue": "3",
  "pages": "123-145",
  "doi": "10.1234/example",
  "type": "article"
}
```

### Output (In-text Citation)
```
(Brown & White, 2019)
```

### Output (Reference List Entry)
```
Brown, K., & White, L. (2019). Cognitive Development in Children. Journal of Psychology, 45(3), 123-145. https://doi.org/10.1234/example
```

### Output con Sangría Francesa (LaTeX)
```latex
\hangindent=36pt Brown, K., & White, L. (2019). Cognitive Development in Children. Journal of Psychology, 45(3), 123-145. https://doi.org/10.1234/example\\
```

---

## Ejemplo 3: Sitio Web

### Input (Parsed Reference)
```json
{
  "authors": ["Green, P."],
  "year": 2021,
  "title": "Understanding Psychology",
  "site_name": "Psychology Today",
  "url": "https://example.com/article",
  "type": "web"
}
```

### Output (In-text Citation)
```
(Green, 2021)
```

### Output (Reference List Entry)
```
Green, P. (2021). Understanding Psychology. Psychology Today. https://example.com/article
```

### Output con Sangría Francesa (Text)
```
	Green, P. (2021). Understanding Psychology. Psychology Today. https://example.com/article
```

---

## Ejemplo 4: Capítulo de Libro

### Input (Parsed Reference)
```json
{
  "authors": ["Blue, Q."],
  "year": 2018,
  "chapter_title": "Introduction to Cognitive Psychology",
  "editors": ["Red, R."],
  "book_title": "Handbook of Psychology",
  "publisher": "Academic Press",
  "pages": "45-67",
  "type": "chapter"
}
```

### Output (In-text Citation)
```
(Blue, 2018)
```

### Output (Reference List Entry)
```
Blue, Q. (2018). Introduction to Cognitive Psychology. In Red, R. (Ed.), Handbook of Psychology (pp. 45-67). Academic Press.
```

---

## Ejemplo de Parsing de Texto Libre

### Input (Raw Text)
```
Smith, J., & Jones, M. (2020). Introduction to Psychology. American Journal of Psychology, 45(3), 123-145. https://doi.org/10.1234/example
```

### Output (Parsed)
```json
{
  "authors": ["Smith, J.", "Jones, M."],
  "year": 2020,
  "title": "Introduction to Psychology",
  "source": "American Journal of Psychology",
  "type": "article",
  "doi": "10.1234/example",
  "volume": "45",
  "issue": "3",
  "pages": "123-145"
}
```

---

## Ejemplo de Validación de Coherencia

### Input (Citations y References)
```python
citations = [
    {
        "citation_key": "[Smith, 2020]",
        "citation_text": "Smith (2020) states...",
        "parsed": {
            "authors": ["Smith, J."],
            "year": 2020
        }
    },
    {
        "citation_key": "[Jones, 2019]",
        "citation_text": "Jones (2019) found...",
        "parsed": {
            "authors": ["Jones, M."],
            "year": 2019
        }
    }
]

references = [
    {
        "ref_key": "[Smith, 2020]",
        "ref_text": "Smith, J. (2020). Example book.",
        "parsed": {
            "authors": ["Smith, J."],
            "year": 2020
        }
    }
]
```

### Output (Validation Result)
```json
{
  "citations_without_reference": [
    {
      "citation_key": "[Jones, 2019]",
      "citation_text": "Jones (2019) found...",
      "issue": "No matching reference found"
    }
  ],
  "references_without_citations": [],
  "imperfect_matches": []
}
```

---

## Uso de Endpoints

### 1. Generar Lista de Referencias

```bash
POST /api/v1/documents/{id}/apa/generate-references
Content-Type: application/json

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

### 2. Validar Coherencia

```bash
GET /api/v1/documents/{id}/apa/validate
```

**Response:**
```json
{
  "citations_without_reference": [],
  "references_without_citations": [
    {
      "ref_key": "[Jones, 2019]",
      "ref_text": "Jones, M. (2019). Example book.",
      "issue": "No matching citation found"
    }
  ],
  "imperfect_matches": []
}
```

### 3. Parsear Referencia

```bash
POST /api/v1/documents/apa/parse-reference
Content-Type: application/json

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

---

## Integración con Base de Datos

### Almacenar Referencia Parseada

```python
from app.models.reference import Reference
from app.services.apa_service import apa7_service

# Parsear texto
raw_text = "Smith, J. (2020). Introduction to Psychology. Academic Press."
parsed = apa7_service.parse_reference_text(raw_text)

# Crear referencia en DB
reference = Reference(
    document_id=document.id,
    ref_key="[Smith, 2020]",
    ref_text=raw_text,
    parsed=parsed  # Almacenar como JSONB
)
db.add(reference)
db.commit()
```

### Almacenar Cita Parseada

```python
from app.models.citation import Citation

# Generar cita
parsed_ref = {
    "authors": ["Smith, J."],
    "year": 2020
}
citation_text = apa7_service.generate_citation(parsed_ref)

# Crear cita en DB
citation = Citation(
    document_id=document.id,
    citation_key="[Smith, 2020]",
    citation_text=citation_text,
    parsed=parsed_ref  # Almacenar como JSONB
)
db.add(citation)
db.commit()
```

---

## Formatos de Salida

### Text (con tabulación)
```
	Smith, J. (2020). Introduction to Psychology. Academic Press.
```

### HTML (con CSS)
```html
<p style="text-indent: -36px; padding-left: 36px;">
  Smith, J. (2020). Introduction to Psychology. Academic Press.
</p>
```

### LaTeX (con comando)
```latex
\hangindent=36pt Smith, J. (2020). Introduction to Psychology. Academic Press.\\
```

