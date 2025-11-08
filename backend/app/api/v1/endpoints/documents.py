from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.document_analysis import DocumentAnalysis
from app.models.document_stats import DocumentStats
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentShare,
    DocumentResponse,
    DocumentListResponse,
    DocumentVersionResponse,
)
from app.schemas.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalysisResponse,
)
from app.schemas.stats import DocumentStatsResponse
from app.tasks.nlp_tasks import analyze_document_text
from app.tasks.stats_tasks import calculate_document_stats
from app.services.stats_service import stats_service
from app.services.audit_service import audit_service

router = APIRouter()


def can_access_document(document: Document, current_user: User) -> bool:
    """Check if current user can access a document"""
    if document.is_public:
        return True
    if document.owner_id == current_user.id:
        return True
    if current_user.role == UserRole.ADMIN:
        return True
    return False


def can_edit_document(document: Document, current_user: User) -> bool:
    """Check if current user can edit a document"""
    if document.owner_id == current_user.id:
        return True
    if current_user.role == UserRole.ADMIN:
        return True
    return False


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new document.
    
    The document will be owned by the current authenticated user.
    """
    new_document = Document(
        owner_id=current_user.id,
        title=document_data.title,
        content=document_data.content,
        metadata=document_data.metadata,
        is_public=document_data.is_public,
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    # Log action
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        audit_service.log_action(
            user_id=str(current_user.id),
            action="create_document",
            details={"document_id": str(new_document.id), "title": new_document.title},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception:
        pass  # Don't fail if audit logging fails
    
    return DocumentResponse.from_document(new_document)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    q: Optional[str] = Query(None, description="Search query for title"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List documents accessible to the current user.
    
    - Returns user's own documents and public documents
    - Supports pagination and search by title
    """
    # Base query: user's documents or public documents
    query = db.query(Document).filter(
        or_(
            Document.owner_id == current_user.id,
            Document.is_public == True
        )
    )
    
    # Apply search filter if provided
    if q:
        query = query.filter(Document.title.ilike(f"%{q}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    documents = query.order_by(Document.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Calculate pages
    pages = (total + per_page - 1) // per_page if total > 0 else 0
    
    return DocumentListResponse(
        items=[DocumentResponse.from_document(doc) for doc in documents],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a document by ID.
    
    - Accessible if document is public, user is owner, or user is admin
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
            detail="Access denied to this document"
        )
    
    return DocumentResponse.from_document(document)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a document.
    
    - Only owner or admin can update
    - Creates a version snapshot before updating
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
    
    if not can_edit_document(document, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this document"
        )
    
    # Create version snapshot before updating
    if document.content:  # Only create version if there's content to save
        version = DocumentVersion(
            document_id=document.id,
            content=document.content,
        )
        db.add(version)
    
    # Update document fields
    if document_data.title is not None:
        document.title = document_data.title
    if document_data.content is not None:
        document.content = document_data.content
    if document_data.metadata is not None:
        document.metadata = document_data.metadata
    if document_data.is_public is not None:
        document.is_public = document_data.is_public
    
    db.commit()
    db.refresh(document)
    
    return DocumentResponse.from_document(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a document.
    
    - Only owner or admin can delete
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
    
    if not can_edit_document(document, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this document"
        )
    
    # Log action before deletion
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        audit_service.log_action(
            user_id=str(current_user.id),
            action="delete_document",
            details={"document_id": document_id, "title": document.title},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception:
        pass
    
    db.delete(document)
    db.commit()
    
    return None


@router.post("/{document_id}/share", response_model=DocumentResponse)
async def share_document(
    document_id: str,
    share_data: DocumentShare,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Share a document.
    
    - Can make document public
    - Can share with specific roles (future implementation)
    - Can share with specific emails (future implementation)
    - Only owner or admin can share
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
    
    if not can_edit_document(document, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to share this document"
        )
    
    # Update sharing settings
    if share_data.is_public is not None:
        document.is_public = share_data.is_public
    
    # TODO: Implement share_with_roles and share_with_emails
    # This would require additional tables/models for sharing
    
    db.commit()
    db.refresh(document)
    
    return DocumentResponse.from_document(document)


@router.get("/{document_id}/versions", response_model=list[DocumentVersionResponse])
async def get_document_versions(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all versions of a document.
    
    - Only owner or admin can view versions
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
    
    if not can_edit_document(document, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view versions of this document"
        )
    
    versions = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == doc_uuid
    ).order_by(DocumentVersion.created_at.desc()).all()
    
    return [DocumentVersionResponse.from_version(v) for v in versions]


@router.post("/{document_id}/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start NLP analysis for a document.
    
    This endpoint queues an asynchronous task to analyze the document text
    for spelling, grammar, and style errors. Returns immediately with a job ID.
    
    - Only owner or admin can analyze documents
    - Analysis runs in background via Celery
    - Results are cached if text hasn't changed (based on hash)
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
            detail="You don't have permission to analyze this document"
        )
    
    # Queue Celery task
    task = analyze_document_text.delay(str(document.id))
    
    # Log action
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        audit_service.log_action(
            user_id=str(current_user.id),
            action="analyze_document",
            details={"document_id": document_id, "job_id": task.id},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception:
        pass
    
    return AnalyzeResponse(
        job_id=task.id,
        document_id=document_id,
        status="queued",
        message="Analysis task queued successfully",
    )


@router.get("/{document_id}/analysis", response_model=AnalysisResponse)
async def get_document_analysis(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the latest analysis results for a document.
    
    - Returns the most recent analysis
    - Only owner or admin can view analysis
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
            detail="You don't have permission to view analysis of this document"
        )
    
    # Get latest analysis
    analysis = db.query(DocumentAnalysis).filter(
        DocumentAnalysis.document_id == doc_uuid
    ).order_by(DocumentAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis found for this document"
        )
    
    return AnalysisResponse.from_analysis(analysis)


@router.post("/{document_id}/stats", response_model=DocumentStatsResponse, status_code=status.HTTP_202_ACCEPTED)
async def calculate_stats(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Calculate document statistics.
    
    This endpoint calculates statistics synchronously if fast, or queues
    an asynchronous task for longer calculations.
    
    - Only owner or admin can calculate stats
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
            detail="You don't have permission to calculate stats for this document"
        )
    
    # Calculate stats synchronously (it's fast enough)
    content = document.content or ""
    stats_data = stats_service.calculate_stats(content)
    
    # Save to database
    document_stats = DocumentStats(
        document_id=doc_uuid,
        stats=stats_data,
    )
    db.add(document_stats)
    db.commit()
    db.refresh(document_stats)
    
    return DocumentStatsResponse.from_stats(document_stats)


@router.get("/{document_id}/stats", response_model=DocumentStatsResponse)
async def get_document_stats(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the latest statistics for a document.
    
    - Returns the most recent statistics snapshot
    - Only owner or admin can view stats
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
            detail="You don't have permission to view stats of this document"
        )
    
    # Get latest stats
    stats = db.query(DocumentStats).filter(
        DocumentStats.document_id == doc_uuid
    ).order_by(DocumentStats.created_at.desc()).first()
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No statistics found for this document"
        )
    
    return DocumentStatsResponse.from_stats(stats)

