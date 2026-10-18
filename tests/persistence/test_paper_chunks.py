from uuid import uuid4

from services.persistence.paper_chunks import PaperChunkRepository
from services.persistence.papers import PaperRepository
from services.persistence.paper_versions import PaperVersionRepository
from services.persistence.projects import ProjectRepository


def test_create_and_get_paper_chunks():
    project_repository = ProjectRepository()
    paper_repository = PaperRepository()
    version_repository = PaperVersionRepository()
    chunk_repository = PaperChunkRepository()

    project_id = uuid4()
    paper_id = uuid4()
    paper_version_id = uuid4()

    project_repository.create(
        project_id=project_id,
    )

    paper_repository.create(
        paper_id=paper_id,
        project_id=project_id,
    )

    version_repository.create(
        version_id=paper_version_id,
        paper_id=paper_id,
        version_number=1,
        storage_key="projects/test/papers/test/v1/original.pdf",
        file_hash="hash-v1",
        file_size=1024,
        mime_type="application/pdf",
        processing_status="QUEUED",
    )

    chunk_1_id = uuid4()
    chunk_2_id = uuid4()

    created = chunk_repository.create_many(
        chunks=[
            {
                "id": chunk_1_id,
                "paper_version_id": paper_version_id,
                "text": "This is the first research paragraph.",
                "section_type": "ABSTRACT",
                "start_page": 1,
                "end_page": 1,
                "position": 0,
                "pipeline_version": "1.0.0",
            },
            {
                "id": chunk_2_id,
                "paper_version_id": paper_version_id,
                "text": "This is the second research paragraph.",
                "section_type": "INTRODUCTION",
                "start_page": 2,
                "end_page": 2,
                "position": 1,
                "pipeline_version": "1.0.0",
            },
        ],
    )

    assert len(created) == 2
    assert created[0].id == chunk_1_id
    assert created[0].paper_version_id == paper_version_id
    assert created[0].section_type == "ABSTRACT"
    assert created[0].position == 0

    retrieved = chunk_repository.get_by_paper_version(
        paper_version_id,
    )

    assert len(retrieved) == 2
    assert retrieved[0].id == chunk_1_id
    assert retrieved[0].text == "This is the first research paragraph."
    assert retrieved[1].id == chunk_2_id
    assert retrieved[1].position == 1


def test_create_many_empty_chunks_is_noop():
    repository = PaperChunkRepository()

    created = repository.create_many(
        chunks=[],
    )

    assert created == ()