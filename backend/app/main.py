from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.celery_app import celery_app
from app.api.middleware.audit import AuditMiddleware
from app.core.rate_limit import limiter, get_rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TextLab API",
    description="""
    Backend API for TextLab - A comprehensive academic writing platform.
    
    ## Features
    
    * **Document Management**: Create, edit, and manage academic documents
    * **NLP Analysis**: Automatic spelling, grammar, and style checking
    * **APA 7 Support**: Generate citations and references in APA 7th edition format
    * **Document Export**: Export documents to PDF and DOCX with proper formatting
    * **Statistics**: Track word count, reading time, and readability metrics
    * **Audit Logging**: Complete audit trail of user actions
    
    ## Authentication
    
    Most endpoints require authentication. Register a user or login to get an access token.
    Use the token in the Authorization header: `Authorization: Bearer <token>`
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "TextLab Team",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit middleware (after CORS, before routes)
app.add_middleware(AuditMiddleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())

# Include routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """
    Health check endpoint for liveness probe.
    
    Returns basic status without checking dependencies.
    """
    return {"status": "ok", "service": "textlab-api"}


@app.get("/ready")
async def readiness_check():
    """
    Readiness probe endpoint.
    
    Checks if the service is ready to accept traffic by verifying:
    - Database connection
    - Redis connection
    """
    from sqlalchemy import text
    from app.core.database import engine
    import redis
    from app.core.config import settings
    
    checks = {
        "status": "ready",
        "service": "textlab-api",
        "checks": {}
    }
    
    # Check database
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["checks"]["database"] = "ok"
    except Exception as e:
        checks["checks"]["database"] = f"error: {str(e)}"
        checks["status"] = "not_ready"
    
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        checks["checks"]["redis"] = "ok"
    except Exception as e:
        checks["checks"]["redis"] = f"error: {str(e)}"
        checks["status"] = "not_ready"
    
    if checks["status"] == "not_ready":
        from fastapi import status
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=checks
        )
    
    return checks


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Verify Celery connection
    try:
        celery_app.control.inspect().active()
    except Exception:
        pass  # Celery worker might not be running in development


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    pass

