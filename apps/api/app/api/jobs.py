from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ..schemas.jobs import JobStatusResponse
from services.persistence.processing_jobs import ProcessingJobRepository


router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

job_repository = ProcessingJobRepository()


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_job_status(job_id: UUID):
    job = job_repository.get_by_id(job_id)

    if job is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": "JOB_NOT_FOUND",
                    "message": "The requested processing job was not found.",
                }
            },
        )

    return JobStatusResponse(
        job_id=job.id,
        paper_version_id=job.paper_version_id,
        job_type=job.job_type,
        status=job.status,
        stage=job.stage,
        attempts=job.attempts,
        max_attempts=job.max_attempts,
        pipeline_version=job.pipeline_version,
        error_code=job.error_code,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )