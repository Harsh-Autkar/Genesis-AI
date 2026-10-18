from uuid import uuid4

from services.persistence.projects import ProjectRepository


def test_create_and_get_project():
    repository = ProjectRepository()
    project_id = uuid4()

    created = repository.create(
        project_id=project_id,
    )

    assert created.id == project_id
    assert created.owner_user_id is None
    assert created.created_at is not None
    assert created.updated_at is not None

    retrieved = repository.get_by_id(project_id)

    assert retrieved is not None
    assert retrieved.id == project_id
    assert retrieved.owner_user_id is None