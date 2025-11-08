"""
Comprehensive CRUD tests for documents endpoint.
"""
import pytest
from fastapi import status
import uuid

from app.models.document import Document


class TestDocumentCRUD:
    """Tests for document CRUD operations"""

    def test_create_document_success(self, client, auth_headers):
        """Test successful document creation"""
        response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            json={
                "title": "Test Document",
                "content": "This is test content",
                "metadata": {"language": "en"},
                "is_public": False,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Test Document"
        assert data["content"] == "This is test content"
        assert "id" in data
        assert "created_at" in data

    def test_create_document_minimal(self, client, auth_headers):
        """Test document creation with minimal fields"""
        response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            json={"title": "Minimal Doc"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Minimal Doc"
        assert data["content"] is None or data["content"] == ""

    def test_get_document_success(self, client, auth_headers, created_user, db_session):
        """Test getting a document"""
        doc = Document(
            owner_id=created_user.id,
            title="Test Doc",
            content="Content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(doc.id)
        assert data["title"] == "Test Doc"

    def test_get_document_not_found(self, client, auth_headers):
        """Test getting non-existent document"""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/documents/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_document_unauthorized(self, client, created_user, db_session):
        """Test getting private document without auth"""
        doc = Document(
            owner_id=created_user.id,
            title="Private Doc",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(f"/api/v1/documents/{doc.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_documents(self, client, auth_headers, created_user, db_session):
        """Test listing user's documents"""
        # Create multiple documents
        for i in range(5):
            doc = Document(
                owner_id=created_user.id,
                title=f"Doc {i}",
            )
            db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            "/api/v1/documents",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 5
        assert data["total"] >= 5

    def test_list_documents_pagination(self, client, auth_headers, created_user, db_session):
        """Test document list pagination"""
        # Create multiple documents
        for i in range(15):
            doc = Document(
                owner_id=created_user.id,
                title=f"Doc {i}",
            )
            db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            "/api/v1/documents?page=1&per_page=10",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["per_page"] == 10

    def test_list_documents_search(self, client, auth_headers, created_user, db_session):
        """Test document list search"""
        doc1 = Document(
            owner_id=created_user.id,
            title="Python Tutorial",
        )
        doc2 = Document(
            owner_id=created_user.id,
            title="JavaScript Guide",
        )
        db_session.add_all([doc1, doc2])
        db_session.commit()
        
        response = client.get(
            "/api/v1/documents?q=Python",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any("Python" in item["title"] for item in data["items"])

    def test_update_document_success(self, client, auth_headers, created_user, db_session):
        """Test successful document update"""
        doc = Document(
            owner_id=created_user.id,
            title="Original Title",
            content="Original content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "content": "Updated content",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated content"

    def test_update_document_partial(self, client, auth_headers, created_user, db_session):
        """Test partial document update"""
        doc = Document(
            owner_id=created_user.id,
            title="Original Title",
            content="Original content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
            json={"title": "Updated Title"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        # Content should remain unchanged
        assert data["content"] == "Original content"

    def test_update_document_unauthorized(self, client, auth_headers, created_admin, db_session):
        """Test updating document by non-owner"""
        doc = Document(
            owner_id=created_admin.id,
            title="Admin's Doc",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
            json={"title": "Hacked Title"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_document_success(self, client, auth_headers, created_user, db_session):
        """Test successful document deletion"""
        doc = Document(
            owner_id=created_user.id,
            title="To Delete",
        )
        db_session.add(doc)
        db_session.commit()
        doc_id = doc.id
        
        response = client.delete(
            f"/api/v1/documents/{doc_id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        deleted_doc = db_session.query(Document).filter(Document.id == doc_id).first()
        assert deleted_doc is None

    def test_delete_document_unauthorized(self, client, auth_headers, created_admin, db_session):
        """Test deleting document by non-owner"""
        doc = Document(
            owner_id=created_admin.id,
            title="Admin's Doc",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_public_document(self, client, created_user, db_session):
        """Test getting public document without auth"""
        doc = Document(
            owner_id=created_user.id,
            title="Public Doc",
            is_public=True,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(f"/api/v1/documents/{doc.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_public"] is True

    def test_document_versioning_on_update(self, client, auth_headers, created_user, db_session):
        """Test that document versions are created on update"""
        from app.models.document_version import DocumentVersion
        
        doc = Document(
            owner_id=created_user.id,
            title="Versioned Doc",
            content="Version 1",
        )
        db_session.add(doc)
        db_session.commit()
        
        # Update document
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
            json={"content": "Version 2"},
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Check that version was created
        versions = db_session.query(DocumentVersion).filter(
            DocumentVersion.document_id == doc.id
        ).all()
        assert len(versions) >= 1

