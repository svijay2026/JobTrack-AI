from typing import Any, Dict, List, Optional, Union
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.models.job import JobApplication
from app.schemas.job import JobApplicationCreate, JobApplicationUpdate, JobStatus


class CRUDJobApplication:
    """CRUD operations for JobApplication model."""

    def get_by_id_and_user(self, db: Session, id: int, user_id: int) -> Optional[JobApplication]:
        """Fetch a single job application by ID for a specific user."""
        return db.query(JobApplication).filter(
            JobApplication.id == id, JobApplication.user_id == user_id
        ).first()

    def get_multi_by_user(
        self,
        db: Session,
        user_id: int,
        status: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[JobApplication]:
        """
        Fetch multiple job applications for a user with optional status filtering
        and search by company name or job title.
        """
        query = db.query(JobApplication).filter(JobApplication.user_id == user_id)

        if status:
            query = query.filter(JobApplication.status == status.lower())

        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    JobApplication.company_name.ilike(search_pattern),
                    JobApplication.job_title.ilike(search_pattern),
                    JobApplication.job_location.ilike(search_pattern),
                )
            )

        return query.order_by(JobApplication.updated_at.desc()).offset(skip).limit(limit).all()

    def count_by_user(
        self,
        db: Session,
        user_id: int,
        status: Optional[str] = None,
    ) -> int:
        """Count total applications for user, optionally filtered by status."""
        query = db.query(JobApplication).filter(JobApplication.user_id == user_id)
        if status:
            query = query.filter(JobApplication.status == status.lower())
        return query.count()

    def create_with_user(
        self, db: Session, obj_in: JobApplicationCreate, user_id: int
    ) -> JobApplication:
        """Create a new job application record for a user."""
        db_obj = JobApplication(
            user_id=user_id,
            company_name=obj_in.company_name,
            job_title=obj_in.job_title,
            job_location=obj_in.job_location,
            job_type=obj_in.job_type,
            salary_range=obj_in.salary_range,
            job_description=obj_in.job_description,
            job_url=obj_in.job_url,
            status=obj_in.status.lower() if obj_in.status else JobStatus.APPLIED.value,
            applied_date=obj_in.applied_date,
            deadline=obj_in.deadline,
            notes=obj_in.notes,
            resume_id=obj_in.resume_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: JobApplication,
        obj_in: Union[JobApplicationUpdate, Dict[str, Any]],
    ) -> JobApplication:
        """Update an existing job application record."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Normalize status if updated
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].lower()

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_status(
        self, db: Session, id: int, user_id: int, status: str
    ) -> Optional[JobApplication]:
        """Quick status transition helper (Kanban movement)."""
        job = self.get_by_id_and_user(db, id=id, user_id=user_id)
        if not job:
            return None

        job.status = status.lower()
        db.commit()
        db.refresh(job)
        return job

    def delete(self, db: Session, id: int, user_id: int) -> Optional[JobApplication]:
        """Delete a job application."""
        job = self.get_by_id_and_user(db, id=id, user_id=user_id)
        if not job:
            return None

        db.delete(job)
        db.commit()
        return job

    def get_stats_by_user(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Computes funnel metrics and application stage aggregations."""
        rows = (
            db.query(JobApplication.status, func.count(JobApplication.id))
            .filter(JobApplication.user_id == user_id)
            .group_by(JobApplication.status)
            .all()
        )

        counts = {
            "wishlist": 0,
            "applied": 0,
            "interviewing": 0,
            "offered": 0,
            "rejected": 0,
            "accepted": 0,
            "archived": 0,
        }

        total_applications = 0
        for status_val, count in rows:
            clean_status = status_val.lower() if status_val else "applied"
            if clean_status in counts:
                counts[clean_status] = count
            total_applications += count

        # Funnel conversions: candidates reaching interview stage vs total non-wishlist applications
        active_pipeline = total_applications - counts["wishlist"]
        positive_responses = counts["interviewing"] + counts["offered"] + counts["accepted"]
        successful_offers = counts["offered"] + counts["accepted"]

        interview_rate = (
            round((positive_responses / active_pipeline) * 100, 1)
            if active_pipeline > 0
            else 0.0
        )
        offer_rate = (
            round((successful_offers / active_pipeline) * 100, 1)
            if active_pipeline > 0
            else 0.0
        )

        return {
            "total_applications": total_applications,
            "wishlist": counts["wishlist"],
            "applied": counts["applied"],
            "interviewing": counts["interviewing"],
            "offered": counts["offered"],
            "rejected": counts["rejected"],
            "accepted": counts["accepted"],
            "archived": counts["archived"],
            "interview_rate_percent": interview_rate,
            "offer_rate_percent": offer_rate,
        }


job_crud = CRUDJobApplication()
