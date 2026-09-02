from dataclasses import dataclass
from pathlib import Path


MAX_UPLOAD_SIZE_BYTES = 15 * 1024 * 1024
ALLOWED_MIME_TYPE = "application/pdf"
ALLOWED_EXTENSION = ".pdf"


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    filename: str
    size_bytes: int
    content_type: str | None = None
    error_code: str | None = None
    error_message: str | None = None


def validate_document(
    filename: str | None,
    size_bytes: int,
    content_type: str | None,
) -> ValidationResult:
    if not filename:
        return ValidationResult(
            valid=False,
            filename="",
            size_bytes=size_bytes,
            error_code="MISSING_FILENAME",
            error_message="A filename is required.",
        )

    if size_bytes <= 0:
        return ValidationResult(
            valid=False,
            filename=filename,
            size_bytes=size_bytes,
            error_code="EMPTY_FILE",
            error_message="The uploaded file is empty.",
        )

    if size_bytes > MAX_UPLOAD_SIZE_BYTES:
        return ValidationResult(
            valid=False,
            filename=filename,
            size_bytes=size_bytes,
            error_code="FILE_TOO_LARGE",
            error_message="The uploaded file exceeds the 15 MB limit.",
        )

    if Path(filename).suffix.lower() != ALLOWED_EXTENSION:
        return ValidationResult(
            valid=False,
            filename=filename,
            size_bytes=size_bytes,
            error_code="UNSUPPORTED_FILE",
            error_message="Only PDF files are supported.",
        )

    if content_type != ALLOWED_MIME_TYPE:
        return ValidationResult(
            valid=False,
            filename=filename,
            size_bytes=size_bytes,
            error_code="INVALID_CONTENT_TYPE",
            error_message="The uploaded file must have application/pdf content type.",
        )

    return ValidationResult(
        valid=True,
        filename=filename,
        size_bytes=size_bytes,
        content_type=content_type,
    )