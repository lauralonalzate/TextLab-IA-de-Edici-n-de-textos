"""
Rate limiting configuration using slowapi.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

from app.core.config import settings


def get_limiter_key(request: Request) -> str:
    """
    Get rate limit key from request.
    
    Uses IP address from request, handling proxy headers if configured.
    """
    if settings.TRUST_PROXY:
        # Check for forwarded IP (X-Forwarded-For header)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in chain
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
    
    # Fallback to direct client IP
    return get_remote_address(request)


# Initialize limiter
limiter = Limiter(
    key_func=get_limiter_key,
    default_limits=[f"{settings.GENERAL_RATE_LIMIT}/minute"] if settings.ENABLE_RATE_LIMITING else [],
    storage_uri=settings.REDIS_URL,
)


def get_rate_limit_exceeded_handler():
    """Get rate limit exceeded exception handler"""
    return _rate_limit_exceeded_handler

