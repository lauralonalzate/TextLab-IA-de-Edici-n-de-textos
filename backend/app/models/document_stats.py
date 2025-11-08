import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class DocumentStats(Base):
    __tablename__ = "document_stats"

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
    stats = Column(
        JSONB,
        nullable=False,
    )  # Statistics data: word_count, char_count, reading_time, etc.
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    document = relationship("Document", back_populates="stats_history")

    # Indexes
    __table_args__ = (
        Index("idx_document_stats_document_id", "document_id"),
        Index("idx_document_stats_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<DocumentStats(id={self.id}, document_id={self.document_id}, created_at={self.created_at})>"

