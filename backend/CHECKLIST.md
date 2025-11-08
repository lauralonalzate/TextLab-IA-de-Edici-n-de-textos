# TextLab Backend - Pre-Deployment Checklist

Esta checklist debe completarse antes de marcar el proyecto como listo para producción.

## 📋 Índice

- [Endpoints y Funcionalidad](#endpoints-y-funcionalidad)
- [Tests Automatizados](#tests-automatizados)
- [Pruebas Manuales](#pruebas-manuales)
- [Revisión de Seguridad](#revisión-de-seguridad)
- [Documentación](#documentación)
- [Entregables Finales](#entregables-finales)
- [Comandos de Verificación](#comandos-de-verificación)

---

## Endpoints y Funcionalidad

### ✅ Autenticación

- [x] **POST /api/v1/auth/register** - Registro de usuario
- [x] **POST /api/v1/auth/login** - Login con rate limiting
- [x] **POST /api/v1/auth/refresh** - Refresh token
- [x] **GET /api/v1/users/me** - Obtener usuario actual

**Criterios de Aceptación:**
- Registro crea usuario con hash de contraseña
- Login devuelve access_token y refresh_token
- Rate limiting funciona en login (5 req/min)
- Token JWT válido y con expiración correcta
- Refresh token renueva access token

### ✅ Documentos CRUD

- [x] **POST /api/v1/documents** - Crear documento
- [x] **GET /api/v1/documents** - Listar documentos (paginación)
- [x] **GET /api/v1/documents/{id}** - Obtener documento
- [x] **PUT /api/v1/documents/{id}** - Actualizar documento (crea versión)
- [x] **DELETE /api/v1/documents/{id}** - Eliminar documento
- [x] **POST /api/v1/documents/{id}/share** - Compartir documento

**Criterios de Aceptación:**
- Solo owner/admin puede editar/eliminar
- Paginación funciona correctamente
- Versión se crea al actualizar
- Búsqueda por título funciona
- Permisos de acceso respetados

### ✅ Análisis NLP

- [x] **POST /api/v1/documents/{id}/analyze** - Iniciar análisis
- [x] **GET /api/v1/documents/{id}/analysis** - Obtener resultados

**Criterios de Aceptación:**
- Análisis se ejecuta en background (Celery)
- Resultados se guardan en `document_analysis`
- Hash de texto evita re-análisis innecesario
- Sugerencias incluyen: start, end, error_type, suggestion

### ✅ APA 7

- [x] **POST /api/v1/documents/{id}/apa/generate-references** - Generar bibliografía
- [x] **GET /api/v1/documents/{id}/apa/validate** - Validar coherencia
- [x] **POST /api/v1/documents/apa/parse-reference** - Parsear referencia

**Criterios de Aceptación:**
- Referencias con sangría francesa (hanging indent)
- Soporta: book, article, web, chapter
- Validación detecta citas sin referencias
- Parseo extrae: authors, year, title, type, doi

### ✅ Exportación

- [x] **POST /api/v1/documents/{id}/export** - Crear job de exportación
- [x] **GET /api/v1/export_jobs/{job_id}** - Estado del job
- [x] **GET /api/v1/downloads/{filename}** - Descargar archivo

**Criterios de Aceptación:**
- Export a PDF y DOCX funciona
- Job asíncrono (Celery)
- Archivo se genera con formato APA 7
- Hanging indent en referencias
- Solo owner/admin puede descargar

### ✅ Estadísticas

- [x] **POST /api/v1/documents/{id}/stats** - Calcular estadísticas
- [x] **GET /api/v1/documents/{id}/stats** - Obtener estadísticas
- [x] **GET /api/v1/stats/overview** - Vista global (admin/teacher)

**Criterios de Aceptación:**
- Calcula: word_count, reading_time, flesch_reading_ease
- Guarda en `document_stats`
- Overview solo para admin/teacher
- Tiempo de lectura: 200 wpm

### ✅ Administración

- [x] **GET /api/v1/admin/stats** - Estadísticas admin
- [x] **GET /api/v1/admin/audit_logs** - Logs de auditoría

**Criterios de Aceptación:**
- Solo admin puede acceder
- Paginación funciona
- Filtros: user, action
- Logs contienen: user_id, action, ip, user_agent

---

## Tests Automatizados

### ✅ Ejecutar Suite de Tests

```bash
# Todos los tests
pytest -v

# Con coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Tests específicos
pytest tests/test_auth.py -v
pytest tests/test_documents_crud.py -v
pytest tests/test_nlp_service.py -v
pytest tests/test_apa_service.py -v
pytest tests/test_export.py -v
pytest tests/test_stats.py -v
pytest tests/test_audit.py -v
```

**Criterios de Aceptación:**
- [x] Todos los tests pasan (pytest exit code 0)
- [x] Coverage mínimo: >70% (recomendado)
- [x] No hay tests marcados como skip
- [x] Tests de integración pasan con Docker Compose

### ✅ Tests por Módulo

- [x] **Auth Tests** - Registro, login, refresh, permisos
- [x] **Document CRUD Tests** - Crear, leer, actualizar, eliminar
- [x] **NLP Service Tests** - Análisis con mocks
- [x] **APA Service Tests** - Generación de citas y referencias
- [x] **Export Tests** - Generación de PDF/DOCX
- [x] **Stats Tests** - Cálculo de métricas
- [x] **Audit Tests** - Logging de acciones

---

## Pruebas Manuales

### ✅ Setup Inicial

```bash
# 1. Iniciar servicios
docker-compose up -d

# 2. Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# 3. Verificar servicios
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

### ✅ Flujo Completo de Usuario

#### 1. Registro y Login

```bash
# Variables
API_URL="http://localhost:8000/api/v1"
EMAIL="test@example.com"
PASSWORD="TestPassword123!"

# Registro
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"full_name\": \"Test User\",
    \"password\": \"$PASSWORD\",
    \"role\": \"student\"
  }"

# Login
RESPONSE=$(curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

TOKEN=$(echo $RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"
```

**Verificar:**
- [x] Registro devuelve user data y token
- [x] Login devuelve access_token y refresh_token
- [x] Token es válido y no contiene password

#### 2. Crear y Gestionar Documento

```bash
# Crear documento
DOC_RESPONSE=$(curl -X POST "$API_URL/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Document",
    "content": "# Introduction\n\nThis is a test document.",
    "metadata": {"language": "en"},
    "is_public": false
  }')

DOC_ID=$(echo $DOC_RESPONSE | jq -r '.id')
echo "Document ID: $DOC_ID"

# Listar documentos
curl -X GET "$API_URL/documents?page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"

# Obtener documento
curl -X GET "$API_URL/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN"

# Actualizar documento
curl -X PUT "$API_URL/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Document",
    "content": "# Updated Content\n\nNew content here."
  }'
```

**Verificar:**
- [x] Documento se crea correctamente
- [x] Lista muestra el documento
- [x] Actualización crea versión
- [x] Solo owner puede editar

#### 3. Análisis NLP

```bash
# Iniciar análisis
ANALYZE_RESPONSE=$(curl -X POST "$API_URL/documents/$DOC_ID/analyze" \
  -H "Authorization: Bearer $TOKEN")

JOB_ID=$(echo $ANALYZE_RESPONSE | jq -r '.job_id')
echo "Analysis Job ID: $JOB_ID"

# Esperar unos segundos y obtener resultados
sleep 5
curl -X GET "$API_URL/documents/$DOC_ID/analysis" \
  -H "Authorization: Bearer $TOKEN"
```

**Verificar:**
- [x] Job se crea y devuelve job_id
- [x] Resultados contienen sugerencias
- [x] Hash evita re-análisis del mismo texto

#### 4. Generar Referencias APA

```bash
# Generar referencias
curl -X POST "$API_URL/documents/$DOC_ID/apa/generate-references" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "references": [
      {
        "authors": ["Doe, J."],
        "year": 2023,
        "title": "Test Article",
        "type": "article",
        "source": "Test Journal",
        "volume": "10",
        "issue": "2",
        "pages": "45-60"
      }
    ],
    "format": "text"
  }"

# Validar coherencia
curl -X GET "$API_URL/documents/$DOC_ID/apa/validate" \
  -H "Authorization: Bearer $TOKEN"
```

**Verificar:**
- [x] Referencias generadas con formato APA 7
- [x] Hanging indent presente
- [x] Validación detecta discrepancias

#### 5. Exportar Documento

```bash
# Crear export job
EXPORT_RESPONSE=$(curl -X POST "$API_URL/documents/$DOC_ID/export" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "include_stats": true,
    "template_id": "default"
  }')

EXPORT_JOB_ID=$(echo $EXPORT_RESPONSE | jq -r '.job_id')
echo "Export Job ID: $EXPORT_JOB_ID"

# Verificar estado
sleep 10
curl -X GET "$API_URL/export_jobs/$EXPORT_JOB_ID" \
  -H "Authorization: Bearer $TOKEN"

# Descargar (cuando status = "done")
FILENAME="document_${DOC_ID}_*.pdf"
curl -X GET "$API_URL/downloads/$FILENAME" \
  -H "Authorization: Bearer $TOKEN" \
  -o exported_document.pdf
```

**Verificar:**
- [x] Job se crea correctamente
- [x] Archivo PDF/DOCX se genera
- [x] Contiene sección "References"
- [x] Hanging indent en referencias
- [x] Solo owner puede descargar

#### 6. Estadísticas

```bash
# Calcular estadísticas
curl -X POST "$API_URL/documents/$DOC_ID/stats" \
  -H "Authorization: Bearer $TOKEN"

# Obtener estadísticas
curl -X GET "$API_URL/documents/$DOC_ID/stats" \
  -H "Authorization: Bearer $TOKEN"

# Overview (requiere admin)
curl -X GET "$API_URL/stats/overview?page=1&per_page=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Verificar:**
- [x] Estadísticas se calculan correctamente
- [x] Incluye: word_count, reading_time, flesch_reading_ease
- [x] Overview solo para admin/teacher

#### 7. Auditoría (Admin)

```bash
# Obtener logs de auditoría
curl -X GET "$API_URL/admin/audit_logs?page=1&per_page=10&action=login" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Verificar:**
- [x] Logs contienen acciones realizadas
- [x] Filtros funcionan (user, action)
- [x] Paginación funciona
- [x] Solo admin puede acceder

---

## Revisión de Seguridad

### ✅ Linting y Code Quality

```bash
# Black (formato)
black --check app tests

# Isort (imports)
isort --check-only app tests

# Flake8 (linting)
flake8 app tests

# Type checking (opcional)
mypy app --ignore-missing-imports
```

**Criterios de Aceptación:**
- [x] Black no reporta cambios necesarios
- [x] Isort no reporta cambios necesarios
- [x] Flake8 no reporta errores
- [x] No hay warnings críticos

### ✅ Secrets y Variables de Entorno

```bash
# Verificar que .env no está en git
git ls-files | grep -E "\.env$|\.env\."

# Verificar .env.example existe
test -f .env.example && echo "✓ .env.example exists"

# Verificar .dockerignore excluye .env
grep -q "\.env" .dockerignore && echo "✓ .env in .dockerignore"

# Verificar .gitignore excluye .env
grep -q "\.env" .gitignore && echo "✓ .env in .gitignore"
```

**Criterios de Aceptación:**
- [x] `.env` no está en el repositorio
- [x] `.env.example` contiene todas las variables
- [x] `.dockerignore` excluye `.env`
- [x] `.gitignore` excluye `.env`
- [x] No hay secretos hardcodeados en el código

### ✅ Rate Limiting

```bash
# Probar rate limiting en login
for i in {1..10}; do
  curl -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "wrong"}' \
    -w "\nHTTP Status: %{http_code}\n"
  sleep 1
done
```

**Verificar:**
- [x] Después de 5 requests, devuelve 429 (Too Many Requests)
- [x] Rate limiting funciona con Redis
- [x] Headers de rate limit presentes

### ✅ Autenticación y Autorización

```bash
# Intentar acceder sin token
curl -X GET "$API_URL/documents" \
  -w "\nHTTP Status: %{http_code}\n"

# Intentar acceder con token inválido
curl -X GET "$API_URL/documents" \
  -H "Authorization: Bearer invalid_token" \
  -w "\nHTTP Status: %{http_code}\n"

# Intentar acceder a endpoint admin sin ser admin
curl -X GET "$API_URL/admin/audit_logs" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -w "\nHTTP Status: %{http_code}\n"
```

**Verificar:**
- [x] Endpoints protegidos requieren token
- [x] Token inválido devuelve 401
- [x] Endpoints admin solo para admin (403 si no es admin)

### ✅ Validación de Input

```bash
# Intentar crear documento con datos inválidos
curl -X POST "$API_URL/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "", "content": null}'

# Intentar registro con email inválido
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid-email", "password": "123"}'
```

**Verificar:**
- [x] Validación Pydantic rechaza datos inválidos
- [x] Mensajes de error claros
- [x] Status code 422 para validation errors

### ✅ SQL Injection y Path Traversal

```bash
# Verificar que parámetros están parametrizados (revisar código)
grep -r "execute.*%" app/ || echo "✓ No string formatting in SQL"

# Probar path traversal en downloads
curl -X GET "$API_URL/downloads/../../../etc/passwd" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP Status: %{http_code}\n"
```

**Verificar:**
- [x] SQL usa parámetros (no string formatting)
- [x] Path traversal bloqueado (400 Bad Request)
- [x] Filenames validados

---

## Documentación

### ✅ README.md

**Verificar:**
- [x] Descripción del proyecto
- [x] Instrucciones de instalación
- [x] Comandos para desarrollo
- [x] Ejemplos de uso de API (curl)
- [x] Sección de seguridad
- [x] Variables de entorno documentadas

### ✅ OpenAPI/Swagger

```bash
# Verificar que /docs funciona
curl http://localhost:8000/docs

# Exportar OpenAPI schema
curl http://localhost:8000/openapi.json > openapi.json

# Verificar que tiene ejemplos
jq '.paths."/api/v1/auth/register".post.requestBody.content."application/json".example' openapi.json
```

**Verificar:**
- [x] `/docs` muestra todos los endpoints
- [x] Schemas tienen ejemplos (`json_schema_extra`)
- [x] Descripciones completas
- [x] Respuestas de error documentadas

### ✅ CHANGELOG.md

**Verificar:**
- [x] Todas las features documentadas
- [x] Versión actual indicada
- [x] Formato Keep a Changelog
- [x] Breaking changes documentados

### ✅ DEPLOY.md

**Verificar:**
- [x] Instrucciones para VPS
- [x] Instrucciones para cloud platforms
- [x] Configuración de Kubernetes
- [x] Troubleshooting incluido

---

## Entregables Finales

### ✅ Repositorio

```bash
# Verificar estructura
tree -L 2 -I '__pycache__|*.pyc|.git'

# Verificar que no hay archivos sensibles
git ls-files | grep -E "\.env$|secret|password" | grep -v ".example"

# Verificar tags
git tag -l
```

**Criterios de Aceptación:**
- [x] Repositorio completo y organizado
- [x] No hay archivos sensibles
- [x] Tag de versión creado (ej: v0.1.0)
- [x] README actualizado

### ✅ Docker

```bash
# Verificar Dockerfile
docker build -t textlab-backend:test .

# Verificar docker-compose
docker-compose config

# Verificar docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml config
```

**Criterios de Aceptación:**
- [x] Dockerfile build sin errores
- [x] docker-compose.yml válido
- [x] docker-compose.prod.yml válido
- [x] Imagen optimizada (multi-stage)

### ✅ Migraciones

```bash
# Verificar migraciones
alembic history

# Verificar que todas aplican
alembic upgrade head

# Verificar que se puede hacer downgrade
alembic downgrade -1
alembic upgrade head
```

**Criterios de Aceptación:**
- [x] Todas las migraciones aplican
- [x] Migraciones son reversibles
- [x] No hay migraciones conflictivas
- [x] Tablas creadas correctamente

### ✅ Base de Datos

```bash
# Conectar a PostgreSQL y verificar tablas
docker-compose exec postgres psql -U textlab -d textlab_db -c "\dt"

# Verificar estructura de tablas clave
docker-compose exec postgres psql -U textlab -d textlab_db -c "\d users"
docker-compose exec postgres psql -U textlab -d textlab_db -c "\d documents"
docker-compose exec postgres psql -U textlab -d textlab_db -c "\d document_analysis"
docker-compose exec postgres psql -U textlab -d textlab_db -c "\d audit_logs"
```

**Criterios de Aceptación:**
- [x] Todas las tablas existen
- [x] Índices creados
- [x] Foreign keys configuradas
- [x] Constraints aplicados

### ✅ Servicios

```bash
# Verificar que todos los servicios están corriendo
docker-compose ps

# Verificar health checks
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Verificar Celery
docker-compose exec celery celery -A app.celery_app inspect active
```

**Criterios de Aceptación:**
- [x] Backend corriendo
- [x] PostgreSQL corriendo
- [x] Redis corriendo
- [x] Celery worker corriendo
- [x] Health checks responden

---

## Comandos de Verificación Rápida

### Script de Verificación Completa

```bash
#!/bin/bash
# verify_deployment.sh

set -e

echo "🔍 Verificando TextLab Backend..."

# 1. Health checks
echo "1. Health Checks..."
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:8000/ready || exit 1
echo "✓ Health checks OK"

# 2. Tests
echo "2. Running Tests..."
pytest -v --tb=short || exit 1
echo "✓ Tests OK"

# 3. Linting
echo "3. Linting..."
black --check app tests || exit 1
isort --check-only app tests || exit 1
flake8 app tests || exit 1
echo "✓ Linting OK"

# 4. Database
echo "4. Database..."
docker-compose exec -T postgres psql -U textlab -d textlab_db -c "SELECT COUNT(*) FROM users;" > /dev/null || exit 1
echo "✓ Database OK"

# 5. Services
echo "5. Services..."
docker-compose ps | grep -q "Up" || exit 1
echo "✓ Services OK"

# 6. OpenAPI
echo "6. OpenAPI..."
curl -f http://localhost:8000/openapi.json > /dev/null || exit 1
echo "✓ OpenAPI OK"

echo "✅ All checks passed!"
```

### Verificación de Tablas SQL

```sql
-- Verificar todas las tablas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Verificar estructura de users
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Verificar índices
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Verificar foreign keys
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;
```

---

## Checklist de Entrega Final

### Pre-Entrega

- [x] Todos los endpoints funcionan
- [x] Todos los tests pasan
- [x] Linting sin errores
- [x] Documentación completa
- [x] Secrets no en repositorio
- [x] Docker build exitoso
- [x] Migraciones aplicadas
- [x] Health checks funcionan

### Entrega

- [x] Tag de versión creado: `git tag v0.1.0`
- [x] Changelog actualizado
- [x] README final revisado
- [x] OpenAPI exportado
- [x] PR de cierre creado con esta checklist

### Post-Entrega

- [x] Deploy a staging exitoso
- [x] Pruebas en staging pasadas
- [x] Documentación de deploy verificada
- [x] Monitoreo configurado

---

## Notas Finales

- Ejecutar esta checklist en un entorno limpio
- Verificar con datos reales, no solo mocks
- Documentar cualquier issue encontrado
- Mantener esta checklist actualizada

**Última actualización:** $(date +%Y-%m-%d)

