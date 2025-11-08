import pytest
import os
from pathlib import Path
from fastapi import status

from app.models.document import Document
from app.models.reference import Reference
from app.models.export_job import ExportJob, ExportJobStatus
from app.services.export_service import export_service
from app.tasks.export_tasks import export_document


class TestExportService:
    """Tests for export service"""

    def test_generate_filename(self):
        """Test filename generation"""
        filename = export_service.generate_filename("test-doc-id", "pdf")
        assert filename.startswith("document_test-doc-id_")
        assert filename.endswith(".pdf")
        
        filename = export_service.generate_filename("test-doc-id", "docx")
        assert filename.endswith(".docx")

    def test_get_file_path(self):
        """Test file path generation"""
        filename = "test_file.pdf"
        file_path = export_service.get_file_path(filename)
        assert isinstance(file_path, Path)
        assert file_path.name == filename

    @pytest.mark.skipif(not export_service._check_docx_available(), reason="python-docx not available")
    def test_export_to_docx_basic(self, tmp_path):
        """Test basic DOCX export"""
        document = {
            "title": "Test Document",
            "content": "This is a test document.\n\nWith multiple paragraphs.",
        }
        references = [
            {
                "authors": ["Smith, J."],
                "year": 2020,
                "title": "Test Book",
                "type": "book",
            }
        ]
        options = {"include_stats": False}
        
        output_path = tmp_path / "test.docx"
        result = export_service.export_to_docx(document, references, options, str(output_path))
        
        assert Path(result).exists()
        assert output_path.exists()

    @pytest.mark.skipif(not hasattr(export_service, '_check_pdf_available') or not export_service._check_pdf_available(), reason="reportlab not available")
    def test_export_to_pdf_basic(self, tmp_path):
        """Test basic PDF export"""
        document = {
            "title": "Test Document",
            "content": "This is a test document.\n\nWith multiple paragraphs.",
        }
        references = [
            {
                "authors": ["Smith, J."],
                "year": 2020,
                "title": "Test Book",
                "type": "book",
            }
        ]
        options = {"include_stats": False}
        
        output_path = tmp_path / "test.pdf"
        result = export_service.export_to_pdf(document, references, options, str(output_path))
        
        assert Path(result).exists()
        assert output_path.exists()

    def test_calculate_stats(self):
        """Test statistics calculation"""
        content = "This is a test document with multiple words and sentences. It has some content."
        stats = export_service._calculate_stats(content)
        
        assert "Word Count" in stats
        assert "Character Count" in stats
        assert "Paragraph Count" in stats
        assert stats["Word Count"] > 0


class TestExportEndpoints:
    """Tests for export endpoints"""

    def test_create_export_success(self, client, auth_headers, created_user, db_session):
        """Test successful export job creation"""
        # Create document
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/export",
            json={
                "format": "pdf",
                "include_stats": True,
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        
        assert "job_id" in data
        assert data["document_id"] == str(doc.id)
        assert data["status"] == "queued"

    def test_create_export_invalid_format(self, client, auth_headers, created_user, db_session):
        """Test export with invalid format"""
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/export",
            json={
                "format": "invalid",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_export_unauthorized(self, client, created_user, db_session):
        """Test export without authentication"""
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/export",
            json={"format": "pdf"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_export_job(self, client, auth_headers, created_user, db_session):
        """Test getting export job status"""
        # Create document and job
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content",
        )
        db_session.add(doc)
        db_session.commit()
        
        job = ExportJob(
            document_id=doc.id,
            user_id=created_user.id,
            status=ExportJobStatus.QUEUED,
            export_format="pdf",
        )
        db_session.add(job)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/export_jobs/{job.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(job.id)
        assert data["status"] == "queued"

    def test_download_file_not_found(self, client, auth_headers):
        """Test downloading non-existent file"""
        response = client.get(
            "/api/v1/downloads/nonexistent.pdf",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_file_unauthorized(self, client, created_user, db_session):
        """Test downloading file without authentication"""
        response = client.get("/api/v1/downloads/test.pdf")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestExportTask:
    """Tests for export Celery task"""

    @pytest.mark.skipif(True, reason="Requires Celery worker running")
    def test_export_task_completes(self, created_user, db_session):
        """Test that export task completes successfully"""
        # Create document with references
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="Test content with references.",
        )
        db_session.add(doc)
        db_session.commit()
        
        ref = Reference(
            document_id=doc.id,
            ref_key="[Smith, 2020]",
            ref_text="Smith, J. (2020). Test book.",
            parsed={
                "authors": ["Smith, J."],
                "year": 2020,
                "title": "Test book",
                "type": "book",
            },
        )
        db_session.add(ref)
        db_session.commit()
        
        job = ExportJob(
            document_id=doc.id,
            user_id=created_user.id,
            status=ExportJobStatus.QUEUED,
            export_format="pdf",
            include_stats=False,
        )
        db_session.add(job)
        db_session.commit()
        
        # Run task (synchronously for testing)
        result = export_document(str(job.id))
        
        # Check result
        assert result["status"] == "completed"
        assert "filename" in result
        
        # Check job updated
        db_session.refresh(job)
        assert job.status == ExportJobStatus.DONE
        assert job.result_path is not None
        
        # Check file exists
        file_path = export_service.get_file_path(job.result_path)
        assert file_path.exists()

