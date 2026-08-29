from pydantic import BaseModel


class PaperUploadResponse(BaseModel):
    paper_id: str
    project_id: str
    filename: str
    size_bytes: int
    status: str