from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, resumes, jobs, matching

api_router = APIRouter()

# Mount health check endpoint
api_router.include_router(health.router, tags=["Health"])

# Mount authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Mount resume management endpoints
api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])

# Mount job application management endpoints
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])

# Mount AI matching and scoring endpoints
api_router.include_router(matching.router, prefix="/matching", tags=["AI Matching"])
