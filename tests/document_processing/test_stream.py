from io import BytesIO

import pytest

from services.document_processing.intake.stream import (
    FileTooLargeError,
    measure_stream_size,
)
from services.document_processing.intake.validator import MAX_UPLOAD_SIZE_BYTES


def test_measure_stream_size_returns_size_and_rewinds():
    content = b"Genesis-AI"
    file = BytesIO(content)

    size = measure_stream_size(file)

    assert size == len(content)
    assert file.tell() == 0


def test_measure_stream_size_rejects_files_over_15_mb():
    content = b"x" * (MAX_UPLOAD_SIZE_BYTES + 1)
    file = BytesIO(content)

    with pytest.raises(FileTooLargeError):
        measure_stream_size(file)