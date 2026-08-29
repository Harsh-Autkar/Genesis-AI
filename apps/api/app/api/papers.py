from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import JSONResponse

from services.document_processing.intake.stream import (
    FileTooLargeError,
    measure_stream_size,
)
from services.document_processing.intake.validator import validate_document

from ..schemas.papers import PaperUploadResponse
from ..services.storage import file_storage


router = APIRouter(prefix="/api/v1/projects", tags=["papers"])


@router.post(
    "/{project_id}/papers",
    response_model=PaperUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_paper(
    project_id: str,
    file: UploadFile = File(...),
):
    try:
        size_bytes = measure_stream_size(file.file)
    except FileTooLargeError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": "The uploaded file exceeds the 15 MB limit.",
                }
            },
        )

    validation = validate_document(
        filename=file.filename,
        size_bytes=size_bytes,
        content_type=file.content_type,
    )

    if not validation.valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": validation.error_code,
                    "message": validation.error_message,
                }
            },
        )

    paper_id = str(uuid4())
    paper_version_id = str(uuid4())

    extension = Path(validation.filename).suffix.lower()

    storage_key = (
        f"projects/{project_id}/papers/"
        f"{paper_id}/versions/{paper_version_id}/original{extension}"
    )

    stored_file = file_storage.store(
        file.file,
        storage_key=storage_key,
        content_type=validation.content_type or "application/pdf",
    )

    return PaperUploadResponse(
        paper_id=paper_id,
        project_id=project_id,
        paper_version_id=paper_version_id,
        filename=validation.filename,
        size_bytes=stored_file.size_bytes,
        sha256=stored_file.sha256,
        storage_key=stored_file.storage_key,
        content_type=stored_file.content_type,
        status="STORED",
    )