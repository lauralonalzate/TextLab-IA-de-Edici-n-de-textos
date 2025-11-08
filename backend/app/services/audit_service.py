"""
Audit Service for logging user actions.

Handles creation of audit logs with sanitization to prevent sensitive data exposure.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database import SessionLocal
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for creating audit logs"""
    
    # Actions that should be logged
    LOGGED_ACTIONS = {
        "login",
        "logout",
        "register",
        "create_document",
        "update_document",
        "delete_document",
        "export_document",
        "analyze_document",
        "generate_references",
        "share_document",
    }
    
    # Fields to exclude from details (sensitive data)
    SENSITIVE_FIELDS = {
        "password",
        "password_hash",
        "access_token",
        "refresh_token",
        "secret_key",
        "api_key",
        "token",
    }
    
    def log_action(
        self,
        user_id: Optional[str],
        action: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            user_id: ID of the user performing the action (None for anonymous)
            action: Action name (e.g., "login", "create_document")
            details: Additional details (will be sanitized)
            ip_address: IP address of the client
            user_agent: User agent string
        
        Returns:
            Created AuditLog instance
        """
        # Sanitize details to remove sensitive data
        sanitized_details = self._sanitize_details(details) if details else None
        
        # Create audit log
        db = SessionLocal()
        try:
            import uuid
            user_uuid = uuid.UUID(user_id) if user_id else None
            
            audit_log = AuditLog(
                user_id=user_uuid,
                action=action,
                details=sanitized_details,
                ip_address=ip_address,
                user_agent=user_agent,
                archived=False,
            )
            
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            return audit_log
        
        except Exception as e:
            logger.error(f"Error creating audit log: {e}", exc_info=True)
            db.rollback()
            raise
        
        finally:
            db.close()
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive data from details dictionary.
        
        Args:
            details: Original details dictionary
        
        Returns:
            Sanitized details dictionary
        """
        if not details:
            return {}
        
        sanitized = {}
        for key, value in details.items():
            # Skip sensitive fields
            if key.lower() in self.SENSITIVE_FIELDS:
                sanitized[key] = "[REDACTED]"
                continue
            
            # Recursively sanitize nested dictionaries
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_details(value)
            elif isinstance(value, list):
                # Sanitize list items
                sanitized[key] = [
                    self._sanitize_details(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized


# Singleton instance
audit_service = AuditService()

