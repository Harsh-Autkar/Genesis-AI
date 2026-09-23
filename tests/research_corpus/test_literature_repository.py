from datetime import date

from services.research_corpus.domain import (
    AccessStatus,
    PaperAuthor,
    PaperProvenance,
    ProcessingStatus,
    ResearchPaper,
)
from services.research_corpus.persistence import LiteratureRepository


class FakeLiteratureRepository:
    """Minimal in-memory implementation used to test the contract."""

    def __init__(self) -> None:
        self._papers: dict[str, ResearchPaper] = {}

    def save(
        self,
        paper: ResearchPaper,
    ) -> ResearchPaper:
        self._papers[paper.paper_id] = paper
        return paper

    def get_by_paper_id(
        self,
        paper_id: str,
    ) -> ResearchPaper | None:
        return self._papers.get(paper_id)

    def find_by_external_id(
        self,
        *,
        provider: str,
        external_id: str,
    ) -> ResearchPaper | None:
        for paper in self._papers.values():
            if (
                provider,
                external_id,
            ) in paper.external_ids:
                return paper

        return None

    def find_by_doi(
        self,
        doi: str,
    ) -> ResearchPaper | None:
        for paper in self._papers.values():
            if paper.doi == doi:
                return paper

        return None


def make_paper() -> ResearchPaper:
    return ResearchPaper(
        paper_id="openalex:W123",
        title="Test Literature Item",
        abstract="Test abstract",
        authors=(
            PaperAuthor(name="Test Author"),
        ),
        publication_date=date(2025, 1, 1),
        venue="Test Journal",
        doi="10.1234/test",
        external_ids=(
            ("openalex", "W123"),
            ("doi", "10.1234/test"),
        ),
        source="openalex",
        domains=("Computer Science",),
        topics=("Machine Learning",),
        access_status=AccessStatus.OPEN_ACCESS,
        full_text_location="https://example.org/paper.pdf",
        processing_status=ProcessingStatus.DISCOVERED,
        provenance=PaperProvenance(
            source="openalex",
            source_id="W123",
            retrieved_at="2026-09-22T00:00:00+00:00",
        ),
    )


def test_repository_can_save_and_get_paper():
    repository: LiteratureRepository = FakeLiteratureRepository()
    paper = make_paper()

    repository.save(paper)

    stored = repository.get_by_paper_id("openalex:W123")

    assert stored == paper


def test_repository_returns_none_for_unknown_paper():
    repository: LiteratureRepository = FakeLiteratureRepository()

    assert repository.get_by_paper_id("openalex:UNKNOWN") is None


def test_repository_can_find_by_external_id():
    repository: LiteratureRepository = FakeLiteratureRepository()
    paper = make_paper()

    repository.save(paper)

    stored = repository.find_by_external_id(
        provider="openalex",
        external_id="W123",
    )

    assert stored == paper


def test_repository_can_find_by_doi():
    repository: LiteratureRepository = FakeLiteratureRepository()
    paper = make_paper()

    repository.save(paper)

    stored = repository.find_by_doi(
        "10.1234/test"
    )

    assert stored == paper


def test_repository_returns_none_for_unknown_doi():
    repository: LiteratureRepository = FakeLiteratureRepository()

    assert repository.find_by_doi(
        "10.9999/unknown"
    ) is None
    