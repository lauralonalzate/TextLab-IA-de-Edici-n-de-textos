import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Reference(Base):
    __tablename__ = "references"

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
    ref_text = Column(Text, nullable=False)
    ref_key = Column(String(255), nullable=False)  # Maps to citation_key
    parsed = Column(
        JSONB,
        nullable=True,
    )  # Parsed fields: authors, year, title, type, doi, url
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    document = relationship("Document", back_populates="references")

    # Indexes
    __table_args__ = (
        Index("idx_references_document_id", "document_id"),
        Index("idx_references_ref_key", "ref_key"),
    )

    def __repr__(self):
        return f"<Reference(id={self.id}, ref_key={self.ref_key}, document_id={self.document_id})>"

