# Changelog

All notable changes to the TextLab Backend project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-XX

### Added

#### Core Infrastructure
- FastAPI application with PostgreSQL and SQLAlchemy ORM
- Alembic for database migrations
- JWT authentication with refresh tokens
- Celery + Redis for asynchronous task processing
- Docker and Docker Compose setup for local development
- GitHub Actions CI/CD pipeline

#### Authentication & Authorization
- User registration endpoint (`POST /api/v1/auth/register`)
- User login endpoint (`POST /api/v1/auth/login`)
- Token refresh endpoint (`POST /api/v1/auth/refresh`)
- Role-based access control (student, teacher, researcher, admin)
- Protected endpoints with JWT authentication
- User profile endpoint (`GET /api/v1/users/me`)

#### Document Management
- Create document (`POST /api/v1/documents`)
- List documents with pagination and search (`GET /api/v1/documents`)
- Get document by ID (`GET /api/v1/documents/{id}`)
- Update document (`PUT /api/v1/documents/{id}`)
- Delete document (`DELETE /api/v1/documents/{id}`)
- Share document (`POST /api/v1/documents/{id}/share`)
- Document versioning (automatic snapshots on update)
- Public/private document visibility

#### NLP Analysis Service
- Text analysis for spelling, grammar, and style errors
- LanguageTool integration (with fallback mock)
- Style analysis (long sentences, passive voice, adverbs)
- Document analysis endpoint (`POST /api/v1/documents/{id}/analyze`)
- Get analysis results (`GET /api/v1/documents/{id}/analysis`)
- Text hashing for caching analysis results
- Asynchronous analysis via Celery tasks

#### APA 7 Citation & Reference Service
- Generate in-text citations (`generate_citation`)
- Generate reference list entries (`generate_reference`)
- Parse raw reference text (`parse_reference_text`)
- Validate citation-reference coherence (`validate_coherence`)
- Support for multiple source types (book, article, web, chapter)
- French indentation for reference lists
- Generate references endpoint (`POST /api/v1/documents/{id}/apa/generate-references`)
- Validate coherence endpoint (`GET /api/v1/documents/{id}/apa/validate`)
- Parse reference endpoint (`POST /api/v1/documents/apa/parse-reference`)

#### Document Export Service
- Export to DOCX format with APA 7 formatting
- Export to PDF format with APA 7 formatting
- French indentation for references
- Institutional template support
- Include/exclude statistics option
- Asynchronous export via Celery tasks
- Export endpoint (`POST /api/v1/documents/{id}/export`)
- Get export job status (`GET /api/v1/export_jobs/{job_id}`)
- Download exported files (`GET /api/v1/downloads/{filename}`)

#### Statistics Service
- Calculate document statistics (word count, character count, paragraphs)
- Reading time estimation (200 wpm)
- Readability metrics (Flesch Reading Ease, Flesch-Kincaid Grade)
- Calculate stats endpoint (`POST /api/v1/documents/{id}/stats`)
- Get stats endpoint (`GET /api/v1/documents/{id}/stats`)
- Statistics overview for admin/teacher (`GET /api/v1/stats/overview`)
- Statistics history with timestamps

#### Audit Logging
- Automatic action logging via middleware
- Manual logging in critical endpoints
- Sanitization of sensitive data (passwords, tokens)
- Audit log query endpoint (`GET /api/v1/admin/audit_logs`)
- Filtering by user and action
- Pagination support
- Automatic archiving of old logs (>365 days)
- IP address and user agent tracking

#### Admin Features
- Admin statistics endpoint (`GET /api/v1/admin/stats`)
- Audit log management
- User management capabilities

#### Testing
- Comprehensive test suite with pytest
- Unit tests for all services
- Integration tests for export functionality
- Mock for LanguageTool
- Test fixtures for users and authentication
- Docker Compose test configuration
- Coverage reporting

#### Documentation
- OpenAPI/Swagger documentation (`/docs`)
- ReDoc documentation (`/redoc`)
- README with setup instructions
- API documentation files for each module
- Example requests and responses
- CHANGELOG

### Technical Details

#### Database Models
- `User` - User accounts with roles
- `Document` - User documents
- `DocumentVersion` - Document version history
- `DocumentAnalysis` - NLP analysis results
- `DocumentStats` - Document statistics
- `Citation` - In-text citations
- `Reference` - Bibliography references
- `ExportJob` - Export job tracking
- `AuditLog` - Audit trail

#### Services
- `nlp_service` - Text analysis service
- `apa_service` - APA 7 formatting service
- `export_service` - Document export service
- `stats_service` - Statistics calculation service
- `audit_service` - Audit logging service

#### Celery Tasks
- `analyze_document_text` - Asynchronous NLP analysis
- `validate_apa_coherence` - Asynchronous coherence validation
- `export_document` - Asynchronous document export
- `calculate_document_stats` - Asynchronous statistics calculation
- `archive_old_audit_logs` - Archive old audit logs

### Security
- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- Sensitive data sanitization in audit logs
- CORS configuration

### Performance
- Database indexing on frequently queried fields
- Text hashing for analysis caching
- Asynchronous task processing
- Pagination for large result sets
- Connection pooling

### Development
- Code formatting with black
- Import sorting with isort
- Linting with flake8
- Type hints throughout codebase
- Comprehensive error handling
- Logging configuration

