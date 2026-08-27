from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_resume import resume_crud
from app.models.user import User
from app.schemas.resume import ResumeCreate, ResumeListItem, ResumeResponse
from app.services.file_service import file_service
from app.services.resume_parser import resume_parser

router = APIRouter()


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a new resume (PDF or DOCX)",
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume document in PDF or DOCX format"),
    is_primary: bool = Form(False, description="Whether to mark this resume as primary"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Uploads a resume file, extracts clean text, identifies technical & soft skills,
    estimates experience, extracts education and contact information, and saves the record.
    """
    # 1. Validate & save file to disk
    file_path, file_name, file_size, file_bytes = await file_service.save_file(
        file=file, user_id=current_user.id
    )

    # 2. Extract extension and parse document
    file_ext = file_service.validate_file(file)
    try:
        parsed_data = resume_parser.parse(file_bytes=file_bytes, file_extension=file_ext)
    except Exception as e:
        # Cleanup uploaded file if parsing fails critically
        file_service.delete_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unable to parse the uploaded document: {str(e)}",
        )

    # 3. Create DB record
    resume_in = ResumeCreate(
        user_id=current_user.id,
        file_name=file_name,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        parsed_text=parsed_data.get("parsed_text", ""),
        skills=parsed_data.get("skills", []),
        experience_years=parsed_data.get("experience_years", 0.0),
        education=parsed_data.get("education", []),
        contact_info=parsed_data.get("contact_info", {}),
        is_primary=is_primary,
    )

    resume = resume_crud.create_with_user(db=db, obj_in=resume_in)
    return resume


@router.get(
    "/",
    response_model=List[ResumeListItem],
    summary="List all resumes of current user",
)
def list_resumes(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Limit of resumes to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retrieves all resumes uploaded by the current user."""
    return resume_crud.get_multi_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)


@router.get(
    "/primary",
    response_model=ResumeResponse,
    summary="Get user's primary resume",
)
def get_primary_resume(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retrieves the user's primary resume."""
    resume = resume_crud.get_primary(db=db, user_id=current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No primary resume found for this user.",
        )
    return resume


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Get specific resume details and parsed data",
)
def get_resume(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retrieves metadata, extracted text, skills, and contact info for a specific resume."""
    resume = resume_crud.get_by_id_and_user(db=db, id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found.",
        )
    return resume


@router.get(
    "/{resume_id}/download",
    summary="Download raw resume file",
)
def download_resume(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Streams the physical resume file for download."""
    resume = resume_crud.get_by_id_and_user(db=db, id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found.",
        )

    file_path = file_service.get_file(resume.file_path)
    return FileResponse(
        path=str(file_path),
        filename=resume.file_name,
        media_type=resume.file_type or "application/octet-stream",
    )


@router.put(
    "/{resume_id}/primary",
    response_model=ResumeResponse,
    summary="Set resume as primary",
)
def set_primary_resume(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Designates a specific resume as the user's primary resume."""
    resume = resume_crud.set_primary(db=db, id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found.",
        )
    return resume


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a resume and its stored file",
)
def delete_resume(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Deletes the resume from database and deletes the physical file from storage."""
    resume = resume_crud.delete(db=db, id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found.",
        )
    return {"message": f"Resume '{resume.file_name}' deleted successfully."}
