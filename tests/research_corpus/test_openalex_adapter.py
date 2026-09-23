from datetime import date, datetime, timezone
from unittest.mock import Mock

import pytest

from services.research_corpus.domain import (
    AccessStatus,
    ProcessingStatus,
)
from services.research_corpus.sources.openalex_adapter import (
    OpenAlexAdapter,
)


def make_work() -> dict:
    return {
        "id": "https://openalex.org/W123456",
        "display_name": "Machine Learning for Research Discovery",
        "publication_date": "2025-05-10",
        "doi": "https://doi.org/10.1234/example",
        "ids": {
            "pmid": "123456",
            "pmcid": "PMC123456",
        },
        "abstract_inverted_index": {
            "Machine": [0],
            "learning": [1],
            "improves": [2],
            "research": [3],
            "discovery": [4],
        },
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A123",
                    "display_name": "Jane Doe",
                    "orcid": "https://orcid.org/0000-0000-0000-0000",
                }
            }
        ],
        "primary_location": {
            "source": {
                "display_name": "Journal of AI Research"
            }
        },
        "topics": [
            {
                "display_name": "Machine Learning",
                "domain": {
                    "display_name": "Computer Science"
                },
            },
            {
                "display_name": "Information Retrieval",
                "domain": {
                    "display_name": "Computer Science"
                },
            },
        ],
        "open_access": {
            "is_oa": True,
            "oa_url": "https://example.org/paper.pdf",
        },
        "_retrieved_at": "2026-09-22T19:00:00Z",
    }


def make_adapter(
    work: dict | None = None,
) -> tuple[OpenAlexAdapter, Mock]:
    client = Mock()
    client.search_works.return_value = (
        work or make_work(),
    )
    client.get_work.return_value = work or make_work()

    fixed_time = datetime(
        2026,
        9,
        22,
        19,
        0,
        tzinfo=timezone.utc,
    )

    return (
        OpenAlexAdapter(
            client,
            clock=lambda: fixed_time,
        ),
        client,
    )


def test_adapter_has_openalex_name():
    adapter, _ = make_adapter()

    assert adapter.name == "openalex"


def test_search_papers_normalizes_work():
    adapter, client = make_adapter()

    papers = adapter.search_papers(
        "machine learning",
        limit=5,
    )

    assert len(papers) == 1

    paper = papers[0]

    assert paper.paper_id == "openalex:W123456"
    assert paper.title == (
        "Machine Learning for Research Discovery"
    )
    assert paper.source == "openalex"

    client.search_works.assert_called_once_with(
        "machine learning",
        limit=5,
    )


def test_adapter_normalizes_authors_and_identifiers():
    adapter, _ = make_adapter()

    paper = adapter.search_papers("machine learning")[0]

    assert len(paper.authors) == 1
    assert paper.authors[0].name == "Jane Doe"
    assert paper.authors[0].author_id == "A123"

    assert paper.doi == "10.1234/example"

    assert (
        ("openalex", "W123456")
        in paper.external_ids
    )

    assert (
        ("doi", "10.1234/example")
        in paper.external_ids
    )

    assert (
        ("pmid", "123456")
        in paper.external_ids
    )


def test_adapter_reconstructs_abstract():
    adapter, _ = make_adapter()

    paper = adapter.search_papers("machine learning")[0]

    assert paper.abstract == (
        "Machine learning improves research discovery"
    )


def test_adapter_normalizes_topics_and_domains():
    adapter, _ = make_adapter()

    paper = adapter.search_papers("machine learning")[0]

    assert paper.domains == ("Computer Science",)

    assert paper.topics == (
        "Machine Learning",
        "Information Retrieval",
    )


def test_adapter_normalizes_access_information():
    adapter, _ = make_adapter()

    paper = adapter.search_papers("machine learning")[0]

    assert paper.access_status == AccessStatus.OPEN_ACCESS
    assert paper.full_text_location == (
        "https://example.org/paper.pdf"
    )


def test_adapter_normalizes_publication_and_venue():
    adapter, _ = make_adapter()

    paper = adapter.search_papers("machine learning")[0]

    assert paper.publication_date == date(2025, 5, 10)
    assert paper.venue == "Journal of AI Research"


def test_adapter_sets_processing_status():
    adapter, _ = make_adapter()

    paper = adapter.search_papers("machine learning")[0]

    assert (
        paper.processing_status
        == ProcessingStatus.DISCOVERED
    )


def test_get_paper_normalizes_single_work():
    adapter, client = make_adapter()

    paper = adapter.get_paper("W123456")

    assert paper is not None
    assert paper.paper_id == "openalex:W123456"

    client.get_work.assert_called_once_with("W123456")


def test_get_paper_returns_none_when_missing():
    adapter, client = make_adapter()

    client.get_work.return_value = None

    assert adapter.get_paper("W999999") is None


def test_related_papers_not_implemented_yet():
    adapter, _ = make_adapter()

    with pytest.raises(
        NotImplementedError,
        match="related-paper retrieval",
    ):
        adapter.get_related_papers("W123456")


def test_citations_not_implemented_yet():
    adapter, _ = make_adapter()

    with pytest.raises(
        NotImplementedError,
        match="citation retrieval",
    ):
        adapter.get_citations("W123456")
        
def test_adapter_sets_retrieval_provenance():
    adapter, _ = make_adapter()

    paper = adapter.search_papers(
        "machine learning"
    )[0]

    assert paper.provenance.source == "openalex"
    assert paper.provenance.source_id == "W123456"
    assert paper.provenance.retrieved_at == (
        "2026-09-22T19:00:00+00:00"
    )