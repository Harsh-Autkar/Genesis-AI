from dataclasses import dataclass
from typing import BinaryIO, Protocol


@dataclass(frozen=True)
class StoredFile:
    storage_key: str
    size_bytes: int
    sha256: str
    content_type: str


class FileStorage(Protocol):
    def store(
        self,
        file: BinaryIO,
        *,
        storage_key: str,
        content_type: str,
    ) -> StoredFile:
        """Persist a file and return its storage metadata."""

    def delete(self, *, storage_key: str) -> None:
        """Delete a previously stored file."""

    def exists(self, *, storage_key: str) -> bool:
        """Return whether a stored file exists."""