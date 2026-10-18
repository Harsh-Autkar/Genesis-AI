from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import psycopg

from .database import get_connection


@dataclass(frozen=True)
class PaperChunk:
    id: UUID
    paper_version_id: UUID
    text: str
    section_type: str
    start_page: int
    end_page: int
    position: int
    pipeline_version: str
    created_at: datetime


class PaperChunkRepository:
    """PostgreSQL persistence for document chunks."""

    def create_many(
        self,
        *,
        chunks: list[dict],
        connection: psycopg.Connection | None = None,
    ) -> tuple[PaperChunk, ...]:
        if not chunks:
            return ()

        if connection is not None:
            return self._create_many_with_connection(
                connection,
                chunks=chunks,
            )

        with get_connection() as own_connection:
            return self._create_many_with_connection(
                own_connection,
                chunks=chunks,
            )

    def get_by_paper_version(
        self,
        paper_version_id: UUID,
        *,
        pipeline_version: str | None = None,
        connection: psycopg.Connection | None = None,
    ) -> tuple[PaperChunk, ...]:
        if connection is not None:
            return self._get_by_paper_version_with_connection(
                connection,
                paper_version_id=paper_version_id,
                pipeline_version=pipeline_version,
            )

        with get_connection() as own_connection:
            return self._get_by_paper_version_with_connection(
                own_connection,
                paper_version_id=paper_version_id,
                pipeline_version=pipeline_version,
            )

    @staticmethod
    def _create_many_with_connection(
        connection: psycopg.Connection,
        *,
        chunks: list[dict],
    ) -> tuple[PaperChunk, ...]:
        values = [
            (
                chunk["id"],
                chunk["paper_version_id"],
                chunk["text"],
                chunk["section_type"],
                chunk["start_page"],
                chunk["end_page"],
                chunk["position"],
                chunk["pipeline_version"],
            )
            for chunk in chunks
        ]

        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO paper_chunks (
                    id,
                    paper_version_id,
                    text,
                    section_type,
                    start_page,
                    end_page,
                    position,
                    pipeline_version
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                """,
                values,
            )

        created = []

        for chunk in chunks:
            paper_chunk = PaperChunkRepository._get_by_id_with_connection(
                connection,
                chunk["id"],
            )

            if paper_chunk is None:
                raise RuntimeError(
                    f"Paper chunk '{chunk['id']}' could not be retrieved "
                    "after insertion."
                )

            created.append(paper_chunk)

        return tuple(
            sorted(
                created,
                key=lambda chunk: (
                    chunk.pipeline_version,
                    chunk.position,
                ),
            )
        )

    @staticmethod
    def _get_by_paper_version_with_connection(
        connection: psycopg.Connection,
        *,
        paper_version_id: UUID,
        pipeline_version: str | None,
    ) -> tuple[PaperChunk, ...]:
        if pipeline_version is None:
            query = """
                SELECT
                    id,
                    paper_version_id,
                    text,
                    section_type,
                    start_page,
                    end_page,
                    position,
                    pipeline_version,
                    created_at
                FROM paper_chunks
                WHERE paper_version_id = %s
                ORDER BY pipeline_version, position
            """
            parameters = (paper_version_id,)
        else:
            query = """
                SELECT
                    id,
                    paper_version_id,
                    text,
                    section_type,
                    start_page,
                    end_page,
                    position,
                    pipeline_version,
                    created_at
                FROM paper_chunks
                WHERE paper_version_id = %s
                  AND pipeline_version = %s
                ORDER BY position
            """
            parameters = (
                paper_version_id,
                pipeline_version,
            )

        with connection.cursor() as cursor:
            cursor.execute(
                query,
                parameters,
            )

            rows = cursor.fetchall()

        return tuple(
            PaperChunkRepository._from_row(row)
            for row in rows
        )

    @staticmethod
    def _get_by_id_with_connection(
        connection: psycopg.Connection,
        chunk_id: UUID,
    ) -> PaperChunk | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    paper_version_id,
                    text,
                    section_type,
                    start_page,
                    end_page,
                    position,
                    pipeline_version,
                    created_at
                FROM paper_chunks
                WHERE id = %s
                """,
                (chunk_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return PaperChunkRepository._from_row(row)

    @staticmethod
    def _from_row(row: tuple) -> PaperChunk:
        return PaperChunk(
            id=row[0],
            paper_version_id=row[1],
            text=row[2],
            section_type=row[3],
            start_page=row[4],
            end_page=row[5],
            position=row[6],
            pipeline_version=row[7],
            created_at=row[8],
        )