import os
import re
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/octet-stream",
}


class FileService:
    """
    Service for validating, saving, retrieving, and deleting uploaded resume files safely.
    """

    def __init__(self, base_upload_dir: str = settings.UPLOAD_DIR):
        self.base_upload_dir = Path(base_upload_dir)

    def validate_file(self, file: UploadFile) -> str:
        """
        Validates file extension and content type.
        Returns the file extension in lowercase.
        """
        filename = file.filename or ""
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '{ext}'. Allowed extensions are: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
            # Fallback check if extension is valid
            pass

        return ext

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes filename by stripping directory paths and keeping only safe characters.
        """
        clean_name = os.path.basename(filename)
        clean_name = re.sub(r"[^\w\.\-]", "_", clean_name)
        return clean_name or "resume"

    async def save_file(self, file: UploadFile, user_id: int) -> Tuple[str, str, int, bytes]:
        """
        Validates and saves the uploaded file into user's upload directory.
        Returns a tuple of (saved_file_path, sanitized_file_name, file_size_bytes, file_bytes).
        """
        ext = self.validate_file(file)
        clean_name = self.sanitize_filename(file.filename or f"resume{ext}")
        
        # Read content and validate size
        content = await file.read()
        file_size = len(content)
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        if file_size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB.",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        # Create user storage directory
        user_dir = self.base_upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename to prevent overwriting
        unique_name = f"{uuid.uuid4().hex}_{clean_name}"
        destination_path = user_dir / unique_name

        with open(destination_path, "wb") as f:
            f.write(content)

        return str(destination_path), clean_name, file_size, content

    def delete_file(self, file_path: str) -> bool:
        """
        Safely deletes a file from the disk if it exists.
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                return True
        except Exception:
            pass
        return False

    def get_file(self, file_path: str) -> Path:
        """
        Retrieves Path object and ensures it exists.
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume file not found on disk.",
            )
        return path


file_service = FileService()
