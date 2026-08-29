from pydantic import BaseModel


class PaperUploadResponse(BaseModel):
    paper_id: str
    project_id: str
    paper_version_id: str
    filename: str
    size_bytes: int
    sha256: str
    storage_key: str
    content_type: str
    status: str