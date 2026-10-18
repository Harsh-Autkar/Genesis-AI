from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobStatusResponse(BaseModel):
    job_id: UUID
    paper_version_id: UUID
    job_type: str
    status: str
    stage: str | None
    attempts: int
    max_attempts: int
    pipeline_version: str
    error_code: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None