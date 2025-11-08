import pytest
from fastapi import status
import uuid

from app.models.document import Document
from app.models.document_analysis import DocumentAnalysis
from app.tasks.nlp_tasks import analyze_document_text


class TestAnalyzeDocument:
    """Tests for document analysis endpoints"""

    def test_analyze_document_success(self, client, auth_headers, created_user, db_session):
        """Test successful document analysis request"""
        # Create document with content
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Este es un texto de prueba con algunos errores de ortografia.",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/analyze",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        
        assert "job_id" in data
        assert data["document_id"] == str(doc.id)
        assert data["status"] == "queued"
        assert "message" in data

    def test_analyze_document_no_content(self, client, auth_headers, created_user, db_session):
        """Test analyzing document without content"""
        doc = Document(
            owner_id=created_user.id,
            title="Empty Document",
            content=None,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/analyze",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        # Task will be queued but will skip analysis

    def test_analyze_document_not_found(self, client, auth_headers):
        """Test analyzing non-existent document"""
        fake_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/documents/{fake_id}/analyze",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_analyze_document_unauthorized(self, client, created_user, db_session):
        """Test analyzing document without authentication"""
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(f"/api/v1/documents/{doc.id}/analyze")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyze_document_by_other_user_denied(self, client, auth_headers, created_admin, db_session):
        """Test analyzing document by another user (private document)"""
        doc = Document(
            owner_id=created_admin.id,
            title="Admin's Document",
            content="Content",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/analyze",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyze_document_public_allowed(self, client, auth_headers, created_admin, db_session):
        """Test analyzing public document by another user"""
        doc = Document(
            owner_id=created_admin.id,
            title="Public Document",
            content="Content",
            is_public=True,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/analyze",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_202_ACCEPTED


class TestGetDocumentAnalysis:
    """Tests for getting document analysis results"""

    def test_get_analysis_success(self, client, auth_headers, created_user, db_session):
        """Test getting analysis results"""
        # Create document
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        # Create analysis manually
        text_hash = DocumentAnalysis.compute_text_hash("Test content")
        analysis = DocumentAnalysis(
            document_id=doc.id,
            text_hash=text_hash,
            analysis={
                "suggestions": [
                    {
                        "start": 0,
                        "end": 4,
                        "error_type": "SPELLING",
                        "suggestion": "Test",
                        "rule_id": "TEST_RULE",
                        "confidence": 0.9,
                    }
                ],
                "stats": {
                    "total_suggestions": 1,
                    "spelling_errors": 1,
                    "grammar_errors": 0,
                    "style_issues": 0,
                },
                "text_length": 12,
                "text_hash": text_hash,
            },
        )
        db_session.add(analysis)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}/analysis",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["document_id"] == str(doc.id)
        assert "suggestions" in data
        assert "stats" in data
        assert data["stats"]["total_suggestions"] == 1
        assert len(data["suggestions"]) == 1

    def test_get_analysis_not_found(self, client, auth_headers, created_user, db_session):
        """Test getting analysis for document without analysis"""
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}/analysis",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_analysis_document_not_found(self, client, auth_headers):
        """Test getting analysis for non-existent document"""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/documents/{fake_id}/analysis",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_analysis_unauthorized(self, client, created_user, db_session):
        """Test getting analysis without authentication"""
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(f"/api/v1/documents/{doc.id}/analysis")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_analysis_by_other_user_denied(self, client, auth_headers, created_admin, db_session):
        """Test getting analysis of private document by another user"""
        doc = Document(
            owner_id=created_admin.id,
            title="Admin's Document",
            content="Content",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}/analysis",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAnalysisCaching:
    """Tests for analysis caching based on text hash"""

    def test_analysis_caching_same_text(self, client, auth_headers, created_user, db_session):
        """Test that analysis is cached for same text"""
        # Create document
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Same text content",
        )
        db_session.add(doc)
        db_session.commit()
        
        # Create first analysis
        text_hash = DocumentAnalysis.compute_text_hash("Same text content")
        analysis1 = DocumentAnalysis(
            document_id=doc.id,
            text_hash=text_hash,
            analysis={
                "suggestions": [],
                "stats": {"total_suggestions": 0, "spelling_errors": 0, "grammar_errors": 0, "style_issues": 0},
                "text_length": 18,
                "text_hash": text_hash,
            },
        )
        db_session.add(analysis1)
        db_session.commit()
        
        # Request analysis again (should use cached)
        # Note: In real scenario, Celery task would check cache
        # Here we just verify the hash matching logic
        new_hash = DocumentAnalysis.compute_text_hash("Same text content")
        assert new_hash == text_hash
        
        # Verify analysis exists
        existing = db_session.query(DocumentAnalysis).filter(
            DocumentAnalysis.document_id == doc.id,
            DocumentAnalysis.text_hash == text_hash,
        ).first()
        assert existing is not None

    def test_analysis_different_text(self, client, auth_headers, created_user, db_session):
        """Test that different text produces different hash"""
        text1 = "First text"
        text2 = "Second text"
        
        hash1 = DocumentAnalysis.compute_text_hash(text1)
        hash2 = DocumentAnalysis.compute_text_hash(text2)
        
        assert hash1 != hash2

