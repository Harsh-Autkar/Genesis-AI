from dataclasses import dataclass
from typing import Protocol

import psycopg


@dataclass(frozen=True)
class StoredEmbedding:
    source_type: str
    source_id: str
    model_name: str
    model_version: str
    vector: tuple[float, ...]


class EmbeddingRepository(Protocol):
    def save(
        self,
        embeddings: tuple[StoredEmbedding, ...],
    ) -> None:
        """Persist embedding records."""

    def find_similar(
        self,
        *,
        vector: tuple[float, ...],
        model_name: str,
        model_version: str,
        limit: int = 10,
    ) -> tuple[StoredEmbedding, ...]:
        """Return the most similar stored embeddings for one model version."""


class PostgreSQLEmbeddingRepository:
    """Persist and search embeddings using PostgreSQL and pgvector."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def save(
        self,
        embeddings: tuple[StoredEmbedding, ...],
    ) -> None:
        if not embeddings:
            return

        with psycopg.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO embeddings (
                        source_type,
                        source_id,
                        model_name,
                        model_version,
                        vector
                    )
                    VALUES (%s, %s, %s, %s, %s::vector)
                    ON CONFLICT (
                        source_type,
                        source_id,
                        model_name,
                        model_version
                    ) DO NOTHING
                    """,
                    [
                        (
                            embedding.source_type,
                            embedding.source_id,
                            embedding.model_name,
                            embedding.model_version,
                            self._vector_literal(embedding.vector),
                        )
                        for embedding in embeddings
                    ],
                )

    def find_similar(
        self,
        *,
        vector: tuple[float, ...],
        model_name: str,
        model_version: str,
        limit: int = 10,
    ) -> tuple[StoredEmbedding, ...]:
        if limit <= 0:
            raise ValueError("limit must be greater than 0.")

        with psycopg.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        source_type,
                        source_id,
                        model_name,
                        model_version,
                        vector
                    FROM embeddings
                    WHERE model_name = %s
                      AND model_version = %s
                    ORDER BY vector <=> %s::vector
                    LIMIT %s
                    """,
                    (
                        model_name,
                        model_version,
                        self._vector_literal(vector),
                        limit,
                    ),
                )

                rows = cursor.fetchall()

        return tuple(
            StoredEmbedding(
                source_type=row[0],
                source_id=row[1],
                model_name=row[2],
                model_version=row[3],
                vector=self._parse_vector(row[4]),
            )
            for row in rows
        )

    @staticmethod
    def _vector_literal(vector: tuple[float, ...]) -> str:
        if not vector:
            raise ValueError("Embedding vector must not be empty.")

        return "[" + ",".join(str(value) for value in vector) + "]"

    @staticmethod
    def _parse_vector(value) -> tuple[float, ...]:
        if isinstance(value, str):
            stripped = value.strip().strip("[]")

            if not stripped:
                return ()

            return tuple(
                float(item.strip())
                for item in stripped.split(",")
            )

        try:
            return tuple(float(item) for item in value)
        except TypeError as exc:
            raise TypeError("Unsupported pgvector value.") from exc
