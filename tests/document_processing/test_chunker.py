from services.document_processing.chunks import ParagraphChunker
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
                original_heading="Introduction",
                text=text,
                start_page=2,
                end_page=3,
                confidence=1.0,
            ),
        ),
        structure_confidence=1.0,
    )


def test_chunks_paragraphs():
    document = make_document(
        "First paragraph.\n\nSecond paragraph."
    )

    chunks = ParagraphChunker().chunk(document)

    assert len(chunks) == 2
    assert chunks[0].text == "First paragraph."
    assert chunks[1].text == "Second paragraph."


def test_chunk_preserves_provenance():
    document = make_document("Research content.")

    chunks = ParagraphChunker().chunk(document)

    assert chunks[0].section_type == SectionType.INTRODUCTION
    assert chunks[0].start_page == 2
    assert chunks[0].end_page == 3
    assert chunks[0].position == 1


def test_large_paragraph_is_split():
    document = make_document("A" * 2500)

    chunks = ParagraphChunker(max_characters=1000).chunk(document)

    assert len(chunks) == 3
    assert all(len(chunk.text) <= 1000 for chunk in chunks)


def test_chunk_positions_are_sequential():
    document = StructuredDocument(
        sections=(
            DocumentSection(
                section_type=SectionType.INTRODUCTION,
                original_heading="Introduction",
                text="First paragraph.\n\nSecond paragraph.",
                start_page=1,
                end_page=1,
                confidence=1.0,
            ),
            DocumentSection(
                section_type=SectionType.METHODS,
                original_heading="Methods",
                text="Method paragraph.",
                start_page=2,
                end_page=2,
                confidence=1.0,
            ),
        ),
        structure_confidence=1.0,
    )

    chunks = ParagraphChunker().chunk(document)

    assert [chunk.position for chunk in chunks] == [1, 2, 3]


def test_empty_section_produces_no_chunks():
    document = make_document("")

    chunks = ParagraphChunker().chunk(document)

    assert chunks == ()