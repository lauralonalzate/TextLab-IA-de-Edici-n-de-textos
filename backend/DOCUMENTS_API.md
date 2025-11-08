# API REST de Documentos - TextLab

## Endpoints

### 1. Crear Documento
**POST** `/api/v1/documents`

Crea un nuevo documento. El documento será propiedad del usuario autenticado.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Mi Primer Documento",
  "content": "# Introducción\n\nEste es el contenido de mi documento.",
  "metadata": {
    "language": "es",
    "template": "article",
    "word_count": 150
  },
  "is_public": false
}
```

**Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "owner_id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "Mi Primer Documento",
  "content": "# Introducción\n\nEste es el contenido de mi documento.",
  "metadata": {
    "language": "es",
    "template": "article",
    "word_count": 150
  },
  "is_public": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errores:**
- `400 Bad Request`: Datos inválidos
- `403 Forbidden`: No autenticado

---

### 2. Listar Documentos
**GET** `/api/v1/documents`

Lista los documentos accesibles al usuario (propios y públicos).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, default: 1): Número de página
- `per_page` (int, default: 10, max: 100): Elementos por página
- `q` (string, optional): Búsqueda por título

**Ejemplos:**
```
GET /api/v1/documents?page=1&per_page=10
GET /api/v1/documents?q=Python&page=1
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "owner_id": "123e4567-e89b-12d3-a456-426614174001",
      "title": "Documento 1",
      "content": "Contenido 1",
      "metadata": {},
      "is_public": false,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "per_page": 10,
  "pages": 1
}
```

**Errores:**
- `403 Forbidden`: No autenticado

---

### 3. Obtener Documento
**GET** `/api/v1/documents/{id}`

Obtiene un documento por ID. Accesible si:
- El documento es público
- El usuario es el propietario
- El usuario es admin

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "owner_id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "Mi Documento",
  "content": "# Contenido\n\nContenido del documento.",
  "metadata": {"language": "es"},
  "is_public": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errores:**
- `400 Bad Request`: ID inválido
- `403 Forbidden`: Sin acceso o no autenticado
- `404 Not Found`: Documento no encontrado

---

### 4. Actualizar Documento
**PUT** `/api/v1/documents/{id}`

Actualiza un documento. Solo el propietario o admin pueden actualizar.
Crea automáticamente una versión del contenido anterior.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (todos los campos son opcionales):**
```json
{
  "title": "Título Actualizado",
  "content": "# Contenido Actualizado\n\nNuevo contenido.",
  "metadata": {
    "language": "en",
    "word_count": 200
  },
  "is_public": true
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "owner_id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "Título Actualizado",
  "content": "# Contenido Actualizado\n\nNuevo contenido.",
  "metadata": {
    "language": "en",
    "word_count": 200
  },
  "is_public": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T01:00:00Z"
}
```

**Errores:**
- `400 Bad Request`: ID inválido
- `403 Forbidden`: Sin permiso para editar o no autenticado
- `404 Not Found`: Documento no encontrado

---

### 5. Eliminar Documento
**DELETE** `/api/v1/documents/{id}`

Elimina un documento. Solo el propietario o admin pueden eliminar.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content):**
Sin cuerpo de respuesta.

**Errores:**
- `400 Bad Request`: ID inválido
- `403 Forbidden`: Sin permiso para eliminar o no autenticado
- `404 Not Found`: Documento no encontrado

---

### 6. Compartir Documento
**POST** `/api/v1/documents/{id}/share`

Comparte un documento (hacer público, compartir con roles/emails).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "is_public": true,
  "share_with_roles": ["teacher", "researcher"],
  "share_with_emails": ["user@example.com"]
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "owner_id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "Mi Documento",
  "content": "Contenido",
  "metadata": {},
  "is_public": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errores:**
- `400 Bad Request`: ID inválido
- `403 Forbidden`: Sin permiso para compartir o no autenticado
- `404 Not Found`: Documento no encontrado

---

### 7. Obtener Versiones de Documento
**GET** `/api/v1/documents/{id}/versions`

Obtiene todas las versiones de un documento. Solo el propietario o admin pueden ver las versiones.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174002",
    "document_id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "# Versión Anterior\n\nContenido anterior.",
    "created_at": "2024-01-01T00:30:00Z"
  },
  {
    "id": "123e4567-e89b-12d3-a456-426614174003",
    "document_id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "# Versión Original\n\nContenido original.",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

**Errores:**
- `400 Bad Request`: ID inválido
- `403 Forbidden`: Sin permiso para ver versiones o no autenticado
- `404 Not Found`: Documento no encontrado

---

## Permisos

### Acceso a Documentos
- **Público**: Cualquier usuario autenticado puede ver documentos con `is_public: true`
- **Propietario**: El usuario puede ver, editar y eliminar sus propios documentos
- **Admin**: Los administradores pueden ver, editar y eliminar cualquier documento

### Operaciones
- **Crear**: Cualquier usuario autenticado
- **Listar**: Usuario autenticado (ve sus documentos y los públicos)
- **Ver**: Si es público, propietario o admin
- **Editar**: Solo propietario o admin
- **Eliminar**: Solo propietario o admin
- **Compartir**: Solo propietario o admin
- **Ver Versiones**: Solo propietario o admin

## Versionado

Cada vez que se actualiza el contenido de un documento, se crea automáticamente una versión (snapshot) del contenido anterior en la tabla `documents_versions`. Esto permite:

- Ver el historial de cambios
- Restaurar versiones anteriores (funcionalidad futura)
- Auditoría de cambios

Las versiones se ordenan por fecha de creación (más recientes primero).

## Ejemplos de Uso

### Crear y Actualizar Documento

```bash
# 1. Crear documento
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Documento",
    "content": "# Título\n\nContenido inicial.",
    "is_public": false
  }'

# 2. Actualizar documento (crea versión automáticamente)
curl -X PUT "http://localhost:8000/api/v1/documents/DOCUMENT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Título\n\nContenido actualizado."
  }'

# 3. Ver versiones
curl -X GET "http://localhost:8000/api/v1/documents/DOCUMENT_ID/versions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Búsqueda y Paginación

```bash
# Buscar documentos por título
curl -X GET "http://localhost:8000/api/v1/documents?q=Python&page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Listar segunda página
curl -X GET "http://localhost:8000/api/v1/documents?page=2&per_page=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Compartir Documento

```bash
# Hacer documento público
curl -X POST "http://localhost:8000/api/v1/documents/DOCUMENT_ID/share" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_public": true
  }'
```

## Códigos de Estado HTTP

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **204 No Content**: Recurso eliminado exitosamente
- **400 Bad Request**: Solicitud inválida (ID inválido, etc.)
- **403 Forbidden**: Sin permisos o no autenticado
- **404 Not Found**: Recurso no encontrado
- **422 Unprocessable Entity**: Datos de validación inválidos

