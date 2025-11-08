import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, ForeignKey, DateTime, Enum as SQLEnum, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ExportJobStatus(str, PyEnum):
    """Export job status enumeration"""
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class ExportJob(Base):
    __tablename__ = "export_jobs"

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
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        SQLEnum(ExportJobStatus, name="export_job_status"),
        nullable=False,
        default=ExportJobStatus.QUEUED,
        index=True,
    )
    result_path = Column(String(500), nullable=True)
    export_format = Column(String(10), nullable=True, default="pdf")
    include_stats = Column(Boolean, nullable=True, default=False)
    template_id = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="export_jobs")
    user = relationship("User", back_populates="export_jobs")

    # Indexes
    __table_args__ = (
        Index("idx_export_jobs_document_id", "document_id"),
        Index("idx_export_jobs_user_id", "user_id"),
        Index("idx_export_jobs_status", "status"),
        Index("idx_export_jobs_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<ExportJob(id={self.id}, status={self.status}, document_id={self.document_id})>"

