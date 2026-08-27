from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class Resume(Base):
    """
    Resume database model representing the `resumes` table.
    Stores uploaded file metadata, raw extracted text, and structured parsed attributes
    (skills, experience, education, contact info).
    """
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    
    parsed_text = Column(Text, nullable=True)
    skills = Column(JSON, default=list, nullable=False)
    experience_years = Column(Float, default=0.0, nullable=False)
    education = Column(JSON, default=list, nullable=False)
    contact_info = Column(JSON, default=dict, nullable=False)
    
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="resumes")
    job_applications = relationship("JobApplication", back_populates="resume")

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, user_id={self.user_id}, file_name='{self.file_name}', is_primary={self.is_primary})>"
