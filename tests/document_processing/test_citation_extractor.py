from services.document_processing.scholarly import (
    BaselineCitationExtractor,
    Reference,
)
from services.document_processing.structure import (
    DocumentSection,
    SectionType,
    StructuredDocument,
)


def make_document(text: str) -> StructuredDocument:
    return StructuredDocument(
        sections=(
            DocumentSection(
                section_type=SectionType.INTRODUCTION,
                original_heading="1 Introduction",
                text=text,
                start_page=2,
                end_page=2,
                confidence=1.0,
            ),
        ),
        structure_confidence=1.0,
    )


def make_references() -> tuple[Reference, ...]:
    return (
        Reference(
            reference_id="ref-1",
            raw_text="[1] Smith. Research paper. 2024.",
            title=None,
            authors=(),
            year=2024,
            doi=None,
        ),
        Reference(
            reference_id="ref-2",
            raw_text="[2] Jones. Another paper. 2023.",
            title=None,
            authors=(),
            year=2023,
            doi=None,
        ),
        Reference(
            reference_id="ref-3",
            raw_text="[3] Brown. Third paper. 2022.",
            title=None,
            authors=(),
            year=2022,
            doi=None,
        ),
    )


def test_extracts_single_citation():
    document = make_document(
        "Prior work supports this approach [1]."
    )

    citations = BaselineCitationExtractor().extract_citations(
        document,
        make_references(),
    )

    assert len(citations) == 1
    assert citations[0].citation_id == "cit-1"
    assert citations[0].reference_id == "ref-1"
    assert citations[0].page_number == 2
    assert citations[0].context == "Prior work supports this approach [1]."


def test_extracts_multiple_citations():
    document = make_document(
        "Several studies support this finding [1, 2]."
    )

    citations = BaselineCitationExtractor().extract_citations(
        document,
        make_references(),
    )

    assert [citation.reference_id for citation in citations] == [
        "ref-1",
        "ref-2",
    ]


def test_expands_citation_range():
    document = make_document(
        "Prior studies reached similar conclusions [1-3]."
    )

    citations = BaselineCitationExtractor().extract_citations(
        document,
        make_references(),
    )

    assert [citation.reference_id for citation in citations] == [
        "ref-1",
        "ref-2",
        "ref-3",
    ]


def test_ignores_unknown_reference_numbers():
    document = make_document(
        "This cites a missing reference [99]."
    )

    citations = BaselineCitationExtractor().extract_citations(
        document,
        make_references(),
    )

    assert citations == ()


def test_skips_reference_section():
    document = StructuredDocument(
        sections=(
            DocumentSection(
                section_type=SectionType.REFERENCES,
                original_heading="References",
                text="[1] Smith. Research paper. 2024.",
                start_page=5,
                end_page=5,
                confidence=1.0,
            ),
        ),
        structure_confidence=1.0,
    )

    citations = BaselineCitationExtractor().extract_citations(
        document,
        make_references(),
    )

    assert citations == ()