import uuid
from datetime import datetime

from sqlalchemy import Column, Text, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class DocumentVersion(Base):
    __tablename__ = "documents_versions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column(Text, nullable=True)  # Snapshot of content at this version
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    document = relationship("Document", back_populates="versions")

    # Indexes
    __table_args__ = (
        Index("idx_document_versions_document_id", "document_id"),
        Index("idx_document_versions_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<DocumentVersion(id={self.id}, document_id={self.document_id}, created_at={self.created_at})>"

