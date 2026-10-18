from uuid import uuid4

from services.persistence.database import transaction
from services.persistence.paper_versions import PaperVersionRepository
from services.persistence.papers import PaperRepository
from services.persistence.processing_jobs import ProcessingJobRepository
from services.persistence.projects import ProjectRepository


def create_queued_job():
    project_id = uuid4()
    paper_id = uuid4()
    version_id = uuid4()
    job_id = uuid4()

    ProjectRepository().create(
        project_id=project_id,
    )

    PaperRepository().create(
        paper_id=paper_id,
        project_id=project_id,
    )

    PaperVersionRepository().create(
        version_id=version_id,
        paper_id=paper_id,
        version_number=1,
        storage_key=f"lifecycle-test/{version_id}.pdf",
        file_hash="lifecycle-test-hash",
        file_size=100,
        mime_type="application/pdf",
        processing_status="QUEUED",
    )

    ProcessingJobRepository().create(
        job_id=job_id,
        paper_version_id=version_id,
        job_type="PAPER_ANALYSIS",
        status="QUEUED",
        stage="VALIDATING",
        pipeline_version="1.0.0",
    )

    return job_id


def cleanup_jobs():
    with transaction() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM processing_jobs
                WHERE status = 'QUEUED'
                """
            )


def test_job_can_be_claimed_and_completed():
    cleanup_jobs()

    repository = ProcessingJobRepository()
    job_id = create_queued_job()

    claimed = repository.claim_next_queued_job()

    assert claimed is not None
    assert claimed.id == job_id
    assert claimed.status == "RUNNING"
    assert claimed.stage == "PARSING"
    assert claimed.attempts == 1
    assert claimed.started_at is not None

    completed = repository.mark_succeeded(job_id)

    assert completed.status == "SUCCEEDED"
    assert completed.stage == "FINALIZING"
    assert completed.completed_at is not None

    cleanup_jobs()


def test_job_can_be_claimed_and_failed():
    cleanup_jobs()

    repository = ProcessingJobRepository()
    job_id = create_queued_job()

    claimed = repository.claim_next_queued_job()

    assert claimed is not None
    assert claimed.id == job_id
    assert claimed.status == "RUNNING"

    failed = repository.mark_failed(
        job_id,
        error_code="PROCESSING_ERROR",
        error_message="Test processing failure.",
    )

    assert failed.status == "FAILED"
    assert failed.error_code == "PROCESSING_ERROR"
    assert failed.error_message == "Test processing failure."
    assert failed.completed_at is not None

    cleanup_jobs()


def test_claim_returns_none_when_no_queued_job_exists():
    cleanup_jobs()

    repository = ProcessingJobRepository()

    assert repository.claim_next_queued_job() is None

    cleanup_jobs()