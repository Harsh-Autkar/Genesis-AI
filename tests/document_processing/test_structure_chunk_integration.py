from services.document_processing.chunks import ParagraphChunker
from services.document_processing.structure import (
    DocumentSection,
    SectionType,
    StructuredDocument,
)


def test_structured_document_produces_provenance_preserving_chunks():
    document = StructuredDocument(
        sections=(
            DocumentSection(
                section_type=SectionType.INTRODUCTION,
                original_heading="1 Introduction",
                text=(
                    "Research motivation and context."
                    "\n\n"
                    "Previous work is summarized here."
                ),
                start_page=2,
                end_page=3,
                confidence=1.0,
            ),
            DocumentSection(
                section_type=SectionType.METHODS,
                original_heading="2 Methods",
                text="The proposed methodology is described here.",
                start_page=4,
                end_page=5,
                confidence=1.0,
            ),
        ),
        structure_confidence=1.0,
    )

    chunks = ParagraphChunker().chunk(document)

    assert len(chunks) == 3

    assert chunks[0].section_type == SectionType.INTRODUCTION
    assert chunks[0].start_page == 2
    assert chunks[0].end_page == 3

    assert chunks[2].section_type == SectionType.METHODS
    assert chunks[2].start_page == 4
    assert chunks[2].end_page == 5

    assert [chunk.position for chunk in chunks] == [1, 2, 3]