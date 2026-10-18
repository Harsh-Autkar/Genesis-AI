import os
from uuid import uuid4

import psycopg
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


def make_vector(first_value: float = 1.0) -> tuple[float, ...]:
    return tuple([first_value] + [0.0] * 383)


def test_save_and_find_similar(repository):
    model_name = f"test-model-{uuid4()}"

    embedding = StoredEmbedding(
        source_type="paper_chunk",
        source_id=f"test-chunk-{uuid4()}",
        model_name=model_name,
        model_version="v1",
        vector=make_vector(),
    )

    repository.save((embedding,))

    results = repository.find_similar(
        vector=embedding.vector,
        model_name=embedding.model_name,
        model_version=embedding.model_version,
        limit=1,
    )

    assert len(results) == 1
    assert results[0].source_type == "paper_chunk"
    assert results[0].source_id == embedding.source_id
    assert results[0].model_name == embedding.model_name
    assert results[0].model_version == embedding.model_version
    assert len(results[0].vector) == 384


def test_empty_save_is_noop(repository):
    repository.save(())


def test_invalid_limit_is_rejected(repository):
    with pytest.raises(ValueError, match="limit"):
        repository.find_similar(
            vector=make_vector(),
            model_name=f"test-model-{uuid4()}",
            model_version="v1",
            limit=0,
        )


def test_find_similar_filters_by_model_and_version(repository):
    filter_model = f"filter-model-{uuid4()}"

    matching = StoredEmbedding(
        source_type="paper_chunk",
        source_id=f"filter-test-{uuid4()}",
        model_name=filter_model,
        model_version="v1",
        vector=make_vector(),
    )

    other_model = StoredEmbedding(
        source_type="paper_chunk",
        source_id=f"other-model-{uuid4()}",
        model_name=f"other-model-{uuid4()}",
        model_version="v1",
        vector=make_vector(),
    )

    other_version = StoredEmbedding(
        source_type="paper_chunk",
        source_id=f"other-version-{uuid4()}",
        model_name=filter_model,
        model_version="v2",
        vector=make_vector(),
    )

    repository.save((matching, other_model, other_version))

    results = repository.find_similar(
        vector=matching.vector,
        model_name=filter_model,
        model_version="v1",
        limit=10,
    )

    assert results
    assert all(
        result.model_name == filter_model
        and result.model_version == "v1"
        for result in results
    )
    assert results[0].source_id == matching.source_id


def test_duplicate_save_is_idempotent(repository):
    embedding = StoredEmbedding(
        source_type="paper_chunk",
        source_id=f"idempotent-{uuid4()}",
        model_name=f"idempotent-model-{uuid4()}",
        model_version="v1",
        vector=make_vector(),
    )

    repository.save((embedding,))
    repository.save((embedding,))

    dsn = os.environ.get(
        "GENESIS_DATABASE_DSN",
        "dbname=genesis_ai user=genesis password=genesis_local_dev_password "
        "host=localhost port=5433",
    )

    with psycopg.connect(dsn) as connection:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM embeddings
            WHERE source_type = %s
              AND source_id = %s
              AND model_name = %s
              AND model_version = %s
            """,
            (
                embedding.source_type,
                embedding.source_id,
                embedding.model_name,
                embedding.model_version,
            ),
        ).fetchone()[0]

    assert count == 1
