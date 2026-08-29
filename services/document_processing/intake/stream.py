from typing import BinaryIO

from .validator import MAX_UPLOAD_SIZE_BYTES


class FileTooLargeError(ValueError):
    """Raised when a stream exceeds the configured upload limit."""


def measure_stream_size(file: BinaryIO) -> int:
    size_bytes = 0

    while chunk := file.read(1024 * 1024):
        size_bytes += len(chunk)

        if size_bytes > MAX_UPLOAD_SIZE_BYTES:
            raise FileTooLargeError

    file.seek(0)
    return size_bytes