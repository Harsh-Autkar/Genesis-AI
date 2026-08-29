from io import BytesIO

import pytest

from services.document_processing.storage import LocalFileStorage


def test_store_creates_file_and_returns_metadata(tmp_path):
    storage = LocalFileStorage(tmp_path)
    content = b"Genesis-AI test document"

    result = storage.store(
        BytesIO(content),
        storage_key="papers/project-123/paper-456.pdf",
        content_type="application/pdf",
    )

    stored_path = tmp_path / "papers" / "project-123" / "paper-456.pdf"

    assert result.storage_key == "papers/project-123/paper-456.pdf"
    assert result.size_bytes == len(content)
    assert result.content_type == "application/pdf"
    assert result.sha256

    assert stored_path.exists()
    assert stored_path.read_bytes() == content


def test_exists_returns_true_for_stored_file(tmp_path):
    storage = LocalFileStorage(tmp_path)

    storage.store(
        BytesIO(b"test"),
        storage_key="papers/test.pdf",
        content_type="application/pdf",
    )

    assert storage.exists(storage_key="papers/test.pdf") is True


def test_exists_returns_false_for_missing_file(tmp_path):
    storage = LocalFileStorage(tmp_path)

    assert storage.exists(storage_key="papers/missing.pdf") is False


def test_delete_removes_stored_file(tmp_path):
    storage = LocalFileStorage(tmp_path)

    storage.store(
        BytesIO(b"test"),
        storage_key="papers/delete-me.pdf",
        content_type="application/pdf",
    )

    storage.delete(storage_key="papers/delete-me.pdf")

    assert storage.exists(storage_key="papers/delete-me.pdf") is False


def test_path_traversal_is_rejected(tmp_path):
    storage = LocalFileStorage(tmp_path)

    with pytest.raises(ValueError, match="escapes the storage root"):
        storage.store(
            BytesIO(b"malicious"),
            storage_key="../../outside.txt",
            content_type="text/plain",
        )


def test_storage_handles_nested_keys(tmp_path):
    storage = LocalFileStorage(tmp_path)

    result = storage.store(
        BytesIO(b"nested content"),
        storage_key="users/u1/projects/p1/versions/v1/original.pdf",
        content_type="application/pdf",
    )

    assert result.size_bytes == len(b"nested content")
    assert storage.exists(
        storage_key="users/u1/projects/p1/versions/v1/original.pdf"
    )