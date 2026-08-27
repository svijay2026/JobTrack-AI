from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class MatchAnalysis(Base):
    """
    MatchAnalysis database model representing the `match_analyses` table.
    Stores AI-computed scoring results, skill gaps, and recommendations
    comparing a candidate's resume against a target job description.
    """
    __tablename__ = "match_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_applications.id", ondelete="SET NULL"), nullable=True, index=True)

    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)

    match_score = Column(Float, nullable=False)
    skill_match_score = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)

    matching_skills = Column(JSON, default=list, nullable=False)
    missing_skills = Column(JSON, default=list, nullable=False)
    recommendations = Column(JSON, default=list, nullable=False)
    summary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="matches")
    resume = relationship("Resume", back_populates="matches")
    job = relationship("JobApplication", back_populates="matches")

    def __repr__(self) -> str:
        return f"<MatchAnalysis(id={self.id}, user_id={self.user_id}, score={self.match_score}%)>"
