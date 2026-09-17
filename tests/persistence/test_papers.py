from uuid import uuid4

from services.persistence.papers import PaperRepository
from services.persistence.projects import ProjectRepository


def test_create_and_get_paper():
    project_repository = ProjectRepository()
    paper_repository = PaperRepository()

    project_id = uuid4()
    paper_id = uuid4()

    project_repository.create(
        project_id=project_id,
    )

    created = paper_repository.create(
        paper_id=paper_id,
        project_id=project_id,
    )

    assert created.id == paper_id
    assert created.project_id == project_id
    assert created.created_at is not None
    assert created.updated_at is not None

    retrieved = paper_repository.get_by_id(paper_id)

    assert retrieved is not None
    assert retrieved.id == paper_id
    assert retrieved.project_id == project_id