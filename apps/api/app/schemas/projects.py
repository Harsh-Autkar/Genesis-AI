from uuid import UUID

from pydantic import BaseModel


class ProjectCreateResponse(BaseModel):
    project_id: UUID
    status: str