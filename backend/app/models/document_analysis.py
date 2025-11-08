import uuid
import hashlib
from datetime import datetime

from sqlalchemy import Column, Text, ForeignKey, DateTime, String, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class DocumentAnalysis(Base):
    __tablename__ = "document_analysis"

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
    text_hash = Column(
        String(64),
        nullable=False,
        index=True,
    )  # SHA-256 hash of the analyzed text
    analysis = Column(
        JSONB,
        nullable=False,
    )  # Analysis results: suggestions, stats, etc.
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    document = relationship("Document", back_populates="analyses")

    # Indexes
    __table_args__ = (
        Index("idx_document_analysis_document_id", "document_id"),
        Index("idx_document_analysis_text_hash", "text_hash"),
        Index("idx_document_analysis_created_at", "created_at"),
        Index("idx_document_analysis_document_hash", "document_id", "text_hash"),
    )

    @staticmethod
    def compute_text_hash(text: str) -> str:
        """Compute SHA-256 hash of text"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def __repr__(self):
        return f"<DocumentAnalysis(id={self.id}, document_id={self.document_id}, created_at={self.created_at})>"

