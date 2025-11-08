# TextLab Backend - Verification Scripts

Scripts de verificación y testing para TextLab Backend.

## Scripts Disponibles

### 1. `verify_deployment.sh`

Verificación rápida del deployment.

```bash
./scripts/verify_deployment.sh [API_URL]
```

**Verifica:**
- Health checks
- OpenAPI documentation
- Database connection
- Services status
- Code quality (linting)
- Security basics

**Ejemplo:**
```bash
./scripts/verify_deployment.sh http://localhost:8000/api/v1
```

### 2. `test_endpoints.sh`

Prueba todos los endpoints principales.

```bash
./scripts/test_endpoints.sh [API_URL] [EMAIL] [PASSWORD]
```

**Prueba:**
- Autenticación (register/login)
- Documentos CRUD
- Análisis NLP
- APA 7
- Exportación
- Estadísticas

**Ejemplo:**
```bash
./scripts/test_endpoints.sh http://localhost:8000/api/v1 test@example.com TestPass123!
```

### 3. `check_security.sh`

Revisión de seguridad del código.

```bash
./scripts/check_security.sh
```

**Verifica:**
- Secrets management
- Hardcoded secrets
- SQL injection protection
- Rate limiting
- CORS configuration
- Authentication/Authorization
- Input validation
- Path traversal protection
- HTTPS/SSL
- Security headers

### 4. `backup-db.sh`

Backup manual de la base de datos.

```bash
./scripts/backup-db.sh [backup-name]
```

**Ejemplo:**
```bash
./scripts/backup-db.sh pre-deployment-backup
```

### 5. `restore-db.sh`

Restaurar backup de la base de datos.

```bash
./scripts/restore-db.sh <backup-file.sql.gz>
```

**Ejemplo:**
```bash
./scripts/restore-db.sh backups/backup-20240101-120000.sql.gz
```

## Uso en CI/CD

### GitHub Actions

```yaml
- name: Verify Deployment
  run: |
    chmod +x scripts/*.sh
    ./scripts/verify_deployment.sh ${{ env.API_URL }}

- name: Test Endpoints
  run: |
    ./scripts/test_endpoints.sh ${{ env.API_URL }} ${{ secrets.TEST_EMAIL }} ${{ secrets.TEST_PASSWORD }}

- name: Security Check
  run: |
    ./scripts/check_security.sh
```

## Requisitos

- `curl` - Para testing de endpoints
- `jq` - Para parsing de JSON (opcional pero recomendado)
- `docker-compose` - Para verificación de servicios
- `pytest`, `black`, `isort`, `flake8` - Para code quality

## Notas

- Los scripts son compatibles con bash
- En Windows, usar Git Bash o WSL
- Asegurar permisos de ejecución: `chmod +x scripts/*.sh`

