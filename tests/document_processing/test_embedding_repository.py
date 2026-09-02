import os

import pytest

from services.document_processing.embeddings import (
    PostgreSQLEmbeddingRepository,
    StoredEmbedding,
)


@pytest.fixture
def repository():
    dsn = os.environ.get(
    "GENESIS_DATABASE_DSN",
    "dbname=genesis_ai user=genesis password=genesis_local_dev_password "
    "host=localhost port=5433",
)

    return PostgreSQLEmbeddingRepository(dsn)


def test_save_and_find_similar(repository):
    embedding = StoredEmbedding(
        source_type="paper_chunk",
        source_id="test-chunk-1",
        model_name="test-model",
        model_version="v1",
        vector=tuple([1.0] + [0.0] * 383),
    )

    repository.save((embedding,))

    results = repository.find_similar(
        vector=embedding.vector,
        limit=1,
    )

    assert len(results) == 1
    assert results[0].source_type == "paper_chunk"
    assert results[0].source_id == "test-chunk-1"
    assert results[0].model_name == "test-model"
    assert results[0].model_version == "v1"
    assert len(results[0].vector) == 384


def test_empty_save_is_noop(repository):
    repository.save(())


def test_invalid_limit_is_rejected(repository):
    with pytest.raises(ValueError, match="limit"):
        repository.find_similar(
            vector=tuple([1.0] + [0.0] * 383),
            limit=0,
        )