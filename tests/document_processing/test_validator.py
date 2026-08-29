from services.document_processing.intake.validator import (
    MAX_UPLOAD_SIZE_BYTES,
    validate_document,
)


def test_valid_pdf_is_accepted():
    result = validate_document(
        filename="research-paper.pdf",
        size_bytes=1024,
        content_type="application/pdf",
    )

    assert result.valid is True
    assert result.error_code is None


def test_missing_filename_is_rejected():
    result = validate_document(
        filename=None,
        size_bytes=1024,
        content_type="application/pdf",
    )

    assert result.valid is False
    assert result.error_code == "MISSING_FILENAME"


def test_empty_file_is_rejected():
    result = validate_document(
        filename="research-paper.pdf",
        size_bytes=0,
        content_type="application/pdf",
    )

    assert result.valid is False
    assert result.error_code == "EMPTY_FILE"


def test_file_over_15_mb_is_rejected():
    result = validate_document(
        filename="research-paper.pdf",
        size_bytes=MAX_UPLOAD_SIZE_BYTES + 1,
        content_type="application/pdf",
    )

    assert result.valid is False
    assert result.error_code == "FILE_TOO_LARGE"


def test_non_pdf_extension_is_rejected():
    result = validate_document(
        filename="research-paper.docx",
        size_bytes=1024,
        content_type="application/pdf",
    )

    assert result.valid is False
    assert result.error_code == "UNSUPPORTED_FILE"


def test_invalid_content_type_is_rejected():
    result = validate_document(
        filename="research-paper.pdf",
        size_bytes=1024,
        content_type="text/plain",
    )

    assert result.valid is False
    assert result.error_code == "INVALID_CONTENT_TYPE"