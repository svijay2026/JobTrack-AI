import pytest
from fastapi import HTTPException, UploadFile
import io

from app.services.file_service import FileService


def test_sanitize_filename():
    service = FileService(base_upload_dir="temp_uploads")
    # Path traversal attempts
    assert service.sanitize_filename("../../etc/passwd") == "passwd"
    assert service.sanitize_filename("..\\..\\windows\\system32\\calc.exe") == "calc.exe"
    # Special characters
    assert service.sanitize_filename("my resume (v2) [final]!.pdf") == "my_resume__v2___final__.pdf"


def test_validate_file_extensions():
    service = FileService(base_upload_dir="temp_uploads")
    
    # Valid files
    pdf_file = UploadFile(filename="resume.pdf", file=io.BytesIO(b"dummy"))
    docx_file = UploadFile(filename="cv.docx", file=io.BytesIO(b"dummy"))
    assert service.validate_file(pdf_file) == ".pdf"
    assert service.validate_file(docx_file) == ".docx"

    # Invalid files
    exe_file = UploadFile(filename="malicious.exe", file=io.BytesIO(b"dummy"))
    with pytest.raises(HTTPException) as exc_info:
        service.validate_file(exe_file)
    assert exc_info.value.status_code == 400
