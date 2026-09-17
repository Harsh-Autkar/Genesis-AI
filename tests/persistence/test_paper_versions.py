from uuid import uuid4

from services.persistence.paper_versions import PaperVersionRepository
from services.persistence.papers import PaperRepository
from services.persistence.projects import ProjectRepository


def test_create_get_and_get_latest_paper_version():
    project_repository = ProjectRepository()
    paper_repository = PaperRepository()
    version_repository = PaperVersionRepository()

    project_id = uuid4()
    paper_id = uuid4()

    project_repository.create(
        project_id=project_id,
    )

    paper_repository.create(
        paper_id=paper_id,
        project_id=project_id,
    )

    version_1_id = uuid4()

    created_v1 = version_repository.create(
        version_id=version_1_id,
        paper_id=paper_id,
        version_number=1,
        storage_key="projects/test/papers/test/v1/original.pdf",
        file_hash="hash-v1",
        file_size=1024,
        mime_type="application/pdf",
        processing_status="QUEUED",
    )

    assert created_v1.id == version_1_id
    assert created_v1.paper_id == paper_id
    assert created_v1.version_number == 1
    assert created_v1.processing_status == "QUEUED"

    version_2_id = uuid4()

    version_repository.create(
        version_id=version_2_id,
        paper_id=paper_id,
        version_number=2,
        storage_key="projects/test/papers/test/v2/original.pdf",
        file_hash="hash-v2",
        file_size=2048,
        mime_type="application/pdf",
        processing_status="QUEUED",
    )

    retrieved = version_repository.get_by_id(version_1_id)

    assert retrieved is not None
    assert retrieved.version_number == 1
    assert retrieved.file_hash == "hash-v1"

    latest = version_repository.get_latest_for_paper(
        paper_id,
    )

    assert latest is not None
    assert latest.id == version_2_id
    assert latest.version_number == 2