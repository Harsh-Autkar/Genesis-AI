from hashlib import sha256
from pathlib import Path
from typing import BinaryIO

from .interface import StoredFile


class LocalFileStorage:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def store(
        self,
        file: BinaryIO,
        *,
        storage_key: str,
        content_type: str,
    ) -> StoredFile:
        destination = self._resolve_key(storage_key)
        destination.parent.mkdir(parents=True, exist_ok=True)

        digest = sha256()
        size_bytes = 0

        with destination.open("wb") as output:
            while chunk := file.read(1024 * 1024):
                output.write(chunk)
                digest.update(chunk)
                size_bytes += len(chunk)

        return StoredFile(
            storage_key=storage_key,
            size_bytes=size_bytes,
            sha256=digest.hexdigest(),
            content_type=content_type,
        )

    def delete(self, *, storage_key: str) -> None:
        destination = self._resolve_key(storage_key)

        if destination.exists():
            destination.unlink()

    def exists(self, *, storage_key: str) -> bool:
        return self._resolve_key(storage_key).is_file()

    def resolve_path(self, *, storage_key: str) -> Path:
        """Resolve a storage key to its private filesystem path."""
        return self._resolve_key(storage_key)

    def _resolve_key(self, storage_key: str) -> Path:
        candidate = (self.base_path / storage_key).resolve()
        base = self.base_path.resolve()

        if candidate != base and base not in candidate.parents:
            raise ValueError("Storage key escapes the storage root.")

        return candidate