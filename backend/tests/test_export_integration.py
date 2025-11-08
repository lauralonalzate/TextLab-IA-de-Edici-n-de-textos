"""
Integration/smoke tests for export functionality.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.export_service import export_service
from app.models.document import Document
from app.models.reference import Reference


@pytest.mark.integration
class TestExportIntegration:
    """Integration tests for export service"""

    def test_export_to_docx_creates_file(self, created_user, db_session, tmp_path):
        """Test that DOCX export creates a file"""
        # Create document with content
        doc = Document(
            owner_id=created_user.id,
            title="Test Document",
            content="This is a test document with some content.",
        )
        db_session.add(doc)
        db_session.commit()
        
        # Create references
        ref = Reference(
            document_id=doc.id,
            ref_key="Smith2020",
            ref_text="Smith, J. (2020). Test Book. Publisher.",
            parsed={
                "authors": [{"first": "J", "last": "Smith"}],
                "year": 2020,
                "title": "Test Book",
                "publisher": "Publisher",
                "type": "book",
            },
        )
        db_session.add(ref)
        db_session.commit()
        
        # Export to DOCX
        output_path = tmp_path / "test_export.docx"
        result_path = export_service.export_to_docx(
            document=doc,
            references=[ref],
            output_path=str(output_path),
            include_stats=False,
        )
        
        # Verify file was created
        assert Path(result_path).exists()
        assert output_path.exists()
        assert output_path.suffix == ".docx"

    def test_export_to_pdf_creates_file(self, created_user, db_session, tmp_path):
        """Test that PDF export creates a file"""
        # Create document
        doc = Document(
            owner_id=created_user.id,
            title="Test PDF Document",
            content="This is content for PDF export.",
        )
        db_session.add(doc)
        db_session.commit()
        
        # Export to PDF
        output_path = tmp_path / "test_export.pdf"
        result_path = export_service.export_to_pdf(
            document=doc,
            references=[],
            output_path=str(output_path),
            include_stats=False,
        )
        
        # Verify file was created
        assert Path(result_path).exists()
        assert output_path.exists()
        assert output_path.suffix == ".pdf"

    def test_export_includes_references(self, created_user, db_session, tmp_path):
        """Test that exported document includes references"""
        doc = Document(
            owner_id=created_user.id,
            title="Document with References",
            content="This document cites Smith (2020).",
        )
        db_session.add(doc)
        db_session.commit()
        
        ref = Reference(
            document_id=doc.id,
            ref_key="Smith2020",
            ref_text="Smith, J. (2020). Test Book.",
            parsed={
                "authors": [{"first": "J", "last": "Smith"}],
                "year": 2020,
                "title": "Test Book",
                "type": "book",
            },
        )
        db_session.add(ref)
        db_session.commit()
        
        # Export
        output_path = tmp_path / "test_with_refs.docx"
        export_service.export_to_docx(
            document=doc,
            references=[ref],
            output_path=str(output_path),
            include_stats=False,
        )
        
        # Basic file check (full content verification would require docx parsing)
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_with_stats(self, created_user, db_session, tmp_path):
        """Test export with statistics included"""
        doc = Document(
            owner_id=created_user.id,
            title="Document with Stats",
            content="This is a test document. " * 10,  # Multiple sentences
        )
        db_session.add(doc)
        db_session.commit()
        
        output_path = tmp_path / "test_with_stats.docx"
        export_service.export_to_docx(
            document=doc,
            references=[],
            output_path=str(output_path),
            include_stats=True,
        )
        
        # Verify file was created
        assert output_path.exists()

    @pytest.mark.slow
    def test_export_large_document(self, created_user, db_session, tmp_path):
        """Test export of large document"""
        # Create large document
        large_content = "This is a sentence. " * 1000
        doc = Document(
            owner_id=created_user.id,
            title="Large Document",
            content=large_content,
        )
        db_session.add(doc)
        db_session.commit()
        
        output_path = tmp_path / "large_doc.docx"
        result_path = export_service.export_to_docx(
            document=doc,
            references=[],
            output_path=str(output_path),
            include_stats=False,
        )
        
        assert Path(result_path).exists()
        assert output_path.stat().st_size > 1000  # Should be substantial

