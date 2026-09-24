from datetime import date

import pytest

from services.research_corpus.domain.paper import (
    AccessStatus,
    PaperAuthor,
    PaperProvenance,
    ProcessingStatus,
    ResearchPaper,
)
from services.retrieval.service import RetrievalService


def make_paper(paper_id: str) -> ResearchPaper:
    return ResearchPaper(
        paper_id=paper_id,
        title=f"Paper {paper_id}",
        abstract="Test abstract",
        authors=(
            PaperAuthor(
                name="Test Author",
                author_id="A1",
                orcid=None,
            ),
        ),
        publication_date=date(2026, 9, 24),
        venue="Test Venue",
        doi=None,
        external_ids=(),
        source="fake",
        domains=("computer science",),
        topics=("machine learning",),
        access_status=AccessStatus.UNKNOWN,
        full_text_location=None,
        processing_status=ProcessingStatus.DISCOVERED,
        provenance=PaperProvenance(
            source="fake",
            source_id=paper_id,
            retrieved_at="2026-09-24T00:00:00Z",
        ),
    )


class FakeScholarlySource:
    name = "fake"

    def __init__(self, papers):
        self.papers = tuple(papers)
        self.received_query = None
        self.received_limit = None

    def search_papers(self, query: str, *, limit: int = 10):
        self.received_query = query
        self.received_limit = limit
        return self.papers[:limit]

    def get_paper(self, paper_id: str):
        return None

    def get_related_papers(self, paper_id: str, *, limit: int = 10):
        return ()

    def get_citations(self, paper_id: str, *, limit: int = 10):
        return ()


def test_search_returns_ranked_candidates():
    papers = (
        make_paper("fake:1"),
        make_paper("fake:2"),
        make_paper("fake:3"),
    )
    source = FakeScholarlySource(papers)
    service = RetrievalService(source)

    results = service.search("machine learning", limit=3)

    assert len(results) == 3
    assert [result.rank for result in results] == [1, 2, 3]
    assert [result.paper.paper_id for result in results] == [
        "fake:1",
        "fake:2",
        "fake:3",
    ]
    assert [result.source for result in results] == [
        "fake",
        "fake",
        "fake",
    ]


def test_search_normalizes_query():
    source = FakeScholarlySource((make_paper("fake:1"),))
    service = RetrievalService(source)

    service.search("  machine learning  ", limit=1)

    assert source.received_query == "machine learning"
    assert source.received_limit == 1


def test_search_respects_limit():
    papers = (
        make_paper("fake:1"),
        make_paper("fake:2"),
        make_paper("fake:3"),
    )
    source = FakeScholarlySource(papers)
    service = RetrievalService(source)

    results = service.search("machine learning", limit=2)

    assert len(results) == 2
    assert [result.paper.paper_id for result in results] == [
        "fake:1",
        "fake:2",
    ]


def test_search_allows_source_to_return_fewer_results():
    source = FakeScholarlySource((make_paper("fake:1"),))
    service = RetrievalService(source)

    results = service.search("machine learning", limit=10)

    assert len(results) == 1
    assert results[0].rank == 1


@pytest.mark.parametrize(
    ("query", "limit"),
    [
        ("", 10),
        ("   ", 10),
        ("machine learning", 0),
        ("machine learning", -1),
    ],
)
def test_search_rejects_invalid_input(query, limit):
    source = FakeScholarlySource(())
    service = RetrievalService(source)

    with pytest.raises(ValueError):
        service.search(query, limit=limit)
