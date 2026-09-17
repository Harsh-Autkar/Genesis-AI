from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import psycopg

from .database import get_connection


@dataclass(frozen=True)
class Paper:
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime


class PaperRepository:
    """PostgreSQL persistence for papers."""

    def create(
        self,
        *,
        paper_id: UUID,
        project_id: UUID,
        connection: psycopg.Connection | None = None,
    ) -> Paper:
        if connection is not None:
            return self._create_with_connection(
                connection,
                paper_id=paper_id,
                project_id=project_id,
            )

        with get_connection() as own_connection:
            return self._create_with_connection(
                own_connection,
                paper_id=paper_id,
                project_id=project_id,
            )

    def get_by_id(
        self,
        paper_id: UUID,
        *,
        connection: psycopg.Connection | None = None,
    ) -> Paper | None:
        if connection is not None:
            return self._get_by_id_with_connection(
                connection,
                paper_id,
            )

        with get_connection() as own_connection:
            return self._get_by_id_with_connection(
                own_connection,
                paper_id,
            )

    @staticmethod
    def _create_with_connection(
        connection: psycopg.Connection,
        *,
        paper_id: UUID,
        project_id: UUID,
    ) -> Paper:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO papers (
                    id,
                    project_id
                )
                VALUES (%s, %s)
                RETURNING
                    id,
                    project_id,
                    created_at,
                    updated_at
                """,
                (paper_id, project_id),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError("Paper creation returned no row.")

        return Paper(
            id=row[0],
            project_id=row[1],
            created_at=row[2],
            updated_at=row[3],
        )

    @staticmethod
    def _get_by_id_with_connection(
        connection: psycopg.Connection,
        paper_id: UUID,
    ) -> Paper | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    project_id,
                    created_at,
                    updated_at
                FROM papers
                WHERE id = %s
                """,
                (paper_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return Paper(
            id=row[0],
            project_id=row[1],
            created_at=row[2],
            updated_at=row[3],
        )