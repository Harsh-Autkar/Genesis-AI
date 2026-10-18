from io import BytesIO
from uuid import uuid4

import pytest

from services.persistence.projects import ProjectRepository

from apps.api.app.services.paper_upload import PaperUploadService


class FakeUpload:
    def __init__(
        self,
        *,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> None:
        self.filename = filename
        self.content_type = content_type
        self.file = BytesIO(content)


class FakeStorage:
    def __init__(self) -> None:
        self.stored_keys: list[str] = []
        self.deleted_keys: list[str] = []

    def store(self, file, *, storage_key: str, content_type: str):
        from services.document_processing.storage.interface import StoredFile

        content = file.read()

        self.stored_keys.append(storage_key)

        return StoredFile(
            storage_key=storage_key,
            size_bytes=len(content),
            sha256="failure-test-hash",
            content_type=content_type,
        )

    def delete(self, *, storage_key: str) -> None:
        self.deleted_keys.append(storage_key)

    def exists(self, *, storage_key: str) -> bool:
        return storage_key in self.stored_keys


class FailingPaperRepository:
    def create(self, **kwargs):
        raise RuntimeError("forced database failure")


def test_database_failure_deletes_stored_file():
    project_id = uuid4()
    ProjectRepository().create(project_id=project_id)

    storage = FakeStorage()

    service = PaperUploadService(
        paper_repository=FailingPaperRepository(),
        storage=storage,
    )

    upload = FakeUpload(
        filename="failure-test.pdf",
        content_type="application/pdf",
        content=b"%PDF-1.4\nGenesis-AI failure test",
    )

    with pytest.raises(RuntimeError, match="forced database failure"):
        service.upload(
            project_id=project_id,
            file=upload,
        )

    assert len(storage.stored_keys) == 1
    assert storage.deleted_keys == storage.stored_keys