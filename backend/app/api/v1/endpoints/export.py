from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
from io import BytesIO

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.export_job import ExportJob, ExportJobStatus
from app.schemas.export import ExportRequest, ExportResponse, ExportJobResponse
from app.tasks.export_tasks import export_document
from app.services.export_service import export_service
from app.services.audit_service import audit_service
from app.core.storage import get_storage

router = APIRouter()


def can_access_document(document: Document, current_user: User) -> bool:
    """Check if current user can access a document"""
    if document.is_public:
        return True
    if document.owner_id == current_user.id:
        return True
    from app.models.user import UserRole
    if current_user.role == UserRole.ADMIN:
        return True
    return False


@router.post("/{document_id}/export", response_model=ExportResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_export(
    document_id: str,
    export_request: ExportRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create an export job for a document.
    
    Queues an asynchronous task to export the document to PDF or DOCX.
    Returns immediately with a job ID.
    """
    import uuid
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format"
        )
    
    document = db.query(Document).filter(Document.id == doc_uuid).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not can_access_document(document, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to export this document"
        )
    
    # Validate format
    if export_request.format.lower() not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'pdf' or 'docx'"
        )
    
    # Create export job
    job = ExportJob(
        document_id=doc_uuid,
        user_id=current_user.id,
        status=ExportJobStatus.QUEUED,
        export_format=export_request.format.lower(),
        include_stats=export_request.include_stats,
        template_id=export_request.template_id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Queue Celery task
    task = export_document.delay(str(job.id))
    
    # Log action
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        audit_service.log_action(
            user_id=str(current_user.id),
            action="export_document",
            details={"document_id": document_id, "format": export_request.format, "job_id": str(job.id)},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception:
        pass
    
    return ExportResponse(
        job_id=str(job.id),
        document_id=document_id,
        status="queued",
        message="Export job queued successfully",
    )


@router.get("/export_jobs/{job_id}", response_model=ExportJobResponse)
async def get_export_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get export job status and download URL.
    
    Returns job information including status and download URL when ready.
    """
    import uuid
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )
    
    job = db.query(ExportJob).filter(ExportJob.id == job_uuid).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found"
        )
    
    # Check permissions: only owner or admin can view job
    if job.user_id != current_user.id:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this export job"
            )
    
    return ExportJobResponse.from_job(job)


@router.get("/downloads/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Download exported file.
    
    Only owner or admin can download files.
    """
    # Security: validate filename (prevent path traversal)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    # Find export job by filename
    job = db.query(ExportJob).filter(ExportJob.result_path == filename).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check permissions
    if job.user_id != current_user.id:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to download this file"
            )
    
    # Check if job is done
    if job.status != ExportJobStatus.DONE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Export job is not complete. Status: {job.status.value}"
        )
    
    # Get file from storage
    storage = get_storage()
    
    if not storage.exists(filename):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    # Get file content
    file_content = storage.get(filename)
    
    # Determine media type
    if filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        media_type = "application/octet-stream"
    
    return StreamingResponse(
        BytesIO(file_content),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

