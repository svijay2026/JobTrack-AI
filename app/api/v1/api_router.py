from fastapi import APIRouter
from app.api.v1.endpoints import health, auth

api_router = APIRouter()

# Mount health check endpoint
api_router.include_router(health.router, tags=["Health"])

# Mount authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
