from datetime import date

from services.research_corpus.domain import (
    AccessStatus,
    PaperAuthor,
    PaperProvenance,
    ProcessingStatus,
    ResearchPaper,
)
from services.research_corpus.sources import ScholarlySource


class FakeScholarlySource:
    """Test implementation proving the source contract is usable."""

    name = "fake"

    def search_papers(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> tuple[ResearchPaper, ...]:
        return (self._paper(),)[:limit]

    def get_paper(
        self,
        paper_id: str,
    ) -> ResearchPaper | None:
        return self._paper() if paper_id == self._paper().paper_id else None

    def get_related_papers(
        self,
        paper_id: str,
        *,
        limit: int = 10,
    ) -> tuple[ResearchPaper, ...]:
        return (self._paper(),)[:limit]

    def get_citations(
        self,
        paper_id: str,
        *,
        limit: int = 10,
    ) -> tuple[ResearchPaper, ...]:
        return (self._paper(),)[:limit]

    @staticmethod
    def _paper() -> ResearchPaper:
        return ResearchPaper(
            paper_id="fake:123",
            title="Test Research Paper",
            abstract="Test abstract",
            authors=(
                PaperAuthor(name="Test Author"),
            ),
            publication_date=date(2025, 1, 1),
            venue="Test Venue",
            doi=None,
            external_ids=(("fake", "123"),),
            source="fake",
            domains=("computer science",),
            topics=("machine learning",),
            access_status=AccessStatus.UNKNOWN,
            full_text_location=None,
            processing_status=ProcessingStatus.DISCOVERED,
            provenance=PaperProvenance(
                source="fake",
                source_id="123",
                retrieved_at="2026-09-22T00:00:00Z",
            ),
        )


def test_fake_source_exposes_source_name():
    source: ScholarlySource = FakeScholarlySource()

    assert source.name == "fake"


def test_source_can_search_papers():
    source: ScholarlySource = FakeScholarlySource()

    papers = source.search_papers("machine learning", limit=5)

    assert len(papers) == 1
    assert papers[0].paper_id == "fake:123"


def test_source_can_get_single_paper():
    source: ScholarlySource = FakeScholarlySource()

    paper = source.get_paper("fake:123")

    assert paper is not None
    assert paper.title == "Test Research Paper"


def test_source_returns_none_for_unknown_paper():
    source: ScholarlySource = FakeScholarlySource()

    assert source.get_paper("fake:unknown") is None


def test_source_can_get_related_papers():
    source: ScholarlySource = FakeScholarlySource()

    papers = source.get_related_papers("fake:123")

    assert len(papers) == 1


def test_source_can_get_citations():
    source: ScholarlySource = FakeScholarlySource()

    papers = source.get_citations("fake:123")

    assert len(papers) == 1