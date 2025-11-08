"""
Celery tasks for NLP analysis.
"""
import logging
from typing import Dict, Any

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document_analysis import DocumentAnalysis
from app.services.nlp_service import nlp_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="analyze_document_text")
def analyze_document_text(self, document_id: str) -> Dict[str, Any]:
    """
    Analyze document text for spelling, grammar, and style errors.
    
    This task:
    1. Fetches the document
    2. Computes text hash
    3. Checks if analysis already exists for this hash
    4. Runs NLP analysis
    5. Saves results to database
    
    Args:
        document_id: UUID of the document to analyze
    
    Returns:
        Dictionary with analysis results and status
    """
    db = SessionLocal()
    try:
        import uuid
        doc_uuid = uuid.UUID(document_id)
        
        # Get document
        document = db.query(Document).filter(Document.id == doc_uuid).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Get text to analyze
        text = document.content or ""
        if not text:
            return {
                "status": "skipped",
                "message": "Document has no content to analyze",
                "suggestions": [],
            }
        
        # Compute text hash
        text_hash = DocumentAnalysis.compute_text_hash(text)
        
        # Check if analysis already exists for this text hash
        existing_analysis = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.document_id == doc_uuid,
            DocumentAnalysis.text_hash == text_hash,
        ).first()
        
        if existing_analysis:
            logger.info(f"Analysis already exists for document {document_id} with hash {text_hash}")
            return {
                "status": "cached",
                "message": "Analysis already exists for this text version",
                "suggestions": existing_analysis.analysis.get("suggestions", []),
                "analysis_id": str(existing_analysis.id),
            }
        
        # Run NLP analysis
        logger.info(f"Running NLP analysis for document {document_id}")
        suggestions = nlp_service.analyze_text(text)
        
        # Prepare analysis result
        analysis_data = {
            "suggestions": suggestions,
            "stats": {
                "total_suggestions": len(suggestions),
                "spelling_errors": len([s for s in suggestions if s.get("error_type") == "SPELLING"]),
                "grammar_errors": len([s for s in suggestions if s.get("error_type") == "GRAMMAR"]),
                "style_issues": len([s for s in suggestions if s.get("error_type") == "STYLE"]),
            },
            "text_length": len(text),
            "text_hash": text_hash,
        }
        
        # Save analysis to database
        analysis = DocumentAnalysis(
            document_id=doc_uuid,
            text_hash=text_hash,
            analysis=analysis_data,
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        logger.info(f"Analysis completed for document {document_id}. Found {len(suggestions)} suggestions.")
        
        return {
            "status": "completed",
            "message": "Analysis completed successfully",
            "suggestions": suggestions,
            "stats": analysis_data["stats"],
            "analysis_id": str(analysis.id),
        }
    
    except Exception as e:
        logger.error(f"Error analyzing document {document_id}: {e}", exc_info=True)
        db.rollback()
        # Update task state
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
    
    finally:
        db.close()

