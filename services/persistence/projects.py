from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import psycopg

from .database import get_connection


@dataclass(frozen=True)
class Project:
    id: UUID
    owner_user_id: UUID | None
    created_at: datetime
    updated_at: datetime


class ProjectRepository:
    """PostgreSQL persistence for projects."""

    def create(
        self,
        *,
        project_id: UUID,
        owner_user_id: UUID | None = None,
        connection: psycopg.Connection | None = None,
    ) -> Project:
        if connection is not None:
            return self._create_with_connection(
                connection,
                project_id=project_id,
                owner_user_id=owner_user_id,
            )

        with get_connection() as own_connection:
            return self._create_with_connection(
                own_connection,
                project_id=project_id,
                owner_user_id=owner_user_id,
            )

    def get_by_id(
        self,
        project_id: UUID,
        *,
        connection: psycopg.Connection | None = None,
    ) -> Project | None:
        if connection is not None:
            return self._get_by_id_with_connection(
                connection,
                project_id,
            )

        with get_connection() as own_connection:
            return self._get_by_id_with_connection(
                own_connection,
                project_id,
            )

    @staticmethod
    def _create_with_connection(
        connection: psycopg.Connection,
        *,
        project_id: UUID,
        owner_user_id: UUID | None,
    ) -> Project:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO projects (
                    id,
                    owner_user_id
                )
                VALUES (%s, %s)
                RETURNING
                    id,
                    owner_user_id,
                    created_at,
                    updated_at
                """,
                (project_id, owner_user_id),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError("Project creation returned no row.")

        return Project(
            id=row[0],
            owner_user_id=row[1],
            created_at=row[2],
            updated_at=row[3],
        )

    @staticmethod
    def _get_by_id_with_connection(
        connection: psycopg.Connection,
        project_id: UUID,
    ) -> Project | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    owner_user_id,
                    created_at,
                    updated_at
                FROM projects
                WHERE id = %s
                """,
                (project_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return Project(
            id=row[0],
            owner_user_id=row[1],
            created_at=row[2],
            updated_at=row[3],
        )