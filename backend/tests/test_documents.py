import pytest
from fastapi import status
import uuid

from app.models.document import Document
from app.models.document_version import DocumentVersion


class TestCreateDocument:
    """Tests for creating documents"""

    def test_create_document_success(self, client, auth_headers):
        """Test successful document creation"""
        response = client.post(
            "/api/v1/documents",
            json={
                "title": "Test Document",
                "content": "# Test Content\n\nThis is test content.",
                "metadata": {"language": "en"},
                "is_public": False,
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["title"] == "Test Document"
        assert data["content"] == "# Test Content\n\nThis is test content."
        assert data["metadata"] == {"language": "en"}
        assert data["is_public"] == False
        assert "id" in data
        assert "owner_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_document_minimal(self, client, auth_headers):
        """Test creating document with minimal fields"""
        response = client.post(
            "/api/v1/documents",
            json={
                "title": "Minimal Document",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["title"] == "Minimal Document"
        assert data["content"] is None
        assert data["is_public"] == False

    def test_create_document_unauthorized(self, client):
        """Test creating document without authentication"""
        response = client.post(
            "/api/v1/documents",
            json={
                "title": "Test Document",
                "content": "Content",
            },
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_document_invalid_title(self, client, auth_headers):
        """Test creating document with invalid title"""
        response = client.post(
            "/api/v1/documents",
            json={
                "title": "",  # Empty title
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListDocuments:
    """Tests for listing documents"""

    def test_list_documents_empty(self, client, auth_headers):
        """Test listing documents when user has none"""
        response = client.get(
            "/api/v1/documents",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert data["pages"] == 0

    def test_list_documents_with_pagination(self, client, auth_headers, created_user, db_session):
        """Test listing documents with pagination"""
        # Create multiple documents
        for i in range(15):
            doc = Document(
                owner_id=created_user.id,
                title=f"Document {i+1}",
                content=f"Content {i+1}",
            )
            db_session.add(doc)
        db_session.commit()
        
        # First page
        response = client.get(
            "/api/v1/documents?page=1&per_page=10",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert data["pages"] == 2
        
        # Second page
        response = client.get(
            "/api/v1/documents?page=2&per_page=10",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) == 5
        assert data["page"] == 2

    def test_list_documents_search(self, client, auth_headers, created_user, db_session):
        """Test searching documents by title"""
        # Create documents with different titles
        doc1 = Document(
            owner_id=created_user.id,
            title="Python Tutorial",
            content="Content 1",
        )
        doc2 = Document(
            owner_id=created_user.id,
            title="JavaScript Guide",
            content="Content 2",
        )
        doc3 = Document(
            owner_id=created_user.id,
            title="Python Advanced",
            content="Content 3",
        )
        db_session.add_all([doc1, doc2, doc3])
        db_session.commit()
        
        # Search for "Python"
        response = client.get(
            "/api/v1/documents?q=Python",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 2
        assert all("Python" in item["title"] for item in data["items"])

    def test_list_documents_includes_public(self, client, auth_headers, created_user, created_admin, db_session):
        """Test that public documents are included in list"""
        # Create user's own document
        own_doc = Document(
            owner_id=created_user.id,
            title="My Document",
            content="My content",
            is_public=False,
        )
        # Create public document by another user
        public_doc = Document(
            owner_id=created_admin.id,
            title="Public Document",
            content="Public content",
            is_public=True,
        )
        db_session.add_all([own_doc, public_doc])
        db_session.commit()
        
        response = client.get(
            "/api/v1/documents",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 2
        titles = [item["title"] for item in data["items"]]
        assert "My Document" in titles
        assert "Public Document" in titles

    def test_list_documents_unauthorized(self, client):
        """Test listing documents without authentication"""
        response = client.get("/api/v1/documents")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetDocument:
    """Tests for getting a single document"""

    def test_get_document_success(self, client, auth_headers, created_user, db_session):
        """Test getting own document"""
        doc = Document(
            owner_id=created_user.id,
            title="My Document",
            content="My content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["title"] == "My Document"
        assert data["content"] == "My content"
        assert str(data["id"]) == str(doc.id)

    def test_get_public_document(self, client, auth_headers, created_admin, db_session):
        """Test getting public document by another user"""
        doc = Document(
            owner_id=created_admin.id,
            title="Public Document",
            content="Public content",
            is_public=True,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["title"] == "Public Document"

    def test_get_private_document_denied(self, client, auth_headers, created_admin, db_session):
        """Test getting private document by another user (should fail)"""
        doc = Document(
            owner_id=created_admin.id,
            title="Private Document",
            content="Private content",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_document_not_found(self, client, auth_headers):
        """Test getting non-existent document"""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/documents/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_document_invalid_id(self, client, auth_headers):
        """Test getting document with invalid ID format"""
        response = client.get(
            "/api/v1/documents/invalid-id",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_document_unauthorized(self, client, created_user, db_session):
        """Test getting document without authentication"""
        doc = Document(
            owner_id=created_user.id,
            title="My Document",
            content="My content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(f"/api/v1/documents/{doc.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateDocument:
    """Tests for updating documents"""

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
            json={
                "title": "Updated Title",
                "content": "Updated content",
            },
            headers=auth_headers,
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
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            json={
                "title": "Updated Title",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["title"] == "Updated Title"
        assert data["content"] == "Original content"  # Unchanged
        assert data["is_public"] == False  # Unchanged

    def test_update_document_creates_version(self, client, auth_headers, created_user, db_session):
        """Test that updating document creates a version"""
        doc = Document(
            owner_id=created_user.id,
            title="Original Title",
            content="Original content",
        )
        db_session.add(doc)
        db_session.commit()
        
        # Update document
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            json={
                "content": "Updated content",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Check that version was created
        versions = db_session.query(DocumentVersion).filter(
            DocumentVersion.document_id == doc.id
        ).all()
        assert len(versions) == 1
        assert versions[0].content == "Original content"

    def test_update_document_by_other_user_denied(self, client, auth_headers, created_admin, db_session):
        """Test updating document by another user (should fail)"""
        doc = Document(
            owner_id=created_admin.id,
            title="Admin's Document",
            content="Admin content",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            json={
                "title": "Hacked Title",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_document_by_admin_allowed(self, client, admin_auth_headers, created_user, db_session):
        """Test that admin can update any document"""
        doc = Document(
            owner_id=created_user.id,
            title="User's Document",
            content="User content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            json={
                "title": "Updated by Admin",
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["title"] == "Updated by Admin"

    def test_update_document_not_found(self, client, auth_headers):
        """Test updating non-existent document"""
        fake_id = str(uuid.uuid4())
        response = client.put(
            f"/api/v1/documents/{fake_id}",
            json={"title": "New Title"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_document_unauthorized(self, client, created_user, db_session):
        """Test updating document without authentication"""
        doc = Document(
            owner_id=created_user.id,
            title="My Document",
            content="My content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            json={"title": "New Title"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteDocument:
    """Tests for deleting documents"""

    def test_delete_document_success(self, client, auth_headers, created_user, db_session):
        """Test successful document deletion"""
        doc = Document(
            owner_id=created_user.id,
            title="To Delete",
            content="Content",
        )
        db_session.add(doc)
        db_session.commit()
        doc_id = doc.id
        
        response = client.delete(
            f"/api/v1/documents/{doc_id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify document is deleted
        deleted_doc = db_session.query(Document).filter(Document.id == doc_id).first()
        assert deleted_doc is None

    def test_delete_document_by_other_user_denied(self, client, auth_headers, created_admin, db_session):
        """Test deleting document by another user (should fail)"""
        doc = Document(
            owner_id=created_admin.id,
            title="Admin's Document",
            content="Content",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/documents/{doc.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_document_by_admin_allowed(self, client, admin_auth_headers, created_user, db_session):
        """Test that admin can delete any document"""
        doc = Document(
            owner_id=created_user.id,
            title="User's Document",
            content="Content",
        )
        db_session.add(doc)
        db_session.commit()
        doc_id = doc.id
        
        response = client.delete(
            f"/api/v1/documents/{doc_id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_document_not_found(self, client, auth_headers):
        """Test deleting non-existent document"""
        fake_id = str(uuid.uuid4())
        response = client.delete(
            f"/api/v1/documents/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_document_unauthorized(self, client, created_user, db_session):
        """Test deleting document without authentication"""
        doc = Document(
            owner_id=created_user.id,
            title="My Document",
            content="Content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.delete(f"/api/v1/documents/{doc.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestShareDocument:
    """Tests for sharing documents"""

    def test_share_document_make_public(self, client, auth_headers, created_user, db_session):
        """Test making document public"""
        doc = Document(
            owner_id=created_user.id,
            title="Private Document",
            content="Content",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/share",
            json={"is_public": True},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["is_public"] == True

    def test_share_document_by_other_user_denied(self, client, auth_headers, created_admin, db_session):
        """Test sharing document by another user (should fail)"""
        doc = Document(
            owner_id=created_admin.id,
            title="Admin's Document",
            content="Content",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/share",
            json={"is_public": True},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_share_document_unauthorized(self, client, created_user, db_session):
        """Test sharing document without authentication"""
        doc = Document(
            owner_id=created_user.id,
            title="My Document",
            content="Content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/documents/{doc.id}/share",
            json={"is_public": True},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDocumentVersions:
    """Tests for document versions"""

    def test_get_document_versions(self, client, auth_headers, created_user, db_session):
        """Test getting document versions"""
        doc = Document(
            owner_id=created_user.id,
            title="Versioned Document",
            content="Version 1",
        )
        db_session.add(doc)
        db_session.commit()
        
        # Create versions manually
        version1 = DocumentVersion(
            document_id=doc.id,
            content="Version 1",
        )
        version2 = DocumentVersion(
            document_id=doc.id,
            content="Version 2",
        )
        db_session.add_all([version1, version2])
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}/versions",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data) == 2
        assert data[0]["content"] == "Version 2"  # Most recent first
        assert data[1]["content"] == "Version 1"

    def test_get_versions_by_other_user_denied(self, client, auth_headers, created_admin, db_session):
        """Test getting versions of document by another user (should fail)"""
        doc = Document(
            owner_id=created_admin.id,
            title="Admin's Document",
            content="Content",
            is_public=False,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/documents/{doc.id}/versions",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_versions_unauthorized(self, client, created_user, db_session):
        """Test getting versions without authentication"""
        doc = Document(
            owner_id=created_user.id,
            title="My Document",
            content="Content",
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.get(f"/api/v1/documents/{doc.id}/versions")
        assert response.status_code == status.HTTP_403_FORBIDDEN

