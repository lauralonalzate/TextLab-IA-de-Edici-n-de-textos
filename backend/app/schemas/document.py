from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.models.user import UserRole


class DocumentCreate(BaseModel):
    """Schema for creating a document"""
    title: str = Field(..., min_length=1, max_length=255, description="Document title")
    content: Optional[str] = Field(None, description="Document content (Markdown/HTML)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata (JSON)")
    is_public: bool = Field(False, description="Whether the document is public")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My First Document",
                "content": "# Introduction\n\nThis is my document content.",
                "metadata": {
                    "language": "en",
                    "template": "article",
                    "word_count": 150
                },
                "is_public": False
            }
        }


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Document title")
    content: Optional[str] = Field(None, description="Document content (Markdown/HTML)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata (JSON)")
    is_public: Optional[bool] = Field(None, description="Whether the document is public")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Document Title",
                "content": "# Updated Content\n\nNew content here.",
                "metadata": {
                    "language": "es",
                    "word_count": 200
                },
                "is_public": True
            }
        }


class DocumentShare(BaseModel):
    """Schema for sharing a document"""
    is_public: Optional[bool] = Field(None, description="Make document public")
    share_with_roles: Optional[List[UserRole]] = Field(None, description="Share with specific roles")
    share_with_emails: Optional[List[str]] = Field(None, description="Share with specific email addresses")

    class Config:
        json_schema_extra = {
            "example": {
                "is_public": True,
                "share_with_roles": ["teacher", "researcher"],
                "share_with_emails": ["user@example.com"]
            }
        }


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: str
    owner_id: str
    title: str
    content: Optional[str]
    metadata: Optional[Dict[str, Any]]
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "owner_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "My Document",
                "content": "# Content\n\nDocument content here.",
                "metadata": {"language": "en"},
                "is_public": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

    @classmethod
    def from_document(cls, document):
        """Create DocumentResponse from Document model"""
        return cls(
            id=str(document.id),
            owner_id=str(document.owner_id),
            title=document.title,
            content=document.content,
            metadata=document.metadata,
            is_public=document.is_public,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class DocumentVersionResponse(BaseModel):
    """Schema for document version response"""
    id: str
    document_id: str
    content: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_version(cls, version):
        """Create DocumentVersionResponse from DocumentVersion model"""
        return cls(
            id=str(version.id),
            document_id=str(version.document_id),
            content=version.content,
            created_at=version.created_at,
        )


class DocumentListResponse(BaseModel):
    """Schema for paginated document list response"""
    items: List[DocumentResponse]
    total: int
    page: int
    per_page: int
    pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "owner_id": "123e4567-e89b-12d3-a456-426614174001",
                        "title": "Document 1",
                        "content": "Content 1",
                        "metadata": {},
                        "is_public": False,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 10,
                "page": 1,
                "per_page": 10,
                "pages": 1
            }
        }

