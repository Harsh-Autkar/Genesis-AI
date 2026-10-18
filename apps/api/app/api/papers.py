from uuid import UUID

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import JSONResponse

from ..schemas.papers import PaperUploadResponse
from ..services.paper_upload import (
    PaperUploadService,
    PaperUploadValidationError,
    ProjectNotFoundError,
)


router = APIRouter(prefix="/api/v1/projects", tags=["papers"])

paper_upload_service = PaperUploadService()


@router.post(
    "/{project_id}/papers",
    response_model=PaperUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_paper(
    project_id: UUID,
    file: UploadFile = File(...),
):
    try:
        paper, paper_version, job, stored_file = paper_upload_service.upload(
            project_id=project_id,
            file=file,
        )

    except ProjectNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": "PROJECT_NOT_FOUND",
                    "message": "The requested project was not found.",
                }
            },
        )

    except PaperUploadValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    return PaperUploadResponse(
        paper_id=paper.id,
        project_id=paper.project_id,
        paper_version_id=paper_version.id,
        job_id=job.id,
        filename=file.filename or "",
        size_bytes=stored_file.size_bytes,
        sha256=stored_file.sha256,
        storage_key=stored_file.storage_key,
        content_type=stored_file.content_type,
        status=job.status,
    )