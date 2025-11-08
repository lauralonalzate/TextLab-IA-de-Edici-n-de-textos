"""
Celery tasks for audit log management.
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="archive_old_audit_logs")
def archive_old_audit_logs(self, days: int = 365) -> Dict[str, Any]:
    """
    Archive audit logs older than specified days.
    
    This task:
    1. Finds logs older than the specified number of days
    2. Marks them as archived
    3. Returns count of archived logs
    
    Args:
        days: Number of days (default: 365)
    
    Returns:
        Dictionary with archive results
    """
    db = SessionLocal()
    try:
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Find logs to archive
        logs_to_archive = db.query(AuditLog).filter(
            AuditLog.archived == False,
            AuditLog.timestamp < cutoff_date
        ).all()
        
        count = len(logs_to_archive)
        
        # Mark as archived
        for log in logs_to_archive:
            log.archived = True
        
        db.commit()
        
        logger.info(f"Archived {count} audit logs older than {days} days")
        
        return {
            "status": "completed",
            "archived_count": count,
            "cutoff_date": cutoff_date.isoformat(),
            "days": days,
        }
    
    except Exception as e:
        logger.error(f"Error archiving audit logs: {e}", exc_info=True)
        db.rollback()
        # Update task state
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
    
    finally:
        db.close()

