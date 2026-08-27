from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_job import job_crud
from app.crud.crud_resume import resume_crud
from app.models.user import User
from app.schemas.job import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationStatusUpdate,
    JobApplicationUpdate,
    JobStatsResponse,
)

router = APIRouter()


@router.post(
    "/",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job application",
)
def create_job_application(
    job_in: JobApplicationCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Creates a new job application record in the candidate's tracker.
    Optionally links a specific resume ID to remember which resume was submitted.
    """
    if job_in.resume_id:
        resume = resume_crud.get_by_id_and_user(db=db, id=job_in.resume_id, user_id=current_user.id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {job_in.resume_id} not found for this user.",
            )

    return job_crud.create_with_user(db=db, obj_in=job_in, user_id=current_user.id)


@router.get(
    "/",
    response_model=List[JobApplicationResponse],
    summary="List job applications with filtering and search",
)
def list_job_applications(
    status: Optional[str] = Query(
        None,
        description="Filter by status (wishlist, applied, interviewing, offered, rejected, accepted, archived)",
    ),
    search: Optional[str] = Query(
        None,
        description="Search term to filter by company name, job title, or location",
    ),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of applications to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retrieves all job applications for the logged-in candidate with support
    for Kanban status filtering, full-text keyword search, and pagination.
    """
    return job_crud.get_multi_by_user(
        db=db,
        user_id=current_user.id,
        status=status,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/stats",
    response_model=JobStatsResponse,
    summary="Get application pipeline analytics and conversion metrics",
)
def get_job_application_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Computes application funnel statistics, including stage breakdown,
    interview response rates, and offer conversion percentages.
    """
    return job_crud.get_stats_by_user(db=db, user_id=current_user.id)


@router.get(
    "/{job_id}",
    response_model=JobApplicationResponse,
    summary="Get single job application details",
)
def get_job_application(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retrieves full details of a specific job application."""
    job = job_crud.get_by_id_and_user(db=db, id=job_id, user_id=current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job application with ID {job_id} not found.",
        )
    return job


@router.put(
    "/{job_id}",
    response_model=JobApplicationResponse,
    summary="Update a job application",
)
def update_job_application(
    job_id: int,
    job_in: JobApplicationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Updates fields of an existing job application."""
    job = job_crud.get_by_id_and_user(db=db, id=job_id, user_id=current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job application with ID {job_id} not found.",
        )

    if job_in.resume_id:
        resume = resume_crud.get_by_id_and_user(db=db, id=job_in.resume_id, user_id=current_user.id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {job_in.resume_id} not found for this user.",
            )

    return job_crud.update(db=db, db_obj=job, obj_in=job_in)


@router.patch(
    "/{job_id}/status",
    response_model=JobApplicationResponse,
    summary="Quickly update application status (Kanban stage transition)",
)
def update_job_status(
    job_id: int,
    status_in: JobApplicationStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Transitions a job application to a new status stage in the Kanban board."""
    job = job_crud.update_status(
        db=db, id=job_id, user_id=current_user.id, status=status_in.status
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job application with ID {job_id} not found.",
        )
    return job


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a job application",
)
def delete_job_application(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Removes a job application from the candidate's tracker."""
    job = job_crud.delete(db=db, id=job_id, user_id=current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job application with ID {job_id} not found.",
        )
    return {"message": f"Job application for '{job.company_name} - {job.job_title}' deleted successfully."}
