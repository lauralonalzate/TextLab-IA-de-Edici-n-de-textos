"""
Audit middleware for automatic logging of API actions.

This middleware intercepts requests and creates audit logs for relevant actions.
"""
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.services.audit_service import audit_service

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log API actions"""
    
    # Map of routes to actions
    ROUTE_ACTION_MAP = {
        "POST /api/v1/auth/login": "login",
        "POST /api/v1/auth/register": "register",
        "POST /api/v1/auth/refresh": "refresh_token",
        "POST /api/v1/documents": "create_document",
        "PUT /api/v1/documents/{document_id}": "update_document",
        "DELETE /api/v1/documents/{document_id}": "delete_document",
        "POST /api/v1/documents/{document_id}/export": "export_document",
        "POST /api/v1/documents/{document_id}/analyze": "analyze_document",
        "POST /api/v1/documents/{document_id}/apa/generate-references": "generate_references",
        "POST /api/v1/documents/{document_id}/share": "share_document",
    }
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and create audit log if needed"""
        # Get user from request state (set by authentication dependency)
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = str(request.state.user.id)
        
        # Get IP address
        ip_address = request.client.host if request.client else None
        # Check for forwarded IP (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()
        
        # Get user agent
        user_agent = request.headers.get("User-Agent")
        
        # Determine action from route
        route_path = f"{request.method} {request.url.path}"
        action = self._get_action_from_route(route_path)
        
        # Process request
        response = await call_next(request)
        
        # Log action if it's a logged action and request was successful
        if action and response.status_code < 400:
            try:
                # Extract relevant details from request
                details = self._extract_details(request, response)
                
                # Create audit log
                audit_service.log_action(
                    user_id=user_id,
                    action=action,
                    details=details,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            except Exception as e:
                # Don't fail the request if audit logging fails
                logger.error(f"Error in audit middleware: {e}", exc_info=True)
        
        return response
    
    def _get_action_from_route(self, route_path: str) -> str:
        """Get action name from route path"""
        # Try exact match first
        if route_path in self.ROUTE_ACTION_MAP:
            return self.ROUTE_ACTION_MAP[route_path]
        
        # Try pattern matching (e.g., /api/v1/documents/{id})
        for pattern, action in self.ROUTE_ACTION_MAP.items():
            if self._route_matches(pattern, route_path):
                return action
        
        return None
    
    def _route_matches(self, pattern: str, route_path: str) -> bool:
        """Check if route path matches pattern"""
        # Simple pattern matching for {id} placeholders
        pattern_parts = pattern.split("/")
        route_parts = route_path.split("/")
        
        if len(pattern_parts) != len(route_parts):
            return False
        
        for pattern_part, route_part in zip(pattern_parts, route_parts):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                continue  # Placeholder matches anything
            if pattern_part != route_part:
                return False
        
        return True
    
    def _extract_details(self, request: Request, response: Response) -> dict:
        """Extract relevant details from request/response"""
        details = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        }
        
        # Add path parameters if available
        if hasattr(request, "path_params"):
            details["path_params"] = request.path_params
        
        return details

