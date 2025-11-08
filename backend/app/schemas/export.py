from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.export_job import ExportJobStatus


class ExportRequest(BaseModel):
    """Schema for export request"""
    format: str = Field("pdf", description="Export format: pdf or docx")
    include_stats: bool = Field(False, description="Include document statistics")
    template_id: Optional[str] = Field(None, description="Template ID to use")

    class Config:
        json_schema_extra = {
            "example": {
                "format": "pdf",
                "include_stats": True,
                "template_id": "institutional_template_1"
            }
        }


class ExportResponse(BaseModel):
    """Schema for export job response"""
    job_id: str
    document_id: str
    status: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "document_id": "123e4567-e89b-12d3-a456-426614174001",
                "status": "queued",
                "message": "Export job queued successfully"
            }
        }


class ExportJobResponse(BaseModel):
    """Schema for export job status response"""
    id: str
    document_id: str
    user_id: str
    status: ExportJobStatus
    result_path: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "document_id": "123e4567-e89b-12d3-a456-426614174001",
                "user_id": "123e4567-e89b-12d3-a456-426614174002",
                "status": "done",
                "result_path": "document_xxx_20240101_120000.pdf",
                "created_at": "2024-01-01T12:00:00Z",
                "finished_at": "2024-01-01T12:01:00Z"
            }
        }

    @classmethod
    def from_job(cls, job):
        """Create ExportJobResponse from ExportJob model"""
        return cls(
            id=str(job.id),
            document_id=str(job.document_id),
            user_id=str(job.user_id),
            status=job.status,
            result_path=job.result_path,
            created_at=job.created_at,
            finished_at=job.finished_at,
        )

