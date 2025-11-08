"""
Celery tasks for document statistics calculation.
"""
import logging
from typing import Dict, Any
from datetime import datetime

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document_stats import DocumentStats
from app.services.stats_service import stats_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="calculate_document_stats")
def calculate_document_stats(self, document_id: str) -> Dict[str, Any]:
    """
    Calculate and save document statistics.
    
    This task:
    1. Fetches the document
    2. Calculates statistics
    3. Saves results to database
    
    Args:
        document_id: UUID of the document to analyze
    
    Returns:
        Dictionary with statistics and status
    """
    db = SessionLocal()
    try:
        import uuid
        doc_uuid = uuid.UUID(document_id)
        
        # Get document
        document = db.query(Document).filter(Document.id == doc_uuid).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Get content
        content = document.content or ""
        
        # Calculate statistics
        logger.info(f"Calculating statistics for document {document_id}")
        stats = stats_service.calculate_stats(content)
        
        # Save statistics to database
        document_stats = DocumentStats(
            document_id=doc_uuid,
            stats=stats,
        )
        db.add(document_stats)
        db.commit()
        db.refresh(document_stats)
        
        logger.info(f"Statistics calculated for document {document_id}")
        
        return {
            "status": "completed",
            "document_id": document_id,
            "stats": stats,
            "stats_id": str(document_stats.id),
        }
    
    except Exception as e:
        logger.error(f"Error calculating statistics for document {document_id}: {e}", exc_info=True)
        db.rollback()
        # Update task state
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
    
    finally:
        db.close()

