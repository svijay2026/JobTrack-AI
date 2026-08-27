from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.nlp.matcher import matcher
from app.crud.crud_job import job_crud
from app.crud.crud_match import match_crud
from app.crud.crud_resume import resume_crud
from app.models.user import User
from app.schemas.match import (
    MatchHistoryItem,
    MatchRequest,
    MatchResultResponse,
)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=MatchResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run AI match analysis between a resume and job description",
)
def analyze_resume_job_match(
    match_req: MatchRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Evaluates candidate resume against target job description.
    Computes multi-dimensional match score (skills, TF-IDF cosine relevance, experience),
    detects missing skill gaps, and generates targeted resume optimization tips.
    """
    # 1. Resolve Resume
    if match_req.resume_id:
        resume = resume_crud.get_by_id_and_user(
            db=db, id=match_req.resume_id, user_id=current_user.id
        )
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {match_req.resume_id} not found.",
            )
    else:
        # Fallback to primary resume or most recent
        resume = resume_crud.get_primary(db=db, user_id=current_user.id)
        if not resume:
            user_resumes = resume_crud.get_multi_by_user(db=db, user_id=current_user.id, limit=1)
            if not user_resumes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No resume found. Please upload a resume before running AI matching.",
                )
            resume = user_resumes[0]

    # 2. Resolve Job Description & Metadata
    job_id: Optional[int] = None
    company_name: Optional[str] = match_req.company_name
    job_title: Optional[str] = match_req.job_title
    job_description: Optional[str] = match_req.job_description

    if match_req.job_id:
        job = job_crud.get_by_id_and_user(db=db, id=match_req.job_id, user_id=current_user.id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job application with ID {match_req.job_id} not found.",
            )
        job_id = job.id
        company_name = job.company_name
        job_title = job.job_title
        job_description = job.job_description or ""

    if not job_description or not job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description text is required to evaluate match.",
        )

    # 3. Execute NLP Matching Pipeline
    match_result = matcher.analyze_match(
        resume_text=resume.parsed_text or "",
        candidate_skills=resume.skills or [],
        candidate_experience_years=resume.experience_years or 0.0,
        job_description=job_description,
        job_title=job_title or "",
    )

    # 4. Save Record to Database
    analysis_record = match_crud.create(
        db=db,
        user_id=current_user.id,
        resume_id=resume.id,
        job_id=job_id,
        company_name=company_name,
        job_title=job_title,
        match_data=match_result,
    )

    return analysis_record


@router.get(
    "/history",
    response_model=List[MatchHistoryItem],
    summary="Get user's past match evaluations",
)
def list_match_history(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=50, description="Max history items"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retrieves previous AI match analysis history for current user."""
    return match_crud.get_multi_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get(
    "/{match_id}",
    response_model=MatchResultResponse,
    summary="Get details of a specific match report",
)
def get_match_report(
    match_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retrieves full scoring breakdown and recommendations for a previous match."""
    report = match_crud.get_by_id_and_user(db=db, id=match_id, user_id=current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match report with ID {match_id} not found.",
        )
    return report


@router.delete(
    "/{match_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a match evaluation report",
)
def delete_match_report(
    match_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Deletes a match analysis record from database."""
    report = match_crud.delete(db=db, id=match_id, user_id=current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match report with ID {match_id} not found.",
        )
    return {"message": "Match analysis report deleted successfully."}
