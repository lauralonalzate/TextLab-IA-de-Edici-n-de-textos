from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ParsedReference(BaseModel):
    """Schema for parsed reference data"""
    authors: List[str] = Field(default_factory=list, description="List of author names")
    year: Optional[int] = Field(None, description="Publication year")
    title: Optional[str] = Field(None, description="Title of work")
    source: Optional[str] = Field(None, description="Journal, publisher, or website name")
    type: str = Field("book", description="Type: book, article, web, chapter")
    doi: Optional[str] = Field(None, description="DOI if available")
    url: Optional[str] = Field(None, description="URL if available")
    publisher: Optional[str] = Field(None, description="Publisher name")
    volume: Optional[str] = Field(None, description="Volume number")
    issue: Optional[str] = Field(None, description="Issue number")
    pages: Optional[str] = Field(None, description="Page range")
    citation_key: Optional[str] = Field(None, description="Citation key for matching")
    ref_key: Optional[str] = Field(None, description="Reference key for matching")

    class Config:
        json_schema_extra = {
            "example": {
                "authors": ["Smith, J.", "Jones, M."],
                "year": 2020,
                "title": "Introduction to Psychology",
                "source": "American Journal of Psychology",
                "type": "article",
                "doi": "10.1234/example",
                "volume": "45",
                "issue": "3",
                "pages": "123-145"
            }
        }


class GenerateReferencesRequest(BaseModel):
    """Schema for generating reference list"""
    references: List[ParsedReference] = Field(..., description="List of parsed references")
    format: str = Field("text", description="Output format: text, html, latex")

    class Config:
        json_schema_extra = {
            "example": {
                "references": [
                    {
                        "authors": ["Smith, J."],
                        "year": 2020,
                        "title": "Introduction to Psychology",
                        "type": "article"
                    }
                ],
                "format": "text"
            }
        }


class GenerateReferencesResponse(BaseModel):
    """Schema for reference list response"""
    reference_list: str = Field(..., description="Formatted reference list")
    format: str = Field(..., description="Output format used")

    class Config:
        json_schema_extra = {
            "example": {
                "reference_list": "\tSmith, J. (2020). Introduction to Psychology. American Journal of Psychology, 45(3), 123-145.",
                "format": "text"
            }
        }


class ParseReferenceRequest(BaseModel):
    """Schema for parsing raw reference text"""
    raw_text: str = Field(..., description="Raw reference text to parse")

    class Config:
        json_schema_extra = {
            "example": {
                "raw_text": "Smith, J., & Jones, M. (2020). Introduction to Psychology. American Journal of Psychology, 45(3), 123-145. https://doi.org/10.1234/example"
            }
        }


class ParseReferenceResponse(BaseModel):
    """Schema for parsed reference response"""
    parsed: ParsedReference = Field(..., description="Parsed reference data")

    class Config:
        json_schema_extra = {
            "example": {
                "parsed": {
                    "authors": ["Smith, J.", "Jones, M."],
                    "year": 2020,
                    "title": "Introduction to Psychology",
                    "source": "American Journal of Psychology",
                    "type": "article",
                    "doi": "10.1234/example",
                    "volume": "45",
                    "issue": "3",
                    "pages": "123-145"
                }
            }
        }


class ValidationIssue(BaseModel):
    """Schema for validation issue"""
    citation_key: Optional[str] = None
    ref_key: Optional[str] = None
    citation_text: Optional[str] = None
    ref_text: Optional[str] = None
    citation_authors: Optional[List[str]] = None
    reference_authors: Optional[List[str]] = None
    citation_year: Optional[int] = None
    reference_year: Optional[int] = None
    issue: str = Field(..., description="Description of the issue")


class ValidationResponse(BaseModel):
    """Schema for coherence validation response"""
    citations_without_reference: List[ValidationIssue] = Field(
        default_factory=list,
        description="Citations that don't have a matching reference"
    )
    references_without_citations: List[ValidationIssue] = Field(
        default_factory=list,
        description="References that don't have a matching citation"
    )
    imperfect_matches: List[ValidationIssue] = Field(
        default_factory=list,
        description="Citations and references with matching keys but mismatched data"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "citations_without_reference": [
                    {
                        "citation_key": "[Smith, 2020]",
                        "citation_text": "Smith (2020) states...",
                        "issue": "No matching reference found"
                    }
                ],
                "references_without_citations": [
                    {
                        "ref_key": "[Jones, 2019]",
                        "ref_text": "Jones, M. (2019). Example book. Publisher.",
                        "issue": "No matching citation found"
                    }
                ],
                "imperfect_matches": [
                    {
                        "citation_key": "[Smith, 2020]",
                        "ref_key": "[Smith, 2020]",
                        "citation_authors": ["Smith, J."],
                        "reference_authors": ["Smith, J.", "Jones, M."],
                        "citation_year": 2020,
                        "reference_year": 2020,
                        "issue": "Authors or year mismatch between citation and reference"
                    }
                ]
            }
        }

