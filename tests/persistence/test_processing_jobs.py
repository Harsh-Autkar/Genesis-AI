from uuid import uuid4

from services.persistence.paper_versions import PaperVersionRepository
from services.persistence.papers import PaperRepository
from services.persistence.processing_jobs import ProcessingJobRepository
from services.persistence.projects import ProjectRepository


def test_create_and_get_processing_job():
    project_repository = ProjectRepository()
    paper_repository = PaperRepository()
    version_repository = PaperVersionRepository()
    job_repository = ProcessingJobRepository()

    project_id = uuid4()
    paper_id = uuid4()
    version_id = uuid4()
    job_id = uuid4()

    project_repository.create(
        project_id=project_id,
    )

    paper_repository.create(
        paper_id=paper_id,
        project_id=project_id,
    )

    version_repository.create(
        version_id=version_id,
        paper_id=paper_id,
        version_number=1,
        storage_key="projects/test/papers/test/v1/original.pdf",
        file_hash="hash-v1",
        file_size=1024,
        mime_type="application/pdf",
        processing_status="QUEUED",
    )

    created = job_repository.create(
        job_id=job_id,
        paper_version_id=version_id,
        job_type="PAPER_ANALYSIS",
        status="QUEUED",
        stage="VALIDATING",
        pipeline_version="1.0.0",
        idempotency_key=f"analyze:{version_id}",
    )

    assert created.id == job_id
    assert created.paper_version_id == version_id
    assert created.job_type == "PAPER_ANALYSIS"
    assert created.status == "QUEUED"
    assert created.stage == "VALIDATING"
    assert created.attempts == 0
    assert created.max_attempts == 3
    assert created.pipeline_version == "1.0.0"
    assert created.idempotency_key == f"analyze:{version_id}"
    assert created.error_code is None
    assert created.error_message is None
    assert created.started_at is None
    assert created.completed_at is None

    retrieved = job_repository.get_by_id(job_id)

    assert retrieved is not None
    assert retrieved.id == job_id
    assert retrieved.paper_version_id == version_id
    assert retrieved.status == "QUEUED"
    assert retrieved.pipeline_version == "1.0.0"