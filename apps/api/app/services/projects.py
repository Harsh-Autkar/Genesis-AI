from uuid import UUID, uuid4

from services.persistence.projects import ProjectRepository


class ProjectService:
    def __init__(self, repository: ProjectRepository | None = None):
        self.repository = repository or ProjectRepository()

    def create_project(self) -> tuple[UUID, str]:
        project_id = uuid4()
        self.repository.create(project_id=project_id)
        return project_id, "CREATED"