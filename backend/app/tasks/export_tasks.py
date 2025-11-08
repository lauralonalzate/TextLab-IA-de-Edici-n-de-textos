"""
Celery tasks for document export.
"""
import logging
from typing import Dict, Any
from datetime import datetime

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.reference import Reference
from app.models.export_job import ExportJob, ExportJobStatus
from app.services.export_service import export_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="export_document")
def export_document(self, job_id: str) -> Dict[str, Any]:
    """
    Export document to PDF or DOCX format.
    
    This task:
    1. Retrieves the export job
    2. Fetches document and references
    3. Generates the file
    4. Updates job status and file path
    
    Args:
        job_id: UUID of the export job
    
    Returns:
        Dictionary with export results
    """
    db = SessionLocal()
    try:
        import uuid
        job_uuid = uuid.UUID(job_id)
        
        # Get export job
        job = db.query(ExportJob).filter(ExportJob.id == job_uuid).first()
        if not job:
            raise ValueError(f"Export job {job_id} not found")
        
        # Update status to running
        job.status = ExportJobStatus.RUNNING
        db.commit()
        
        # Get document
        document = db.query(Document).filter(Document.id == job.document_id).first()
        if not document:
            raise ValueError(f"Document {job.document_id} not found")
        
        # Get references
        references = db.query(Reference).filter(Reference.document_id == job.document_id).all()
        
        # Prepare document data
        document_data = {
            "id": str(document.id),
            "title": document.title,
            "content": document.content or "",
            "metadata": document.metadata or {},
        }
        
        # Prepare references data
        references_data = []
        for ref in references:
            ref_dict = {
                "authors": ref.parsed.get("authors", []) if ref.parsed else [],
                "year": ref.parsed.get("year") if ref.parsed else None,
                "title": ref.parsed.get("title") if ref.parsed else None,
                "source": ref.parsed.get("source") if ref.parsed else None,
                "type": ref.parsed.get("type", "book") if ref.parsed else "book",
                "doi": ref.parsed.get("doi") if ref.parsed else None,
                "url": ref.parsed.get("url") if ref.parsed else None,
                "publisher": ref.parsed.get("publisher") if ref.parsed else None,
                "volume": ref.parsed.get("volume") if ref.parsed else None,
                "issue": ref.parsed.get("issue") if ref.parsed else None,
                "pages": ref.parsed.get("pages") if ref.parsed else None,
            }
            references_data.append(ref_dict)
        
        # Prepare export options (stored in job metadata or use defaults)
        options = {
            "include_stats": getattr(job, "include_stats", False),
            "template_id": getattr(job, "template_id", None),
        }
        
        # Determine format from job or default to PDF
        export_format = getattr(job, "export_format", "pdf") or "pdf"
        
        # Generate filename
        filename = export_service.generate_filename(str(document.id), export_format)
        
        # Export document (returns filename, storage handles the rest)
        try:
            if export_format.lower() == "docx":
                result_filename = export_service.export_to_docx(
                    document_data,
                    references_data,
                    options,
                    filename
                )
            elif export_format.lower() == "pdf":
                result_filename = export_service.export_to_pdf(
                    document_data,
                    references_data,
                    options,
                    filename
                )
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            # Update job with result path (filename only)
            job.status = ExportJobStatus.DONE
            job.result_path = result_filename
            job.finished_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Export completed for job {job_id}. File: {filename}")
            
            return {
                "status": "completed",
                "job_id": job_id,
                "filename": filename,
                "file_path": str(file_path),
            }
        
        except Exception as e:
            logger.error(f"Error exporting document: {e}", exc_info=True)
            job.status = ExportJobStatus.FAILED
            job.finished_at = datetime.now()
            db.commit()
            raise
    
    except Exception as e:
        logger.error(f"Error in export task {job_id}: {e}", exc_info=True)
        db.rollback()
        
        # Update job status to failed
        try:
            job = db.query(ExportJob).filter(ExportJob.id == job_uuid).first()
            if job:
                job.status = ExportJobStatus.FAILED
                job.finished_at = datetime.now()
                db.commit()
        except Exception:
            pass
        
        # Update task state
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
    
    finally:
        db.close()

