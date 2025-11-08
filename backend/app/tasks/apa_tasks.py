"""
Celery tasks for APA 7 validation.
"""
import logging
from typing import Dict, Any

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.citation import Citation
from app.models.reference import Reference
from app.services.apa_service import apa7_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="validate_apa_coherence")
def validate_apa_coherence(self, document_id: str) -> Dict[str, Any]:
    """
    Validate coherence between citations and references in a document.
    
    This task:
    1. Fetches all citations and references for the document
    2. Runs validation
    3. Returns validation report
    
    Args:
        document_id: UUID of the document to validate
    
    Returns:
        Dictionary with validation results
    """
    db = SessionLocal()
    try:
        import uuid
        doc_uuid = uuid.UUID(document_id)
        
        # Get document
        document = db.query(Document).filter(Document.id == doc_uuid).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Get all citations and references
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
        
        logger.info(
            f"Validation completed for document {document_id}. "
            f"Found {len(validation_result['citations_without_reference'])} citations without references, "
            f"{len(validation_result['references_without_citations'])} references without citations, "
            f"{len(validation_result['imperfect_matches'])} imperfect matches."
        )
        
        return {
            "status": "completed",
            "document_id": document_id,
            "validation": validation_result,
            "summary": {
                "total_citations": len(citations),
                "total_references": len(references),
                "citations_without_reference": len(validation_result["citations_without_reference"]),
                "references_without_citations": len(validation_result["references_without_citations"]),
                "imperfect_matches": len(validation_result["imperfect_matches"]),
            },
        }
    
    except Exception as e:
        logger.error(f"Error validating document {document_id}: {e}", exc_info=True)
        db.rollback()
        # Update task state
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
    
    finally:
        db.close()

