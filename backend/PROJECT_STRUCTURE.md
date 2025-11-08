# Estructura del Proyecto TextLab Backend

```
.
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow
├── alembic/                    # Migraciones de base de datos
│   ├── versions/               # Archivos de migración
│   ├── env.py                  # Configuración de Alembic
│   └── script.py.mako            # Template para migraciones
├── app/                        # Aplicación principal
│   ├── api/                    # Endpoints de la API
│   │   └── v1/                 # Versión 1 de la API
│   │       ├── __init__.py
│   │       └── router.py       # Router principal de la API
│   ├── core/                   # Configuración core
│   │   ├── __init__.py
│   │   ├── config.py           # Configuración y settings
│   │   ├── database.py         # Configuración de SQLAlchemy
│   │   └── celery_app.py       # Configuración de Celery
│   ├── models/                 # Modelos SQLAlchemy
│   │   └── __init__.py
│   ├── schemas/                # Schemas Pydantic
│   │   └── __init__.py
│   ├── tasks/                  # Tareas de Celery
│   │   └── __init__.py
│   ├── utils/                  # Utilidades
│   │   ├── __init__.py
│   │   └── auth.py             # Utilidades de autenticación
│   ├── __init__.py
│   └── main.py                 # Aplicación FastAPI
├── tests/                      # Tests
│   ├── __init__.py
│   ├── conftest.py             # Configuración de pytest
│   └── test_health.py          # Test del endpoint health
├── .env.example                # Ejemplo de variables de entorno
├── .gitignore                  # Archivos ignorados por git
├── docker-compose.yml          # Configuración Docker Compose
├── Dockerfile                  # Imagen Docker del backend
├── alembic.ini                 # Configuración de Alembic
├── pyproject.toml              # Configuración del proyecto
├── requirements.txt            # Dependencias de producción
├── requirements-dev.txt        # Dependencias de desarrollo
├── README.md                   # Documentación principal
└── PROJECT_STRUCTURE.md        # Este archivo
```

## Descripción de Carpetas

### `app/`
Contiene todo el código de la aplicación FastAPI.

- **`api/v1/`**: Endpoints de la API organizados por versión
- **`core/`**: Configuración central (DB, Celery, settings)
- **`models/`**: Modelos SQLAlchemy (tablas de la base de datos)
- **`schemas/`**: Schemas Pydantic (validación de datos)
- **`tasks/`**: Tareas asíncronas de Celery (NLP, export, etc.)
- **`utils/`**: Funciones utilitarias (auth, helpers, etc.)

### `alembic/`
Sistema de migraciones de base de datos.

- **`versions/`**: Archivos de migración generados
- **`env.py`**: Configuración del entorno de Alembic

### `tests/`
Tests unitarios e integración con pytest.

### `.github/workflows/`
CI/CD con GitHub Actions para lint y tests.

