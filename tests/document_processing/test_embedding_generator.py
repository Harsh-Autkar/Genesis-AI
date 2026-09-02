import pytest

from services.document_processing.embeddings import (
    EmbeddingInput,
    SentenceTransformerEmbeddingGenerator,
)
from services.document_processing.structure import SectionType


def make_inputs() -> tuple[EmbeddingInput, ...]:
    return (
        EmbeddingInput(
            chunk_id="chunk-1",
            text="Machine learning improves research retrieval.",
            section_type=SectionType.INTRODUCTION,
            start_page=1,
            end_page=1,
            position=1,
        ),
        EmbeddingInput(
            chunk_id="chunk-2",
            text="Semantic search identifies related research papers.",
            section_type=SectionType.RELATED_WORK,
            start_page=2,
            end_page=2,
            position=2,
        ),
    )


@pytest.fixture(scope="module")
def generator():
    return SentenceTransformerEmbeddingGenerator()


def test_generates_384_dimensional_embeddings(generator):
    records = generator.generate(make_inputs())

    assert len(records) == 2
    assert len(records[0].vector) == 384
    assert len(records[1].vector) == 384


def test_preserves_embedding_source_metadata(generator):
    records = generator.generate(make_inputs())

    assert records[0].source_type == "paper_chunk"
    assert records[0].source_id == "chunk-1"
    assert records[0].model_name == (
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    assert records[0].model_version == "v1"


def test_embedding_vectors_are_normalized(generator):
    records = generator.generate(make_inputs())

    norm = sum(value * value for value in records[0].vector) ** 0.5

    assert abs(norm - 1.0) < 1e-5


def test_empty_input_returns_empty_result(generator):
    assert generator.generate(()) == ()