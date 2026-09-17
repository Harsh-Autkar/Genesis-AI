from uuid import UUID

from pydantic import BaseModel


class PaperUploadResponse(BaseModel):
    paper_id: UUID
    project_id: UUID
    paper_version_id: UUID
    job_id: UUID
    filename: str
    size_bytes: int
    sha256: str
    storage_key: str
    content_type: str
    status: str