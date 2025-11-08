from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.api.dependencies import require_roles
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogListResponse, AuditLogResponse

router = APIRouter()


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER)),
    db: Session = Depends(get_db),
):
    """
    Get admin statistics.
    
    Requires ADMIN or TEACHER role.
    """
    from app.models.document import Document
    from app.models.export_job import ExportJob
    
    # Example stats
    total_documents = db.query(Document).count()
    total_users = db.query(User).count()
    total_export_jobs = db.query(ExportJob).count()
    
    return {
        "total_documents": total_documents,
        "total_users": total_users,
        "total_export_jobs": total_export_jobs,
        "requested_by": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role.value,
        }
    }


@router.get("/audit_logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    filter_user: Optional[str] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Get audit logs with pagination and filters.
    
    - Only admins can view audit logs
    - Supports filtering by user and action
    - Returns paginated results
    """
    # Base query: only non-archived logs
    query = db.query(AuditLog).filter(AuditLog.archived == False)
    
    # Apply filters
    if filter_user:
        import uuid
        try:
            user_uuid = uuid.UUID(filter_user)
            query = query.filter(AuditLog.user_id == user_uuid)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid user ID format"
            )
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(per_page).all()
    
    # Calculate pages
    pages = (total + per_page - 1) // per_page if total > 0 else 0
    
    return AuditLogListResponse(
        items=[AuditLogResponse.from_log(log) for log in logs],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )

