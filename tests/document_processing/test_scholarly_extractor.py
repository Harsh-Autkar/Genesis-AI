from services.document_processing.scholarly import (
    BaselineScholarlyExtractor,
)
from services.document_processing.structure import (
    DocumentSection,
    SectionType,
    StructuredDocument,
)


def test_combines_references_and_citations():
    document = StructuredDocument(
        sections=(
            DocumentSection(
                section_type=SectionType.INTRODUCTION,
                original_heading="1 Introduction",
                text="Previous work supports this approach [1].",
                start_page=2,
                end_page=2,
                confidence=1.0,
            ),
            DocumentSection(
                section_type=SectionType.REFERENCES,
                original_heading="References",
                text="[1] Smith. Research systems. 2024.",
                start_page=5,
                end_page=5,
                confidence=1.0,
            ),
        ),
        structure_confidence=1.0,
    )

    result = BaselineScholarlyExtractor().extract(document)

    assert len(result.references) == 1
    assert result.references[0].reference_id == "ref-1"

    assert len(result.citations) == 1
    assert result.citations[0].reference_id == "ref-1"
    assert result.citations[0].page_number == 2
    assert result.citations[0].context == (
        "Previous work supports this approach [1]."
    )