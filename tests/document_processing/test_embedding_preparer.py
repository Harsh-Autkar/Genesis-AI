from services.document_processing.chunks import DocumentChunk
from services.document_processing.embeddings import BasicEmbeddingPreparer
from services.document_processing.structure import SectionType


def test_preparer_preserves_chunk_content_and_provenance():
    chunks = (
        DocumentChunk(
            chunk_id="chunk-1",
            text="Research content.",
            section_type=SectionType.INTRODUCTION,
            start_page=2,
            end_page=3,
            position=1,
        ),
        DocumentChunk(
            chunk_id="chunk-2",
            text="Method content.",
            section_type=SectionType.METHODS,
            start_page=4,
            end_page=4,
            position=2,
        ),
    )

    inputs = BasicEmbeddingPreparer().prepare(chunks)

    assert len(inputs) == 2

    assert inputs[0].chunk_id == "chunk-1"
    assert inputs[0].text == "Research content."
    assert inputs[0].section_type == SectionType.INTRODUCTION
    assert inputs[0].start_page == 2
    assert inputs[0].end_page == 3
    assert inputs[0].position == 1

    assert inputs[1].chunk_id == "chunk-2"
    assert inputs[1].section_type == SectionType.METHODS


def test_preparer_preserves_order():
    chunks = (
        DocumentChunk(
            chunk_id="chunk-1",
            text="First.",
            section_type=SectionType.INTRODUCTION,
            start_page=1,
            end_page=1,
            position=1,
        ),
        DocumentChunk(
            chunk_id="chunk-2",
            text="Second.",
            section_type=SectionType.RESULTS,
            start_page=2,
            end_page=2,
            position=2,
        ),
    )

    inputs = BasicEmbeddingPreparer().prepare(chunks)

    assert [item.chunk_id for item in inputs] == [
        "chunk-1",
        "chunk-2",
    ]


def test_empty_chunks_produce_empty_inputs():
    inputs = BasicEmbeddingPreparer().prepare(())

    assert inputs == ()