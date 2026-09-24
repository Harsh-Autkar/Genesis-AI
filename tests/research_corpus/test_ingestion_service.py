'@'
from datetime import date

import pytest

from services.research_corpus.domain.paper import (
    AccessStatus,
    PaperAuthor,
    PaperProvenance,
    ProcessingStatus,
    ResearchPaper,
)
from services.research_corpus.ingestion.service import (
    ResearchCorpusIngestionService,
)


def make_paper(
    paper_id: str,
    *,
    doi: str | None = None,
    external_ids: tuple[tuple[str, str], ...] = (),
) -> ResearchPaper:
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
        doi=doi,
        external_ids=external_ids,
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


class FakeSource:
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


class FakeRepository:
    def __init__(
        self,
        existing=None,
        existing_dois=None,
        existing_external_ids=None,
        failing_ids=None,
    ):
        self.by_paper_id = {
            paper.paper_id: paper for paper in (existing or ())
        }
        self.by_doi = {
            paper.doi: paper
            for paper in (existing_dois or ())
            if paper.doi
        }
        self.by_external_id = {
            key: paper
            for paper in (existing_external_ids or ())
            for key in paper.external_ids
        }
        self.failing_ids = set(failing_ids or ())
        self.saved = []

    def get_by_paper_id(self, paper_id, *, connection=None):
        return self.by_paper_id.get(paper_id)

    def find_by_doi(self, doi, *, connection=None):
        return self.by_doi.get(doi)

    def find_by_external_id(
        self,
        *,
        provider,
        external_id,
        connection=None,
    ):
        return self.by_external_id.get((provider, external_id))

    def save(self, paper, *, connection=None):
        if paper.paper_id in self.failing_ids:
            raise RuntimeError("simulated persistence failure")

        self.saved.append(paper)
        self.by_paper_id[paper.paper_id] = paper

        if paper.doi:
            self.by_doi[paper.doi] = paper

        for key in paper.external_ids:
            self.by_external_id[key] = paper

        return paper


def test_ingests_new_papers():
    papers = (
        make_paper("fake:1"),
        make_paper("fake:2"),
        make_paper("fake:3"),
    )

    source = FakeSource(papers)
    repository = FakeRepository()
    service = ResearchCorpusIngestionService(source, repository)

    result = service.ingest("  machine learning  ", limit=3)

    assert result.query == "machine learning"
    assert result.retrieved == 3
    assert result.new_papers == 3
    assert result.existing_papers == 0
    assert result.failed_papers == 0
    assert result.saved_paper_ids == (
        "fake:1",
        "fake:2",
        "fake:3",
    )
    assert len(repository.saved) == 3
    assert source.received_query == "machine learning"
    assert source.received_limit == 3


def test_skips_existing_paper():
    existing = make_paper("fake:1")
    new_paper = make_paper("fake:2")

    source = FakeSource((existing, new_paper))
    repository = FakeRepository(existing=(existing,))
    service = ResearchCorpusIngestionService(source, repository)

    result = service.ingest("machine learning", limit=2)

    assert result.retrieved == 2
    assert result.new_papers == 1
    assert result.existing_papers == 1
    assert result.failed_papers == 0
    assert result.saved_paper_ids == ("fake:2",)


def test_skips_paper_with_existing_doi():
    existing = make_paper("other:1", doi="10.1234/example")
    candidate = make_paper("fake:1", doi="10.1234/example")

    source = FakeSource((candidate,))
    repository = FakeRepository(existing_dois=(existing,))
    service = ResearchCorpusIngestionService(source, repository)

    result = service.ingest("machine learning", limit=1)

    assert result.retrieved == 1
    assert result.new_papers == 0
    assert result.existing_papers == 1
    assert result.failed_papers == 0
    assert repository.saved == []


def test_skips_paper_with_existing_external_id():
    existing = make_paper(
        "other:1",
        external_ids=(("doi", "10.1234/example"),),
    )
    candidate = make_paper(
        "fake:1",
        external_ids=(("doi", "10.1234/example"),),
    )

    source = FakeSource((candidate,))
    repository = FakeRepository(existing_external_ids=(existing,))
    service = ResearchCorpusIngestionService(source, repository)

    result = service.ingest("machine learning", limit=1)

    assert result.new_papers == 0
    assert result.existing_papers == 1
    assert result.failed_papers == 0
    assert repository.saved == []


def test_continues_when_one_paper_fails():
    first = make_paper("fake:1")
    failing = make_paper("fake:2")
    third = make_paper("fake:3")

    source = FakeSource((first, failing, third))
    repository = FakeRepository(failing_ids={"fake:2"})
    service = ResearchCorpusIngestionService(source, repository)

    result = service.ingest("machine learning", limit=3)

    assert result.retrieved == 3
    assert result.new_papers == 2
    assert result.existing_papers == 0
    assert result.failed_papers == 1
    assert result.saved_paper_ids == ("fake:1", "fake:3")
    assert result.failed_paper_ids == ("fake:2",)


def test_duplicate_in_same_source_response_is_not_saved_twice():
    paper = make_paper("fake:1")

    source = FakeSource((paper, paper))
    repository = FakeRepository()
    service = ResearchCorpusIngestionService(source, repository)

    result = service.ingest("machine learning", limit=2)

    assert result.retrieved == 2
    assert result.new_papers == 1
    assert result.existing_papers == 1
    assert result.failed_papers == 0
    assert len(repository.saved) == 1


@pytest.mark.parametrize(
    ("query", "limit"),
    [
        ("", 10),
        ("   ", 10),
        ("machine learning", 0),
        ("machine learning", -1),
    ],
)
def test_rejects_invalid_input(query, limit):
    source = FakeSource(())
    repository = FakeRepository()
    service = ResearchCorpusIngestionService(source, repository)

    with pytest.raises(ValueError):
        service.ingest(query, limit=limit)
