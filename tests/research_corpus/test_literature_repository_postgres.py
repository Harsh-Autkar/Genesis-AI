from datetime import date
from uuid import uuid4

from services.research_corpus.domain import (
    AccessStatus,
    PaperAuthor,
    PaperProvenance,
    ProcessingStatus,
    ResearchPaper,
)
from services.research_corpus.persistence import (
    PostgreSQLLiteratureRepository,
)
from services.persistence.database import get_connection


def make_paper(
    *,
    provider_id: str | None = None,
    doi: str | None = None,
) -> ResearchPaper:
    provider_id = provider_id or f"TEST-{uuid4().hex}"

    return ResearchPaper(
        paper_id=f"test:{provider_id}",
        title="Genesis Corpus Test Paper",
        abstract="Test abstract for the scholarly corpus.",
        authors=(
            PaperAuthor(
                name="Test Author",
                author_id="A123",
                orcid="0000-0000-0000-0000",
            ),
            PaperAuthor(
                name="Second Author",
            ),
        ),
        publication_date=date(2025, 1, 15),
        venue="Test Journal",
        doi=doi,
        external_ids=(
          (("test", provider_id),)
            + (
                (("doi", doi),)
                if doi
                else ()
            )
        ),
        source="test",
        domains=("Computer Science",),
        topics=("Machine Learning",),
        access_status=AccessStatus.OPEN_ACCESS,
        full_text_location="https://example.org/paper.pdf",
        processing_status=ProcessingStatus.DISCOVERED,
        provenance=PaperProvenance(
            source="test",
            source_id=provider_id,
            retrieved_at="2026-09-22T00:00:00+00:00",
        ),
    )


def cleanup(provider_id: str) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM literature_items
                WHERE provider = 'test'
                  AND provider_id = %s
                """,
                (provider_id,),
            )


def test_save_and_get_by_paper_id():
    repository = PostgreSQLLiteratureRepository()
    provider_id = f"TEST-{uuid4().hex}"
    paper = make_paper(
        provider_id=provider_id,
        doi=f"10.1234/{uuid4().hex}",
    )

    try:
        stored = repository.save(paper)

        assert stored.paper_id == paper.paper_id
        assert stored.title == paper.title
        assert stored.authors == paper.authors
        assert set(stored.external_ids) == set(paper.external_ids)
        retrieved = repository.get_by_paper_id(
            paper.paper_id
        )

        assert retrieved == stored
    finally:
        cleanup(provider_id)


def test_find_by_external_id():
    repository = PostgreSQLLiteratureRepository()
    provider_id = f"TEST-{uuid4().hex}"
    paper = make_paper(
        provider_id=provider_id,
        doi=f"10.1234/{uuid4().hex}",
    )

    try:
        repository.save(paper)

        retrieved = repository.find_by_external_id(
            provider="test",
            external_id=provider_id,
        )

        assert retrieved is not None
        assert retrieved.paper_id == paper.paper_id
    finally:
        cleanup(provider_id)


def test_find_by_doi():
    repository = PostgreSQLLiteratureRepository()
    provider_id = f"TEST-{uuid4().hex}"
    doi = f"10.1234/{uuid4().hex}"
    paper = make_paper(
        provider_id=provider_id,
        doi=doi,
    )

    try:
        repository.save(paper)

        retrieved = repository.find_by_doi(
            doi.upper()
        )

        assert retrieved is not None
        assert retrieved.doi == doi
    finally:
        cleanup(provider_id)


def test_save_updates_existing_provider_record():
    repository = PostgreSQLLiteratureRepository()
    provider_id = f"TEST-{uuid4().hex}"
    doi = f"10.1234/{uuid4().hex}"

    first = make_paper(
        provider_id=provider_id,
        doi=doi,
    )

    second = ResearchPaper(
        paper_id=first.paper_id,
        title="Updated Genesis Corpus Test Paper",
        abstract=first.abstract,
        authors=first.authors,
        publication_date=first.publication_date,
        venue=first.venue,
        doi=doi,
        external_ids=first.external_ids,
        source="test",
        domains=first.domains,
        topics=first.topics,
        access_status=first.access_status,
        full_text_location=first.full_text_location,
        processing_status=ProcessingStatus.METADATA_READY,
        provenance=first.provenance,
    )

    try:
        repository.save(first)
        updated = repository.save(second)

        assert updated.title == (
            "Updated Genesis Corpus Test Paper"
        )
        assert updated.processing_status == (
            ProcessingStatus.METADATA_READY
        )

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM literature_items
                    WHERE provider = 'test'
                      AND provider_id = %s
                    """,
                    (provider_id,),
                )

                assert cursor.fetchone()[0] == 1
    finally:
        cleanup(provider_id)


def test_unknown_paper_returns_none():
    repository = PostgreSQLLiteratureRepository()

    assert repository.get_by_paper_id(
        "test:DOES-NOT-EXIST"
    ) is None


def test_unknown_doi_returns_none():
    repository = PostgreSQLLiteratureRepository()

    assert repository.find_by_doi(
        "10.9999/does-not-exist"
    ) is None