from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.citation import Citation
from app.models.reference import Reference
from app.schemas.apa import (
    GenerateReferencesRequest,
    GenerateReferencesResponse,
    ParseReferenceRequest,
    ParseReferenceResponse,
    ValidationResponse,
    ParsedReference,
)
from app.services.apa_service import apa7_service
from app.services.audit_service import audit_service

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


@router.post("/{document_id}/apa/generate-references", response_model=GenerateReferencesResponse)
async def generate_references(
    document_id: str,
    request_data: GenerateReferencesRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a complete reference list from parsed references.
    
    Takes a list of parsed references and returns a formatted bibliography
    ready for export (with hanging indent).
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
            detail="You don't have permission to access this document"
        )
    
    # Convert Pydantic models to dicts
    ref_dicts = [ref.dict() for ref in request_data.references]
    
    # Generate reference list
    reference_list = apa7_service.generate_reference_list(
        ref_dicts,
        format_output=request_data.format
    )
    
    # Log action
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        audit_service.log_action(
            user_id=str(current_user.id),
            action="generate_references",
            details={"document_id": document_id, "reference_count": len(ref_dicts), "format": request_data.format},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception:
        pass
    
    return GenerateReferencesResponse(
        reference_list=reference_list,
        format=request_data.format,
    )


@router.get("/{document_id}/apa/validate", response_model=ValidationResponse)
async def validate_coherence(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Validate coherence between citations and references in a document.
    
    Returns:
    - Citations without matching references
    - References without matching citations
    - Imperfect matches (same key but different authors/year)
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
            detail="You don't have permission to access this document"
        )
    
    # Get all citations and references for this document
    citations = db.query(Citation).filter(Citation.document_id == doc_uuid).all()
    references = db.query(Reference).filter(Reference.document_id == doc_uuid).all()
    
    # Convert to dictionaries for validation
    citation_dicts = []
    for cit in citations:
        cit_dict = {
            "citation_key": cit.citation_key,
            "citation_text": cit.citation_text,
            "parsed": cit.parsed or {},
        }
        citation_dicts.append(cit_dict)
    
    reference_dicts = []
    for ref in references:
        ref_dict = {
            "ref_key": ref.ref_key,
            "ref_text": ref.ref_text,
            "parsed": ref.parsed or {},
        }
        reference_dicts.append(ref_dict)
    
    # Run validation
    validation_result = apa7_service.validate_coherence(citation_dicts, reference_dicts)
    
    # Convert to response format
    return ValidationResponse(
        citations_without_reference=[
            {
                "citation_key": item.get("citation_key"),
                "citation_text": item.get("citation_text"),
                "issue": "No matching reference found",
            }
            for item in validation_result["citations_without_reference"]
        ],
        references_without_citations=[
            {
                "ref_key": item.get("ref_key"),
                "ref_text": item.get("ref_text"),
                "issue": "No matching citation found",
            }
            for item in validation_result["references_without_citations"]
        ],
        imperfect_matches=validation_result["imperfect_matches"],
    )


@router.post("/apa/parse-reference", response_model=ParseReferenceResponse)
async def parse_reference(
    request: ParseReferenceRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Parse raw reference text into structured components.
    
    Uses heuristics and regex to extract authors, year, title, etc.
    """
    parsed = apa7_service.parse_reference_text(request.raw_text)
    
    return ParseReferenceResponse(
        parsed=ParsedReference(**parsed)
    )

