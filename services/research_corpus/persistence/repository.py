from dataclasses import dataclass
from uuid import UUID, uuid4

import psycopg

from services.research_corpus.domain import (
    AccessStatus,
    PaperAuthor,
    PaperProvenance,
    ProcessingStatus,
    ResearchPaper,
)

from services.persistence.database import get_connection


@dataclass(frozen=True)
class _LiteratureIdentity:
    provider: str
    provider_id: str


class PostgreSQLLiteratureRepository:
    """PostgreSQL persistence for scholarly literature."""

    def save(
        self,
        paper: ResearchPaper,
        *,
        connection: psycopg.Connection | None = None,
    ) -> ResearchPaper:
        if connection is not None:
            return self._save_with_connection(
                connection,
                paper,
            )

        with get_connection() as own_connection:
            return self._save_with_connection(
                own_connection,
                paper,
            )

    def get_by_paper_id(
        self,
        paper_id: str,
        *,
        connection: psycopg.Connection | None = None,
    ) -> ResearchPaper | None:
        provider, provider_id = self._parse_paper_id(
            paper_id
        )

        if connection is not None:
            return self._get_by_provider_id(
                connection,
                provider=provider,
                provider_id=provider_id,
            )

        with get_connection() as own_connection:
            return self._get_by_provider_id(
                own_connection,
                provider=provider,
                provider_id=provider_id,
            )

    def find_by_external_id(
        self,
        *,
        provider: str,
        external_id: str,
        connection: psycopg.Connection | None = None,
    ) -> ResearchPaper | None:
        if not provider.strip():
            raise ValueError("provider must not be empty")

        if not external_id.strip():
            raise ValueError("external_id must not be empty")

        if connection is not None:
            return self._find_by_external_id_with_connection(
                connection,
                provider=provider,
                external_id=external_id,
            )

        with get_connection() as own_connection:
            return self._find_by_external_id_with_connection(
                own_connection,
                provider=provider,
                external_id=external_id,
            )

    def find_by_doi(
        self,
        doi: str,
        *,
        connection: psycopg.Connection | None = None,
    ) -> ResearchPaper | None:
        normalized_doi = self._normalize_doi(doi)

        if not normalized_doi:
            raise ValueError("doi must not be empty")

        if connection is not None:
            return self._find_by_doi_with_connection(
                connection,
                normalized_doi,
            )

        with get_connection() as own_connection:
            return self._find_by_doi_with_connection(
                own_connection,
                normalized_doi,
            )

    @staticmethod
    def _save_with_connection(
        connection: psycopg.Connection,
        paper: ResearchPaper,
    ) -> ResearchPaper:
        existing = PostgreSQLLiteratureRepository._find_existing(
            connection,
            paper,
        )

        if existing is None:
            literature_id = uuid4()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO literature_items (
                        id,
                        provider,
                        provider_id,
                        title,
                        abstract,
                        publication_date,
                        venue,
                        doi,
                        source,
                        domains,
                        topics,
                        access_status,
                        full_text_location,
                        processing_status,
                        provenance_source,
                        provenance_source_id,
                        retrieved_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s
                    )
                    """,
                    (
                        literature_id,
                        paper.source,
                        PostgreSQLLiteratureRepository._provider_id(
                            paper
                        ),
                        paper.title,
                        paper.abstract,
                        paper.publication_date,
                        paper.venue,
                        PostgreSQLLiteratureRepository._normalize_doi(
                            paper.doi
                        ),
                        paper.source,
                        list(paper.domains),
                        list(paper.topics),
                        paper.access_status.value,
                        paper.full_text_location,
                        paper.processing_status.value,
                        paper.provenance.source,
                        paper.provenance.source_id,
                        paper.provenance.retrieved_at,
                    ),
                )

        else:
            literature_id = existing[0]

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE literature_items
                    SET
                        title = %s,
                        abstract = %s,
                        publication_date = %s,
                        venue = %s,
                        doi = %s,
                        source = %s,
                        domains = %s,
                        topics = %s,
                        access_status = %s,
                        full_text_location = %s,
                        processing_status = %s,
                        provenance_source = %s,
                        provenance_source_id = %s,
                        retrieved_at = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (
                        paper.title,
                        paper.abstract,
                        paper.publication_date,
                        paper.venue,
                        PostgreSQLLiteratureRepository._normalize_doi(
                            paper.doi
                        ),
                        paper.source,
                        list(paper.domains),
                        list(paper.topics),
                        paper.access_status.value,
                        paper.full_text_location,
                        paper.processing_status.value,
                        paper.provenance.source,
                        paper.provenance.source_id,
                        paper.provenance.retrieved_at,
                        literature_id,
                    ),
                )

        PostgreSQLLiteratureRepository._persist_authors(
            connection,
            literature_id,
            paper.authors,
        )

        PostgreSQLLiteratureRepository._persist_external_ids(
            connection,
            literature_id,
            paper.external_ids,
        )

        return PostgreSQLLiteratureRepository._get_by_id(
            connection,
            literature_id,
        )

    @staticmethod
    def _find_existing(
        connection: psycopg.Connection,
        paper: ResearchPaper,
    ) -> tuple[UUID] | None:
        provider_id = PostgreSQLLiteratureRepository._provider_id(
            paper
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM literature_items
                WHERE provider = %s
                  AND provider_id = %s
                """,
                (
                    paper.source,
                    provider_id,
                ),
            )

            row = cursor.fetchone()

            if row is not None:
                return row

            doi = PostgreSQLLiteratureRepository._normalize_doi(
                paper.doi
            )

            if doi is None:
                return None

            cursor.execute(
                """
                SELECT id
                FROM literature_items
                WHERE doi = %s
                """,
                (doi,),
            )

            return cursor.fetchone()

    @staticmethod
    def _persist_authors(
        connection: psycopg.Connection,
        literature_id: UUID,
        authors: tuple[PaperAuthor, ...],
    ) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM literature_authors
                WHERE literature_item_id = %s
                """,
                (literature_id,),
            )

            for position, author in enumerate(
                authors,
                start=1,
            ):
                cursor.execute(
                    """
                    INSERT INTO literature_authors (
                        id,
                        literature_item_id,
                        author_position,
                        name,
                        provider_author_id,
                        orcid
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        uuid4(),
                        literature_id,
                        position,
                        author.name,
                        author.author_id,
                        author.orcid,
                    ),
                )

    @staticmethod
    def _persist_external_ids(
        connection: psycopg.Connection,
        literature_id: UUID,
        external_ids: tuple[tuple[str, str], ...],
    ) -> None:
        with connection.cursor() as cursor:
            for provider, external_id in external_ids:
                cursor.execute(
                    """
                    INSERT INTO literature_external_ids (
                        id,
                        literature_item_id,
                        provider,
                        external_id
                    )
                    VALUES (
                        %s, %s, %s, %s
                    )
                    ON CONFLICT (
                        provider,
                        external_id
                    )
                    DO NOTHING
                    """,
                    (
                        uuid4(),
                        literature_id,
                        provider,
                        external_id,
                    ),
                )

    @staticmethod
    def _get_by_provider_id(
        connection: psycopg.Connection,
        *,
        provider: str,
        provider_id: str,
    ) -> ResearchPaper | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM literature_items
                WHERE provider = %s
                  AND provider_id = %s
                """,
                (
                    provider,
                    provider_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return PostgreSQLLiteratureRepository._get_by_id(
            connection,
            row[0],
        )

    @staticmethod
    def _find_by_external_id_with_connection(
        connection: psycopg.Connection,
        *,
        provider: str,
        external_id: str,
    ) -> ResearchPaper | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT literature_item_id
                FROM literature_external_ids
                WHERE provider = %s
                  AND external_id = %s
                """,
                (
                    provider,
                    external_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return PostgreSQLLiteratureRepository._get_by_id(
            connection,
            row[0],
        )

    @staticmethod
    def _find_by_doi_with_connection(
        connection: psycopg.Connection,
        doi: str,
    ) -> ResearchPaper | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM literature_items
                WHERE doi = %s
                """,
                (doi,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return PostgreSQLLiteratureRepository._get_by_id(
            connection,
            row[0],
        )

    @staticmethod
    def _get_by_id(
        connection: psycopg.Connection,
        literature_id: UUID,
    ) -> ResearchPaper:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    provider,
                    provider_id,
                    title,
                    abstract,
                    publication_date,
                    venue,
                    doi,
                    source,
                    domains,
                    topics,
                    access_status,
                    full_text_location,
                    processing_status,
                    provenance_source,
                    provenance_source_id,
                    retrieved_at
                FROM literature_items
                WHERE id = %s
                """,
                (literature_id,),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Literature item disappeared during retrieval."
            )

        (
            provider,
            provider_id,
            title,
            abstract,
            publication_date,
            venue,
            doi,
            source,
            domains,
            topics,
            access_status,
            full_text_location,
            processing_status,
            provenance_source,
            provenance_source_id,
            retrieved_at,
        ) = row

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    author_position,
                    name,
                    provider_author_id,
                    orcid
                FROM literature_authors
                WHERE literature_item_id = %s
                ORDER BY author_position
                """,
                (literature_id,),
            )

            author_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    provider,
                    external_id
                FROM literature_external_ids
                WHERE literature_item_id = %s
                ORDER BY provider, external_id
                """,
                (literature_id,),
            )

            external_id_rows = cursor.fetchall()

        authors = tuple(
            PaperAuthor(
                name=row[1],
                author_id=row[2],
                orcid=row[3],
            )
            for row in author_rows
        )

        external_ids = tuple(
            (
                row[0],
                row[1],
            )
            for row in external_id_rows
        )

        return ResearchPaper(
            paper_id=f"{provider}:{provider_id}",
            title=title,
            abstract=abstract,
            authors=authors,
            publication_date=publication_date,
            venue=venue,
            doi=doi,
            external_ids=external_ids,
            source=source,
            domains=tuple(domains or ()),
            topics=tuple(topics or ()),
            access_status=AccessStatus(access_status),
            full_text_location=full_text_location,
            processing_status=ProcessingStatus(
                processing_status
            ),
            provenance=PaperProvenance(
                source=provenance_source,
                source_id=provenance_source_id,
                retrieved_at=retrieved_at.isoformat(),
            ),
        )

    @staticmethod
    def _provider_id(
        paper: ResearchPaper,
    ) -> str:
        prefix = f"{paper.source}:"

        if not paper.paper_id.startswith(prefix):
            raise ValueError(
                "paper_id must start with its source prefix."
            )

        provider_id = paper.paper_id.removeprefix(prefix)

        if not provider_id:
            raise ValueError(
                "paper_id must contain a provider identifier."
            )

        return provider_id

    @staticmethod
    def _parse_paper_id(
        paper_id: str,
    ) -> tuple[str, str]:
        if ":" not in paper_id:
            raise ValueError(
                "paper_id must use provider:id format."
            )

        provider, provider_id = paper_id.split(
            ":",
            1,
        )

        if not provider or not provider_id:
            raise ValueError(
                "paper_id must use provider:id format."
            )

        return provider, provider_id

    @staticmethod
    def _normalize_doi(
        doi: str | None,
    ) -> str | None:
        if doi is None:
            return None

        value = doi.strip()

        if not value:
            return None

        return value.removeprefix(
            "https://doi.org/"
        ).removeprefix(
            "http://doi.org/"
        ).strip().lower()