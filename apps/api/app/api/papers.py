from uuid import uuid4

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import JSONResponse

from services.document_processing.intake.validator import validate_document

from ..schemas.papers import PaperUploadResponse

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
    content = await file.read()
    size_bytes = len(content)

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

    return PaperUploadResponse(
        paper_id=str(uuid4()),
        project_id=project_id,
        filename=validation.filename,
        size_bytes=validation.size_bytes,
        status="VALIDATED",
    )