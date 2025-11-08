from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: str
    user_id: Optional[str]
    action: str
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    archived: bool
    timestamp: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
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
                "archived": False,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }

    @classmethod
    def from_log(cls, log):
        """Create AuditLogResponse from AuditLog model"""
        return cls(
            id=str(log.id),
            user_id=str(log.user_id) if log.user_id else None,
            action=log.action,
            details=log.details,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            archived=log.archived,
            timestamp=log.timestamp,
        )


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list response"""
    items: List[AuditLogResponse]
    total: int
    page: int
    per_page: int
    pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174001",
                        "action": "login",
                        "details": {},
                        "ip_address": "192.168.1.1",
                        "archived": False,
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 100,
                "page": 1,
                "per_page": 10,
                "pages": 10
            }
        }

