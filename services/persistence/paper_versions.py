from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import psycopg

from .database import get_connection


@dataclass(frozen=True)
class PaperVersion:
    id: UUID
    paper_id: UUID
    version_number: int
    storage_key: str
    file_hash: str
    file_size: int
    mime_type: str
    processing_status: str
    created_at: datetime
    updated_at: datetime


class PaperVersionRepository:
    """PostgreSQL persistence for paper versions."""

    def create(
        self,
        *,
        version_id: UUID,
        paper_id: UUID,
        version_number: int,
        storage_key: str,
        file_hash: str,
        file_size: int,
        mime_type: str,
        processing_status: str,
        connection: psycopg.Connection | None = None,
    ) -> PaperVersion:
        if connection is not None:
            return self._create_with_connection(
                connection,
                version_id=version_id,
                paper_id=paper_id,
                version_number=version_number,
                storage_key=storage_key,
                file_hash=file_hash,
                file_size=file_size,
                mime_type=mime_type,
                processing_status=processing_status,
            )

        with get_connection() as own_connection:
            return self._create_with_connection(
                own_connection,
                version_id=version_id,
                paper_id=paper_id,
                version_number=version_number,
                storage_key=storage_key,
                file_hash=file_hash,
                file_size=file_size,
                mime_type=mime_type,
                processing_status=processing_status,
            )

    def get_by_id(
        self,
        version_id: UUID,
        *,
        connection: psycopg.Connection | None = None,
    ) -> PaperVersion | None:
        if connection is not None:
            return self._get_by_id_with_connection(
                connection,
                version_id,
            )

        with get_connection() as own_connection:
            return self._get_by_id_with_connection(
                own_connection,
                version_id,
            )

    def get_latest_for_paper(
        self,
        paper_id: UUID,
        *,
        connection: psycopg.Connection | None = None,
    ) -> PaperVersion | None:
        if connection is not None:
            return self._get_latest_with_connection(
                connection,
                paper_id,
            )

        with get_connection() as own_connection:
            return self._get_latest_with_connection(
                own_connection,
                paper_id,
            )

    @staticmethod
    def _create_with_connection(
        connection: psycopg.Connection,
        *,
        version_id: UUID,
        paper_id: UUID,
        version_number: int,
        storage_key: str,
        file_hash: str,
        file_size: int,
        mime_type: str,
        processing_status: str,
    ) -> PaperVersion:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO paper_versions (
                    id,
                    paper_id,
                    version_number,
                    storage_key,
                    file_hash,
                    file_size,
                    mime_type,
                    processing_status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING
                    id,
                    paper_id,
                    version_number,
                    storage_key,
                    file_hash,
                    file_size,
                    mime_type,
                    processing_status,
                    created_at,
                    updated_at
                """,
                (
                    version_id,
                    paper_id,
                    version_number,
                    storage_key,
                    file_hash,
                    file_size,
                    mime_type,
                    processing_status,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Paper version creation returned no row."
            )

        return PaperVersionRepository._from_row(row)

    @staticmethod
    def _get_by_id_with_connection(
        connection: psycopg.Connection,
        version_id: UUID,
    ) -> PaperVersion | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    paper_id,
                    version_number,
                    storage_key,
                    file_hash,
                    file_size,
                    mime_type,
                    processing_status,
                    created_at,
                    updated_at
                FROM paper_versions
                WHERE id = %s
                """,
                (version_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return PaperVersionRepository._from_row(row)

    @staticmethod
    def _get_latest_with_connection(
        connection: psycopg.Connection,
        paper_id: UUID,
    ) -> PaperVersion | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    paper_id,
                    version_number,
                    storage_key,
                    file_hash,
                    file_size,
                    mime_type,
                    processing_status,
                    created_at,
                    updated_at
                FROM paper_versions
                WHERE paper_id = %s
                ORDER BY version_number DESC
                LIMIT 1
                """,
                (paper_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return PaperVersionRepository._from_row(row)

    @staticmethod
    def _from_row(row: tuple) -> PaperVersion:
        return PaperVersion(
            id=row[0],
            paper_id=row[1],
            version_number=row[2],
            storage_key=row[3],
            file_hash=row[4],
            file_size=row[5],
            mime_type=row[6],
            processing_status=row[7],
            created_at=row[8],
            updated_at=row[9],
        )