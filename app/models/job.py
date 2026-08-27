from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class JobApplication(Base):
    """
    JobApplication database model representing the `job_applications` table.
    Tracks applications submitted by candidates, company details, statuses,
    salaries, notes, and links to used resumes.
    """
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True, index=True)

    company_name = Column(String(255), nullable=False, index=True)
    job_title = Column(String(255), nullable=False, index=True)
    job_location = Column(String(255), nullable=True)
    job_type = Column(String(50), default="full_time", nullable=False)  # full_time, part_time, contract, internship, remote
    salary_range = Column(String(100), nullable=True)
    
    job_description = Column(Text, nullable=True)
    job_url = Column(String(500), nullable=True)
    
    status = Column(String(50), default="applied", nullable=False, index=True)  # wishlist, applied, interviewing, offered, rejected, accepted, archived
    applied_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    deadline = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="job_applications")
    resume = relationship("Resume", back_populates="job_applications")

    def __repr__(self) -> str:
        return f"<JobApplication(id={self.id}, company='{self.company_name}', title='{self.job_title}', status='{self.status}')>"
