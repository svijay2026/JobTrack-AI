from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MatchRequest(BaseModel):
    """Schema for requesting an AI match evaluation."""
    resume_id: Optional[int] = Field(
        None,
        description="ID of specific resume to evaluate. If omitted, the user's primary resume is used.",
    )
    job_id: Optional[int] = Field(
        None,
        description="ID of existing tracked job application to evaluate against.",
    )
    job_description: Optional[str] = Field(
        None,
        description="Pasted job posting description text (required if job_id is not provided).",
    )
    job_title: Optional[str] = Field(
        None,
        description="Optional job title for context.",
    )
    company_name: Optional[str] = Field(
        None,
        description="Optional company name for context.",
    )


class MatchScoreBreakdown(BaseModel):
    """Breakdown of individual scoring dimensions."""
    overall_score: float
    skill_score: float
    semantic_score: float
    experience_score: float


class MatchResultResponse(BaseModel):
    """Detailed response schema representing AI match analysis output."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    resume_id: int
    job_id: Optional[int] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    match_score: float
    skill_match_score: float
    semantic_score: float
    experience_score: float
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MatchHistoryItem(BaseModel):
    """Lightweight schema for viewing past match evaluations."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    job_id: Optional[int] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    match_score: float
    created_at: datetime


class CoverLetterRequest(BaseModel):
    """Schema for generating a tailored AI cover letter."""
    resume_id: Optional[int] = Field(None, description="Optional resume ID. Defaults to primary resume.")
    company_name: str = Field(..., description="Target company name.")
    job_title: str = Field(..., description="Target job title.")
    job_description: str = Field(..., description="Job posting text.")
    tone: Optional[str] = Field("professional", description="Tone of cover letter: professional, enthusiastic, concise.")


class CoverLetterResponse(BaseModel):
    """Response schema containing the generated cover letter."""
    company_name: str
    job_title: str
    tone: str
    cover_letter: str
    key_highlights: List[str] = Field(default_factory=list)

