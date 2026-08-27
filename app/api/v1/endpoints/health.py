from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api import deps
from app.config import settings

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Application & Database Health Check",
    response_description="Returns the operational status of the API and its database connection.",
)
def check_health(db: Session = Depends(deps.get_db)):
    """
    Health check endpoint:
    1. Verifies that the FastAPI application is alive.
    2. Executes a lightweight `SELECT 1` query against the database engine.
    3. Returns service metadata and connectivity status.
    """
    try:
        # Ping the database to verify active connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        db_status = f"disconnected: {str(exc)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
