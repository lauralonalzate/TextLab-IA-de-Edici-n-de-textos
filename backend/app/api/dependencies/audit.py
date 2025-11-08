"""
Dependency for manual audit logging.

Use this when you need to log actions that the middleware doesn't catch,
or when you need more control over what gets logged.
"""
from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.audit_service import audit_service


async def log_action(
    action: str,
    details: Optional[dict] = None,
    request: Optional[Request] = None,
    current_user: Optional[User] = None,
    db: Session = None,
):
    """
    Dependency to log an action manually.
    
    Usage:
        @router.post("/some-endpoint")
        async def some_endpoint(
            action_logged: None = Depends(log_action("custom_action"))
        ):
            ...
    """
    def _log_action_internal(
        request: Request = None,
        current_user: User = None,
    ):
        # Get user ID
        user_id = str(current_user.id) if current_user else None
        
        # Get IP and user agent from request
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                ip_address = forwarded_for.split(",")[0].strip()
            user_agent = request.headers.get("User-Agent")
        
        # Log action
        audit_service.log_action(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        return None
    
    return _log_action_internal

