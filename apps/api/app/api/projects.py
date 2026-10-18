from fastapi import APIRouter, status

from ..schemas.projects import ProjectCreateResponse
from ..services.projects import ProjectService


router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

project_service = ProjectService()


@router.post(
    "",
    response_model=ProjectCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project():
    project_id, project_status = project_service.create_project()

    return ProjectCreateResponse(
        project_id=project_id,
        status=project_status,
    )