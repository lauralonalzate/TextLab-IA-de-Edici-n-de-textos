from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class DocumentStatsResponse(BaseModel):
    """Schema for document statistics response"""
    id: str
    document_id: str
    stats: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "document_id": "123e4567-e89b-12d3-a456-426614174001",
                "stats": {
                    "word_count": 1500,
                    "character_count": 8500,
                    "paragraph_count": 10,
                    "reading_time_minutes": 7.5,
                    "reading_time_display": "7 minutes",
                    "flesch_reading_ease": 65.5,
                    "flesch_kincaid_grade": 8.2
                },
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

    @classmethod
    def from_stats(cls, stats):
        """Create DocumentStatsResponse from DocumentStats model"""
        return cls(
            id=str(stats.id),
            document_id=str(stats.document_id),
            stats=stats.stats,
            created_at=stats.created_at,
        )


class StatsOverviewResponse(BaseModel):
    """Schema for statistics overview (admin/teacher)"""
    total_documents: int
    total_users: int
    average_words_per_document: float
    total_words: int
    documents_by_user: List[Dict[str, Any]]
    recent_activity: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "total_documents": 100,
                "total_users": 25,
                "average_words_per_document": 1250.5,
                "total_words": 125050,
                "documents_by_user": [
                    {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_email": "user@example.com",
                        "document_count": 10,
                        "total_words": 15000
                    }
                ],
                "recent_activity": {
                    "documents_created_last_7_days": 15,
                    "documents_created_last_30_days": 50
                }
            }
        }

