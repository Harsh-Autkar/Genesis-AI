from uuid import uuid4

from services.persistence.database import transaction
from services.persistence.paper_versions import PaperVersionRepository
from services.persistence.papers import PaperRepository
from services.persistence.processing_jobs import ProcessingJobRepository
from services.persistence.projects import ProjectRepository


def create_job(*, max_attempts=3):
    project_id = uuid4()
    paper_id = uuid4()
    version_id = uuid4()
    job_id = uuid4()

    ProjectRepository().create(project_id=project_id)

    PaperRepository().create(
        paper_id=paper_id,
        project_id=project_id,
    )

    PaperVersionRepository().create(
        version_id=version_id,
        paper_id=paper_id,
        version_number=1,
        storage_key=f"retry-test/{version_id}.pdf",
        file_hash="retry-test-hash",
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
        max_attempts=max_attempts,
    )

    return job_id


def cleanup_jobs():
    with transaction() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM processing_jobs
                WHERE status IN ('QUEUED', 'RUNNING', 'RETRYING')
                """
            )


def test_retry_returns_job_to_queue():
    cleanup_jobs()

    repository = ProcessingJobRepository()
    job_id = create_job()

    claimed = repository.claim_next_queued_job()

    assert claimed is not None
    assert claimed.id == job_id
    assert claimed.status == "RUNNING"
    assert claimed.attempts == 1

    retried = repository.retry(
        job_id,
        error_code="TEMPORARY_ERROR",
        error_message="Temporary processing failure.",
    )

    assert retried.id == job_id
    assert retried.status == "QUEUED"
    assert retried.error_code == "TEMPORARY_ERROR"
    assert retried.error_message == "Temporary processing failure."
    assert retried.completed_at is None

    cleanup_jobs()


def test_retry_after_max_attempts_marks_job_failed():
    cleanup_jobs()

    repository = ProcessingJobRepository()
    job_id = create_job(max_attempts=1)

    claimed = repository.claim_next_queued_job()

    assert claimed is not None
    assert claimed.id == job_id
    assert claimed.attempts == 1

    failed = repository.retry(
        job_id,
        error_code="FINAL_ERROR",
        error_message="Maximum attempts reached.",
    )

    assert failed.id == job_id
    assert failed.status == "FAILED"
    assert failed.error_code == "FINAL_ERROR"
    assert failed.error_message == "Maximum attempts reached."
    assert failed.completed_at is not None

    cleanup_jobs()


def test_retry_requires_running_job():
    cleanup_jobs()

    repository = ProcessingJobRepository()
    job_id = create_job()

    try:
        repository.retry(
            job_id,
            error_code="INVALID_STATE",
            error_message="Job has not been claimed.",
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("Retry should reject a QUEUED job.")

    cleanup_jobs()