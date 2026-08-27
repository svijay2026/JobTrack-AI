from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.match import MatchAnalysis


class CRUDMatchAnalysis:
    """CRUD operations for MatchAnalysis records."""

    def get_by_id_and_user(self, db: Session, id: int, user_id: int) -> Optional[MatchAnalysis]:
        """Fetch a single match analysis by ID belonging to a specific user."""
        return db.query(MatchAnalysis).filter(
            MatchAnalysis.id == id, MatchAnalysis.user_id == user_id
        ).first()

    def get_multi_by_user(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[MatchAnalysis]:
        """Fetch recent match analyses for a user ordered by created_at descending."""
        return (
            db.query(MatchAnalysis)
            .filter(MatchAnalysis.user_id == user_id)
            .order_by(MatchAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(
        self,
        db: Session,
        user_id: int,
        resume_id: int,
        match_data: Dict[str, Any],
        job_id: Optional[int] = None,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None,
    ) -> MatchAnalysis:
        """Saves a new AI match evaluation record to the database."""
        db_obj = MatchAnalysis(
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            company_name=company_name,
            job_title=job_title,
            match_score=match_data.get("match_score", 0.0),
            skill_match_score=match_data.get("skill_match_score", 0.0),
            semantic_score=match_data.get("semantic_score", 0.0),
            experience_score=match_data.get("experience_score", 0.0),
            matching_skills=match_data.get("matching_skills", []),
            missing_skills=match_data.get("missing_skills", []),
            recommendations=match_data.get("recommendations", []),
            summary=match_data.get("summary", ""),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int, user_id: int) -> Optional[MatchAnalysis]:
        """Deletes a match analysis record."""
        match = self.get_by_id_and_user(db, id=id, user_id=user_id)
        if not match:
            return None

        db.delete(match)
        db.commit()
        return match


match_crud = CRUDMatchAnalysis()
