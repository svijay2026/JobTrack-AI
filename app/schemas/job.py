from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobStatus(str, Enum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    ARCHIVED = "archived"


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class JobApplicationBase(BaseModel):
    """Base fields for job application."""
    company_name: str = Field(..., min_length=1, max_length=255, description="Name of the hiring company")
    job_title: str = Field(..., min_length=1, max_length=255, description="Title of the job position")
    job_location: Optional[str] = Field(None, max_length=255, description="Location (e.g. Remote, Austin, TX)")
    job_type: str = Field(default=JobType.FULL_TIME.value, description="Employment type")
    salary_range: Optional[str] = Field(None, max_length=100, description="Estimated salary or compensation range")
    job_description: Optional[str] = Field(None, description="Full job posting description text")
    job_url: Optional[str] = Field(None, description="URL link to the job posting")
    status: str = Field(default=JobStatus.APPLIED.value, description="Current Kanban pipeline status")
    applied_date: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Date applied")
    deadline: Optional[datetime] = Field(None, description="Application or response deadline")
    notes: Optional[str] = Field(None, description="Interview notes, contacts, or impressions")
    resume_id: Optional[int] = Field(None, description="ID of the resume used for this application")


class JobApplicationCreate(JobApplicationBase):
    """Schema for creating a new job application."""
    pass


class JobApplicationUpdate(BaseModel):
    """Schema for updating job application details."""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    job_title: Optional[str] = Field(None, min_length=1, max_length=255)
    job_location: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    job_description: Optional[str] = None
    job_url: Optional[str] = None
    status: Optional[str] = None
    applied_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None
    resume_id: Optional[int] = None


class JobApplicationStatusUpdate(BaseModel):
    """Schema for quick Kanban drag-and-drop status update."""
    status: str = Field(..., description="Target status in Kanban pipeline")


class JobApplicationResponse(BaseModel):
    """Response schema for JobApplication."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    resume_id: Optional[int] = None
    company_name: str
    job_title: str
    job_location: Optional[str] = None
    job_type: str
    salary_range: Optional[str] = None
    job_description: Optional[str] = None
    job_url: Optional[str] = None
    status: str
    applied_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class JobStatsResponse(BaseModel):
    """Aggregated pipeline metrics response for user dashboard."""
    total_applications: int
    wishlist: int
    applied: int
    interviewing: int
    offered: int
    rejected: int
    accepted: int
    archived: int
    interview_rate_percent: float
    offer_rate_percent: float
