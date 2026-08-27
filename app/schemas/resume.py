from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ContactInfo(BaseModel):
    """Structured contact info extracted from resume."""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    location: Optional[str] = None


class EducationItem(BaseModel):
    """Structured education item extracted from resume."""
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None


class ResumeBase(BaseModel):
    """Base schema for Resume."""
    file_name: str
    is_primary: bool = False


class ResumeCreate(ResumeBase):
    """Schema for internal resume creation after file upload & parsing."""
    user_id: int
    file_path: str
    file_type: str
    file_size: int
    parsed_text: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    education: List[Dict[str, Any]] = Field(default_factory=list)
    contact_info: Dict[str, Any] = Field(default_factory=dict)


class ResumeUpdate(BaseModel):
    """Schema for updating resume properties."""
    is_primary: Optional[bool] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None


class ResumeParsedData(BaseModel):
    """Schema representing structured parsed information."""
    text_preview: str
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    education: List[Dict[str, Any]] = Field(default_factory=list)
    contact_info: Dict[str, Any] = Field(default_factory=dict)


class ResumeListItem(BaseModel):
    """Lightweight schema for listing resumes in dashboard."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    file_name: str
    file_type: str
    file_size: int
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    is_primary: bool
    created_at: datetime
    updated_at: datetime


class ResumeResponse(BaseModel):
    """Full detailed schema for resume response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    file_name: str
    file_type: str
    file_size: int
    parsed_text: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    education: List[Dict[str, Any]] = Field(default_factory=list)
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    is_primary: bool
    created_at: datetime
    updated_at: datetime
