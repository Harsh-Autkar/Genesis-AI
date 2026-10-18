from concurrent.futures import ThreadPoolExecutor
from uuid import UUID, uuid4

from services.persistence.database import transaction
from services.persistence.paper_versions import PaperVersionRepository
from services.persistence.papers import PaperRepository
from services.persistence.processing_jobs import ProcessingJobRepository
from services.persistence.projects import ProjectRepository


TEST_JOB_PREFIX = "concurrency-test:"


def create_queued_jobs(count: int) -> list[UUID]:
    job_ids: list[UUID] = []

    for _ in range(count):
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
            storage_key=f"{TEST_JOB_PREFIX}{version_id}.pdf",
            file_hash=f"{TEST_JOB_PREFIX}{version_id}",
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
            idempotency_key=f"{TEST_JOB_PREFIX}{job_id}",
            max_attempts=3,
        )

        job_ids.append(job_id)

    return job_ids


def isolate_queued_jobs() -> list[UUID]:
    with transaction() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE processing_jobs
                SET status = 'RUNNING',
                    updated_at = NOW()
                WHERE status = 'QUEUED'
                RETURNING id
                """
            )

            return [row[0] for row in cursor.fetchall()]


def restore_queued_jobs(job_ids: list[UUID]) -> None:
    if not job_ids:
        return

    with transaction() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE processing_jobs
                SET status = 'QUEUED',
                    updated_at = NOW()
                WHERE id = ANY(%s)
                """,
                (job_ids,),
            )


def cleanup_jobs() -> None:
    with transaction() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM processing_jobs
                WHERE idempotency_key LIKE %s
                """,
                (f"{TEST_JOB_PREFIX}%",),
            )


def claim_job():
    return ProcessingJobRepository().claim_next_queued_job()


def test_concurrent_workers_claim_different_jobs():
    cleanup_jobs()

    isolated_job_ids = isolate_queued_jobs()

    try:
        job_ids = create_queued_jobs(2)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(claim_job),
                executor.submit(claim_job),
            ]

            claimed_jobs = [future.result() for future in futures]

        claimed_ids = {
            job.id
            for job in claimed_jobs
            if job is not None
        }

        assert len(claimed_ids) == 2
        assert claimed_ids == set(job_ids)

    finally:
        cleanup_jobs()
        restore_queued_jobs(isolated_job_ids)