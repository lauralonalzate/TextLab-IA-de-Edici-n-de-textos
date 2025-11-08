# Autenticación y Autorización - TextLab

## Endpoints de Autenticación

### 1. Registro de Usuario
**POST** `/api/v1/auth/register`

Registra un nuevo usuario en el sistema.

**Request Body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword123",
  "role": "student"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "student",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "token_type": "bearer"
}
```

**Errores:**
- `400 Bad Request`: Email ya registrado
- `422 Unprocessable Entity`: Datos inválidos (email inválido, password corto, etc.)

### 2. Login
**POST** `/api/v1/auth/login`

Inicia sesión con email y password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "token_type": "bearer"
}
```

**Errores:**
- `401 Unauthorized`: Email o password incorrectos

### 3. Refresh Token
**POST** `/api/v1/auth/refresh`

Renueva el access token usando el refresh token.

**Request Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response (200 OK):**
```json
{
  "access_token": "new_jwt_token_here",
  "refresh_token": "new_refresh_token_here",
  "token_type": "bearer"
}
```

**Errores:**
- `401 Unauthorized`: Token inválido o expirado

## Endpoints Protegidos

### Obtener Usuario Actual
**GET** `/api/v1/users/me`

Obtiene la información del usuario autenticado.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "student",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errores:**
- `401 Unauthorized`: Token inválido o expirado
- `403 Forbidden`: Token no proporcionado

### Estadísticas de Admin
**GET** `/api/v1/admin/stats`

Obtiene estadísticas del sistema. Requiere rol ADMIN o TEACHER.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "total_documents": 100,
  "total_users": 50,
  "total_export_jobs": 25,
  "requested_by": {
    "id": "uuid",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

**Errores:**
- `401 Unauthorized`: Token inválido o expirado
- `403 Forbidden`: Rol insuficiente (requiere ADMIN o TEACHER)

## Uso de Dependencies

### Proteger una Ruta con Autenticación

```python
from fastapi import Depends
from app.api.dependencies import get_current_user
from app.models.user import User

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"message": f"Hello {current_user.email}"}
```

### Proteger una Ruta con Roles Específicos

```python
from fastapi import Depends
from app.api.dependencies import require_roles
from app.models.user import User, UserRole

@router.get("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    return {"message": "Admin access granted"}
```

### Múltiples Roles Permitidos

```python
@router.get("/teacher-or-admin")
async def teacher_or_admin_endpoint(
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))
):
    return {"message": "Access granted"}
```

## Códigos de Estado HTTP

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Solicitud inválida (ej: email duplicado)
- **401 Unauthorized**: No autenticado o token inválido
- **403 Forbidden**: Autenticado pero sin permisos suficientes
- **422 Unprocessable Entity**: Datos de validación inválidos

## Configuración

Variables de entorno necesarias:

```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Seguridad

1. **Passwords**: Hasheados con bcrypt antes de almacenar
2. **JWT Tokens**: Firmados con SECRET_KEY
3. **Token Types**: Access y refresh tokens tienen tipos diferentes
4. **Expiración**: Tokens tienen expiración configurable
5. **No exposición de passwords**: Nunca se devuelven en respuestas

## Tests

Ejecutar tests de autenticación:

```bash
pytest tests/test_auth.py -v
pytest tests/test_authorization.py -v
```

Los tests verifican:
- Registro exitoso y con errores
- Login exitoso y con errores
- Refresh token
- Protección de rutas
- Autorización por roles
- Validación de tokens

