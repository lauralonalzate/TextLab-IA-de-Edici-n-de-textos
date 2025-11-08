import pytest
from fastapi import status
import uuid

from app.models.document import Document
from app.models.document_stats import DocumentStats
from app.services.stats_service import stats_service
from app.tasks.stats_tasks import calculate_document_stats


class TestStatsService:
    """Tests for statistics service"""

    def test_calculate_stats_basic(self):
        """Test basic statistics calculation"""
        content = "This is a test document. It has multiple sentences. And paragraphs.\n\nThis is another paragraph."
        stats = stats_service.calculate_stats(content)
        
        assert stats["word_count"] == 15
        assert stats["character_count"] > 0
        assert stats["paragraph_count"] == 2
        assert stats["sentence_count"] >= 3
        assert "reading_time_minutes" in stats
        assert "reading_time_display" in stats

    def test_calculate_stats_reading_time(self):
        """Test reading time calculation (200 wpm)"""
        # 200 words = 1 minute
        content = "word " * 200
        stats = stats_service.calculate_stats(content)
        
        assert stats["word_count"] == 200
        assert stats["reading_time_minutes"] == 1.0
        assert "minute" in stats["reading_time_display"].lower()

    def test_calculate_stats_empty(self):
        """Test statistics for empty content"""
        stats = stats_service.calculate_stats("")
        
        assert stats["word_count"] == 0
        assert stats["character_count"] == 0
        assert stats["paragraph_count"] == 0
        assert stats["reading_time_minutes"] == 0

    def test_calculate_stats_readability(self):
        """Test readability metrics calculation"""
        content = "This is a simple sentence. It has basic words. The text is easy to read."
        stats = stats_service.calculate_stats(content)
        
        # Readability metrics may be None if textstat not available
        assert "flesch_reading_ease" in stats
        assert "flesch_kincaid_grade" in stats
        # If textstat is available, values should be numbers
        if stats["flesch_reading_ease"] is not None:
            assert isinstance(stats["flesch_reading_ease"], (int, float))

    def test_calculate_stats_averages(self):
        """Test average calculations"""
        content = "Sentence one. Sentence two. Sentence three.\n\nParagraph two."
        stats = stats_service.calculate_stats(content)
        
        assert "average_words_per_sentence" in stats
        assert "average_sentences_per_paragraph" in stats
        assert stats["average_words_per_sentence"] > 0
        assert stats["average_sentences_per_paragraph"] > 0


class TestStatsEndpoints:
    """Tests for statistics endpoints"""

    def test_calculate_stats_success(self, client, auth_headers, created_user, db_session):
        """Test successful statistics calculation"""
        # Create document with content
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="This is a test document with some content. It has multiple sentences.",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/stats",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        
        assert "id" in data
        assert data["document_id"] == str(doc.id)
        assert "stats" in data
        assert data["stats"]["word_count"] > 0

    def test_get_stats_success(self, client, auth_headers, created_user, db_session):
        """Test getting document statistics"""
        # Create document
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        # Create stats manually
        stats = DocumentStats(
            document_id=doc.id,
            stats={
                "word_count": 100,
                "character_count": 500,
                "reading_time_minutes": 0.5,
            },
        )
        db_session.add(stats)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}/stats",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["document_id"] == str(doc.id)
        assert data["stats"]["word_count"] == 100

    def test_get_stats_not_found(self, client, auth_headers, created_user, db_session):
        """Test getting stats for document without stats"""
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}/stats",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_calculate_stats_unauthorized(self, client, created_user, db_session):
        """Test calculating stats without authentication"""
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(f"/api/v1/documents/{doc.id}/stats")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_stats_by_other_user_denied(self, client, auth_headers, created_admin, db_session):
        """Test getting stats of private document by another user"""
        doc = Document(
            owner_id=created_admin.id,
            title="Admin's Document",
            content="Content",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}/stats",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestStatsOverview:
    """Tests for statistics overview endpoint"""

    def test_stats_overview_admin(self, client, admin_auth_headers, created_user, db_session):
        """Test stats overview with admin role"""
        # Create some documents
        for i in range(5):
            doc = Document(
                owner_id=created_user.id,
                title=f"Document {i}",
                content=f"Content {i} " * 10,  # ~10 words each
            )
            db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            "/api/v1/stats/overview",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "total_documents" in data
        assert "total_users" in data
        assert "average_words_per_document" in data
        assert "documents_by_user" in data
        assert "recent_activity" in data
        assert data["total_documents"] >= 5

    def test_stats_overview_teacher(self, client, teacher_auth_headers):
        """Test stats overview with teacher role"""
        response = client.get(
            "/api/v1/stats/overview",
            headers=teacher_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_stats_overview_student_denied(self, client, auth_headers):
        """Test stats overview with student role (should fail)"""
        response = client.get(
            "/api/v1/stats/overview",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_stats_overview_pagination(self, client, admin_auth_headers, created_user, db_session):
        """Test stats overview with pagination"""
        # Create multiple users and documents
        for i in range(15):
            doc = Document(
                owner_id=created_user.id,
                title=f"Document {i}",
                content="Content",
            )
            db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            "/api/v1/stats/overview?page=1&per_page=10",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["documents_by_user"]) <= 10


class TestStatsTask:
    """Tests for statistics Celery task"""

    @pytest.mark.skipif(True, reason="Requires Celery worker running")
    def test_calculate_stats_task_completes(self, created_user, db_session):
        """Test that stats calculation task completes successfully"""
        # Create document
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="This is a test document with content.",
        )
        db_session.add(doc)
        db_session.commit()
        
        # Run task (synchronously for testing)
        result = calculate_document_stats(str(doc.id))
        
        # Check result
        assert result["status"] == "completed"
        assert "stats" in result
        
        # Check stats saved to database
        stats = db_session.query(DocumentStats).filter(
            DocumentStats.document_id == doc.id
        ).first()
        assert stats is not None
        assert stats.stats["word_count"] > 0

