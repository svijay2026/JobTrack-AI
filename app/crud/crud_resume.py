from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate
from app.services.file_service import file_service


class CRUDResume:
    """CRUD operations for Resumes."""

    def get_by_id_and_user(self, db: Session, id: int, user_id: int) -> Optional[Resume]:
        """Fetch a single resume belonging to a specific user."""
        return db.query(Resume).filter(Resume.id == id, Resume.user_id == user_id).first()

    def get_multi_by_user(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Resume]:
        """Fetch multiple resumes belonging to a specific user ordered by created_at desc."""
        return (
            db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.is_primary.desc(), Resume.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_primary(self, db: Session, user_id: int) -> Optional[Resume]:
        """Fetch the primary resume for a user."""
        return db.query(Resume).filter(Resume.user_id == user_id, Resume.is_primary == True).first()

    def count_by_user(self, db: Session, user_id: int) -> int:
        """Count total resumes for a user."""
        return db.query(Resume).filter(Resume.user_id == user_id).count()

    def create_with_user(self, db: Session, obj_in: ResumeCreate) -> Resume:
        """
        Creates a new resume record for a user.
        If user has no existing resumes, this automatically becomes the primary resume.
        If is_primary is True, unsets any other primary resumes for this user.
        """
        existing_count = self.count_by_user(db, user_id=obj_in.user_id)
        is_primary = obj_in.is_primary or (existing_count == 0)

        if is_primary and existing_count > 0:
            # Unset existing primary
            db.query(Resume).filter(
                Resume.user_id == obj_in.user_id, Resume.is_primary == True
            ).update({"is_primary": False})
            db.commit()

        db_obj = Resume(
            user_id=obj_in.user_id,
            file_name=obj_in.file_name,
            file_path=obj_in.file_path,
            file_type=obj_in.file_type,
            file_size=obj_in.file_size,
            parsed_text=obj_in.parsed_text,
            skills=obj_in.skills,
            experience_years=obj_in.experience_years,
            education=obj_in.education,
            contact_info=obj_in.contact_info,
            is_primary=is_primary,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def set_primary(self, db: Session, id: int, user_id: int) -> Optional[Resume]:
        """Sets the specified resume as primary and unsets all others for this user."""
        resume = self.get_by_id_and_user(db, id=id, user_id=user_id)
        if not resume:
            return None

        # Unset all other resumes
        db.query(Resume).filter(
            Resume.user_id == user_id, Resume.id != id
        ).update({"is_primary": False})

        resume.is_primary = True
        db.commit()
        db.refresh(resume)
        return resume

    def update(
        self,
        db: Session,
        db_obj: Resume,
        obj_in: Union[ResumeUpdate, Dict[str, Any]],
    ) -> Resume:
        """Updates resume attributes."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int, user_id: int) -> Optional[Resume]:
        """
        Deletes a resume record from database and removes its physical file from disk.
        If deleted resume was primary, promotes the most recent remaining resume to primary.
        """
        resume = self.get_by_id_and_user(db, id=id, user_id=user_id)
        if not resume:
            return None

        was_primary = resume.is_primary
        file_path = resume.file_path

        db.delete(resume)
        db.commit()

        # Delete physical file
        file_service.delete_file(file_path)

        # Promote next resume if this was primary
        if was_primary:
            remaining = self.get_multi_by_user(db, user_id=user_id, limit=1)
            if remaining:
                remaining[0].is_primary = True
                db.commit()

        return resume


resume_crud = CRUDResume()
