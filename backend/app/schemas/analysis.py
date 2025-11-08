from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Suggestion(BaseModel):
    """Schema for a text correction suggestion"""
    start: int = Field(..., description="Start position of the error in text")
    end: int = Field(..., description="End position of the error in text")
    error_type: str = Field(..., description="Type of error: SPELLING, GRAMMAR, STYLE")
    suggestion: str = Field(..., description="Suggested correction")
    rule_id: Optional[str] = Field(None, description="Rule ID that triggered this suggestion")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence level (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "start": 10,
                "end": 20,
                "error_type": "SPELLING",
                "suggestion": "tecnología",
                "rule_id": "SPELLING_RULE_1",
                "confidence": 0.9
            }
        }


class AnalysisStats(BaseModel):
    """Schema for analysis statistics"""
    total_suggestions: int
    spelling_errors: int
    grammar_errors: int
    style_issues: int

    class Config:
        json_schema_extra = {
            "example": {
                "total_suggestions": 5,
                "spelling_errors": 2,
                "grammar_errors": 2,
                "style_issues": 1
            }
        }


class AnalysisResponse(BaseModel):
    """Schema for analysis response"""
    id: str
    document_id: str
    suggestions: List[Suggestion]
    stats: AnalysisStats
    text_length: int
    text_hash: str
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "document_id": "123e4567-e89b-12d3-a456-426614174001",
                "suggestions": [
                    {
                        "start": 10,
                        "end": 20,
                        "error_type": "SPELLING",
                        "suggestion": "tecnología",
                        "rule_id": "SPELLING_RULE_1",
                        "confidence": 0.9
                    }
                ],
                "stats": {
                    "total_suggestions": 1,
                    "spelling_errors": 1,
                    "grammar_errors": 0,
                    "style_issues": 0
                },
                "text_length": 100,
                "text_hash": "abc123...",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

    @classmethod
    def from_analysis(cls, analysis):
        """Create AnalysisResponse from DocumentAnalysis model"""
        analysis_data = analysis.analysis
        return cls(
            id=str(analysis.id),
            document_id=str(analysis.document_id),
            suggestions=analysis_data.get("suggestions", []),
            stats=AnalysisStats(**analysis_data.get("stats", {})),
            text_length=analysis_data.get("text_length", 0),
            text_hash=analysis_data.get("text_hash", ""),
            created_at=analysis.created_at,
        )


class AnalyzeRequest(BaseModel):
    """Schema for analyze request (optional parameters)"""
    language: Optional[str] = Field("es-ES", description="Language code for analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "language": "es-ES"
            }
        }


class AnalyzeResponse(BaseModel):
    """Schema for analyze task response"""
    job_id: str
    document_id: str
    status: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "abc123-def456-ghi789",
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "queued",
                "message": "Analysis task queued successfully"
            }
        }

