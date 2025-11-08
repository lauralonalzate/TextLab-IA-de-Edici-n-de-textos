# Servicio de Auditoría - TextLab

## Descripción

Sistema de auditoría completo para registrar todas las acciones relevantes de los usuarios en la plataforma TextLab.

## Características

### Registro Automático
- Middleware que intercepta requests y registra acciones automáticamente
- Logging manual en endpoints críticos
- Sanitización automática de datos sensibles (contraseñas, tokens)

### Acciones Registradas
- `login` - Inicio de sesión
- `register` - Registro de usuario
- `create_document` - Creación de documento
- `update_document` - Actualización de documento
- `delete_document` - Eliminación de documento
- `export_document` - Exportación de documento
- `analyze_document` - Análisis de documento
- `generate_references` - Generación de referencias
- `share_document` - Compartir documento

### Campos Registrados
- `user_id` - ID del usuario (null para acciones anónimas)
- `action` - Nombre de la acción
- `details` - Detalles adicionales (JSONB, sanitizado)
- `ip_address` - Dirección IP del cliente
- `user_agent` - User agent del navegador
- `archived` - Si el log está archivado
- `timestamp` - Fecha y hora de la acción

## Endpoints

### GET `/api/v1/admin/audit_logs`

Obtiene logs de auditoría con paginación y filtros.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, default: 1): Número de página
- `per_page` (int, default: 10, max: 100): Elementos por página
- `filter_user` (string, optional): Filtrar por ID de usuario
- `action` (string, optional): Filtrar por acción

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "123e4567-e89b-12d3-a456-426614174001",
      "action": "login",
      "details": {
        "method": "POST",
        "path": "/api/v1/auth/login",
        "status_code": 200
      },
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "archived": false,
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 10,
  "pages": 10
}
```

**Permisos:**
- Solo administradores pueden ver logs de auditoría

## Sanitización de Datos

El servicio automáticamente sanitiza los siguientes campos en `details`:
- `password`
- `password_hash`
- `access_token`
- `refresh_token`
- `secret_key`
- `api_key`
- `token`

Estos campos se reemplazan con `[REDACTED]` antes de guardarse.

## Política de Retención

### Archivado Automático
Los logs más antiguos de 365 días se marcan como archivados mediante una tarea Celery:

```python
from app.tasks.audit_tasks import archive_old_audit_logs

# Archivar logs más antiguos de 365 días
result = archive_old_audit_logs.delay(days=365)
```

### Configuración
- Por defecto, los logs se archivan después de 365 días
- Los logs archivados no aparecen en las consultas normales
- Se puede configurar un período diferente pasando el parámetro `days`

## Uso del Servicio

### Logging Manual

```python
from app.services.audit_service import audit_service

# Log una acción
audit_service.log_action(
    user_id=str(current_user.id),
    action="custom_action",
    details={"key": "value"},
    ip_address=request.client.host,
    user_agent=request.headers.get("User-Agent"),
)
```

### Middleware Automático

El middleware se registra automáticamente en `app/main.py` y captura acciones basándose en rutas configuradas.

## Ejemplo de Uso

```bash
# 1. Consultar logs de auditoría
curl -X GET "http://localhost:8000/api/v1/admin/audit_logs?page=1&per_page=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Filtrar por usuario
curl -X GET "http://localhost:8000/api/v1/admin/audit_logs?filter_user=USER_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Filtrar por acción
curl -X GET "http://localhost:8000/api/v1/admin/audit_logs?action=login" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Tests

Ejecutar tests:

```bash
pytest tests/test_audit.py -v
```

Los tests cubren:
- Creación de logs
- Sanitización de datos sensibles
- Endpoints de consulta
- Filtros y paginación
- Control de acceso
- Tarea de archivado

## Notas

- Los logs no contienen contraseñas ni datos sensibles
- Solo administradores pueden consultar logs
- Los logs archivados no aparecen en consultas normales
- El middleware no falla si el logging falla (no interrumpe requests)
- Se soporta IPv6 en el campo `ip_address` (hasta 45 caracteres)

