from datetime import date

from services.research_corpus.domain import (
    AccessStatus,
    PaperAuthor,
    PaperProvenance,
    ProcessingStatus,
    ResearchPaper,
)


def make_paper() -> ResearchPaper:
    return ResearchPaper(
        paper_id="openalex:W123456789",
        title="Deep Learning for Research Discovery",
        abstract="An example research paper.",
        authors=(
            PaperAuthor(
                name="Jane Doe",
                author_id="A123",
                orcid="0000-0000-0000-0000",
            ),
        ),
        publication_date=date(2025, 1, 15),
        venue="Example Journal",
        doi="10.1234/example",
        external_ids=(
            ("openalex", "W123456789"),
            ("doi", "10.1234/example"),
        ),
        source="openalex",
        domains=("computer science",),
        topics=("machine learning", "information retrieval"),
        access_status=AccessStatus.OPEN_ACCESS,
        full_text_location="https://example.org/paper.pdf",
        processing_status=ProcessingStatus.DISCOVERED,
        provenance=PaperProvenance(
            source="openalex",
            source_id="W123456789",
            retrieved_at="2026-09-22T00:00:00Z",
        ),
    )


def test_research_paper_preserves_core_metadata():
    paper = make_paper()

    assert paper.paper_id == "openalex:W123456789"
    assert paper.title == "Deep Learning for Research Discovery"
    assert paper.doi == "10.1234/example"
    assert paper.source == "openalex"


def test_research_paper_preserves_authors():
    paper = make_paper()

    assert len(paper.authors) == 1
    assert paper.authors[0].name == "Jane Doe"
    assert paper.authors[0].author_id == "A123"


def test_research_paper_preserves_topics_and_domains():
    paper = make_paper()

    assert paper.domains == ("computer science",)
    assert paper.topics == (
        "machine learning",
        "information retrieval",
    )


def test_research_paper_has_access_and_processing_status():
    paper = make_paper()

    assert paper.access_status == AccessStatus.OPEN_ACCESS
    assert paper.processing_status == ProcessingStatus.DISCOVERED


def test_research_paper_is_immutable():
    paper = make_paper()

    try:
        paper.title = "Changed"
    except AttributeError:
        pass
    else:
        raise AssertionError("ResearchPaper must be immutable")