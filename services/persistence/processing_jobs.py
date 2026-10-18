from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import psycopg

from .database import get_connection


@dataclass(frozen=True)
class ProcessingJob:
    id: UUID
    paper_version_id: UUID
    job_type: str
    status: str
    stage: str | None
    attempts: int
    max_attempts: int
    idempotency_key: str | None
    pipeline_version: str
    error_code: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class ProcessingJobRepository:
    """PostgreSQL persistence for processing jobs."""

    def create(
        self,
        *,
        job_id: UUID,
        paper_version_id: UUID,
        job_type: str,
        status: str,
        pipeline_version: str,
        idempotency_key: str | None = None,
        stage: str | None = None,
        attempts: int = 0,
        max_attempts: int = 3,
        connection: psycopg.Connection | None = None,
    ) -> ProcessingJob:
        if connection is not None:
            return self._create_with_connection(
                connection,
                job_id=job_id,
                paper_version_id=paper_version_id,
                job_type=job_type,
                status=status,
                pipeline_version=pipeline_version,
                idempotency_key=idempotency_key,
                stage=stage,
                attempts=attempts,
                max_attempts=max_attempts,
            )

        with get_connection() as own_connection:
            return self._create_with_connection(
                own_connection,
                job_id=job_id,
                paper_version_id=paper_version_id,
                job_type=job_type,
                status=status,
                pipeline_version=pipeline_version,
                idempotency_key=idempotency_key,
                stage=stage,
                attempts=attempts,
                max_attempts=max_attempts,
            )

    def get_by_id(
        self,
        job_id: UUID,
        *,
        connection: psycopg.Connection | None = None,
    ) -> ProcessingJob | None:
        if connection is not None:
            return self._get_by_id_with_connection(
                connection,
                job_id,
            )

        with get_connection() as own_connection:
            return self._get_by_id_with_connection(
                own_connection,
                job_id,
            )

    def claim_next_queued_job(
        self,
        *,
        connection: psycopg.Connection | None = None,
    ) -> ProcessingJob | None:
        if connection is not None:
            return self._claim_next_queued_job_with_connection(
                connection,
            )

        with get_connection() as own_connection:
            return self._claim_next_queued_job_with_connection(
                own_connection,
            )

    def mark_succeeded(
        self,
        job_id: UUID,
        *,
        connection: psycopg.Connection | None = None,
    ) -> ProcessingJob:
        if connection is not None:
            return self._mark_succeeded_with_connection(
                connection,
                job_id,
            )

        with get_connection() as own_connection:
            return self._mark_succeeded_with_connection(
                own_connection,
                job_id,
            )

    def mark_failed(
        self,
        job_id: UUID,
        *,
        error_code: str,
        error_message: str,
        connection: psycopg.Connection | None = None,
    ) -> ProcessingJob:
        if connection is not None:
            return self._mark_failed_with_connection(
                connection,
                job_id=job_id,
                error_code=error_code,
                error_message=error_message,
            )

        with get_connection() as own_connection:
            return self._mark_failed_with_connection(
                own_connection,
                job_id=job_id,
                error_code=error_code,
                error_message=error_message,
            )

    def retry(
        self,
        job_id: UUID,
        *,
        error_code: str,
        error_message: str,
        connection: psycopg.Connection | None = None,
    ) -> ProcessingJob:
        if connection is not None:
            return self._retry_with_connection(
                connection,
                job_id=job_id,
                error_code=error_code,
                error_message=error_message,
            )

        with get_connection() as own_connection:
            return self._retry_with_connection(
                own_connection,
                job_id=job_id,
                error_code=error_code,
                error_message=error_message,
            )

    @staticmethod
    def _create_with_connection(
        connection: psycopg.Connection,
        *,
        job_id: UUID,
        paper_version_id: UUID,
        job_type: str,
        status: str,
        pipeline_version: str,
        idempotency_key: str | None,
        stage: str | None,
        attempts: int,
        max_attempts: int,
    ) -> ProcessingJob:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO processing_jobs (
                    id,
                    paper_version_id,
                    job_type,
                    status,
                    stage,
                    attempts,
                    max_attempts,
                    idempotency_key,
                    pipeline_version
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                RETURNING
                    id,
                    paper_version_id,
                    job_type,
                    status,
                    stage,
                    attempts,
                    max_attempts,
                    idempotency_key,
                    pipeline_version,
                    error_code,
                    error_message,
                    created_at,
                    updated_at,
                    started_at,
                    completed_at
                """,
                (
                    job_id,
                    paper_version_id,
                    job_type,
                    status,
                    stage,
                    attempts,
                    max_attempts,
                    idempotency_key,
                    pipeline_version,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Processing job creation returned no row."
            )

        return ProcessingJobRepository._from_row(row)

    @staticmethod
    def _get_by_id_with_connection(
        connection: psycopg.Connection,
        job_id: UUID,
    ) -> ProcessingJob | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    paper_version_id,
                    job_type,
                    status,
                    stage,
                    attempts,
                    max_attempts,
                    idempotency_key,
                    pipeline_version,
                    error_code,
                    error_message,
                    created_at,
                    updated_at,
                    started_at,
                    completed_at
                FROM processing_jobs
                WHERE id = %s
                """,
                (job_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return ProcessingJobRepository._from_row(row)

    @staticmethod
    def _claim_next_queued_job_with_connection(
        connection: psycopg.Connection,
    ) -> ProcessingJob | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM processing_jobs
                WHERE status = 'QUEUED'
                  AND attempts < max_attempts
                ORDER BY created_at
                FOR UPDATE SKIP LOCKED
                LIMIT 1
                """
            )

            row = cursor.fetchone()

            if row is None:
                return None

            job_id = row[0]

            cursor.execute(
                """
                UPDATE processing_jobs
                SET
                    status = 'RUNNING',
                    stage = 'PARSING',
                    attempts = attempts + 1,
                    started_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
                  AND status = 'QUEUED'
                RETURNING
                    id,
                    paper_version_id,
                    job_type,
                    status,
                    stage,
                    attempts,
                    max_attempts,
                    idempotency_key,
                    pipeline_version,
                    error_code,
                    error_message,
                    created_at,
                    updated_at,
                    started_at,
                    completed_at
                """,
                (job_id,),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Processing job claim returned no row."
            )

        return ProcessingJobRepository._from_row(row)

    @staticmethod
    def _mark_succeeded_with_connection(
        connection: psycopg.Connection,
        job_id: UUID,
    ) -> ProcessingJob:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE processing_jobs
                SET
                    status = 'SUCCEEDED',
                    stage = 'FINALIZING',
                    updated_at = NOW(),
                    completed_at = NOW()
                WHERE id = %s
                  AND status = 'RUNNING'
                RETURNING
                    id,
                    paper_version_id,
                    job_type,
                    status,
                    stage,
                    attempts,
                    max_attempts,
                    idempotency_key,
                    pipeline_version,
                    error_code,
                    error_message,
                    created_at,
                    updated_at,
                    started_at,
                    completed_at
                """,
                (job_id,),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                f"Processing job '{job_id}' could not be marked succeeded."
            )

        return ProcessingJobRepository._from_row(row)

    @staticmethod
    def _mark_failed_with_connection(
        connection: psycopg.Connection,
        *,
        job_id: UUID,
        error_code: str,
        error_message: str,
    ) -> ProcessingJob:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE processing_jobs
                SET
                    status = 'FAILED',
                    error_code = %s,
                    error_message = %s,
                    updated_at = NOW(),
                    completed_at = NOW()
                WHERE id = %s
                  AND status = 'RUNNING'
                RETURNING
                    id,
                    paper_version_id,
                    job_type,
                    status,
                    stage,
                    attempts,
                    max_attempts,
                    idempotency_key,
                    pipeline_version,
                    error_code,
                    error_message,
                    created_at,
                    updated_at,
                    started_at,
                    completed_at
                """,
                (
                    error_code,
                    error_message,
                    job_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                f"Processing job '{job_id}' could not be marked failed."
            )

        return ProcessingJobRepository._from_row(row)

    @staticmethod
    def _retry_with_connection(
        connection: psycopg.Connection,
        *,
        job_id: UUID,
        error_code: str,
        error_message: str,
    ) -> ProcessingJob:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE processing_jobs
                SET
                    status = CASE
                        WHEN attempts < max_attempts THEN 'QUEUED'
                        ELSE 'FAILED'
                    END,
                    error_code = %s,
                    error_message = %s,
                    updated_at = NOW(),
                    completed_at = CASE
                        WHEN attempts < max_attempts THEN NULL
                        ELSE NOW()
                    END
                WHERE id = %s
                  AND status = 'RUNNING'
                RETURNING
                    id,
                    paper_version_id,
                    job_type,
                    status,
                    stage,
                    attempts,
                    max_attempts,
                    idempotency_key,
                    pipeline_version,
                    error_code,
                    error_message,
                    created_at,
                    updated_at,
                    started_at,
                    completed_at
                """,
                (
                    error_code,
                    error_message,
                    job_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                f"Processing job '{job_id}' could not be retried."
            )

        return ProcessingJobRepository._from_row(row)

    @staticmethod
    def _from_row(row: tuple) -> ProcessingJob:
        return ProcessingJob(
            id=row[0],
            paper_version_id=row[1],
            job_type=row[2],
            status=row[3],
            stage=row[4],
            attempts=row[5],
            max_attempts=row[6],
            idempotency_key=row[7],
            pipeline_version=row[8],
            error_code=row[9],
            error_message=row[10],
            created_at=row[11],
            updated_at=row[12],
            started_at=row[13],
            completed_at=row[14],
        )