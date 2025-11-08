import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)  # Markdown/HTML content
    metadata = Column(JSONB, nullable=True)  # Language, template, stats, etc.
    is_public = Column(Boolean, default=False, nullable=False)
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
    owner = relationship("User", back_populates="documents")
    citations = relationship(
        "Citation",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    references = relationship(
        "Reference",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    export_jobs = relationship(
        "ExportJob",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    versions = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.created_at.desc()",
    )
    analyses = relationship(
        "DocumentAnalysis",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentAnalysis.created_at.desc()",
    )
    stats_history = relationship(
        "DocumentStats",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentStats.created_at.desc()",
    )

    # Indexes
    __table_args__ = (
        Index("idx_documents_owner_id", "owner_id"),
        Index("idx_documents_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, owner_id={self.owner_id})>"

