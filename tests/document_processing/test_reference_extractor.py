from services.document_processing.structure import (
    DocumentSection,
    SectionType,
    StructuredDocument,
)
from services.document_processing.scholarly import (
    BaselineReferenceExtractor,
)


def make_document(reference_text: str) -> StructuredDocument:
    return StructuredDocument(
        sections=(
            DocumentSection(
                section_type=SectionType.REFERENCES,
                original_heading="References",
                text=reference_text,
                start_page=5,
                end_page=6,
                confidence=1.0,
            ),
        ),
        structure_confidence=1.0,
    )


def test_extracts_numbered_references():
    document = make_document(
        """
        [1] Smith, J. A study of research systems. 2024.
        [2] Jones, P. Machine learning methods. 2023.
        """
    )

    references = BaselineReferenceExtractor().extract_references(document)

    assert len(references) == 2
    assert references[0].reference_id == "ref-1"
    assert references[1].reference_id == "ref-2"
    assert references[0].year == 2024
    assert references[1].year == 2023


def test_extracts_doi():
    document = make_document(
        "[1] Example paper. 2024. "
        "https://doi.org/10.1234/example.paper"
    )

    references = BaselineReferenceExtractor().extract_references(document)

    assert references[0].doi == "10.1234/example.paper"


def test_preserves_raw_reference_text():
    raw = "[1] Smith, J. Important research paper. 2024."
    document = make_document(raw)

    references = BaselineReferenceExtractor().extract_references(document)

    assert references[0].raw_text == raw


def test_returns_empty_when_no_reference_section():
    document = StructuredDocument(
        sections=(),
        structure_confidence=0.0,
    )

    references = BaselineReferenceExtractor().extract_references(document)

    assert references == ()


def test_reference_without_year_or_doi_is_allowed():
    document = make_document(
        "[1] Smith, J. An older reference without structured metadata."
    )

    references = BaselineReferenceExtractor().extract_references(document)

    assert references[0].year is None
    assert references[0].doi is None