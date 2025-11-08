import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Citation(Base):
    __tablename__ = "citations"

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
    citation_text = Column(Text, nullable=False)
    citation_key = Column(String(255), nullable=False)  # e.g., "[Smith, 2020]"
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
    document = relationship("Document", back_populates="citations")

    # Indexes
    __table_args__ = (
        Index("idx_citations_document_id", "document_id"),
        Index("idx_citations_citation_key", "citation_key"),
    )

    def __repr__(self):
        return f"<Citation(id={self.id}, citation_key={self.citation_key}, document_id={self.document_id})>"

