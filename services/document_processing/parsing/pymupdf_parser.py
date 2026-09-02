from pathlib import Path

import pymupdf

from .interface import PageText, ParsedDocument


class DocumentParseError(ValueError):
    """Raised when a PDF cannot be parsed successfully."""


class PyMuPDFParser:
    """Parse digitally native PDFs into Genesis-AI's canonical format."""

    EXTRACTION_METHOD = "pymupdf"
    EXTRACTION_CONFIDENCE = 1.0

    def parse(self, file_path: str) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        pages: list[PageText] = []

        try:
            with pymupdf.open(path) as document:
                metadata = {
                    key: value
                    for key, value in document.metadata.items()
                    if value is not None
                }

                for page_index, page in enumerate(document):
                    pages.append(
                        PageText(
                            page_number=page_index + 1,
                            text=page.get_text(),
                        )
                    )

                return ParsedDocument(
                    page_count=len(document),
                    pages=tuple(pages),
                    metadata=metadata,
                    extraction_method=self.EXTRACTION_METHOD,
                    extraction_confidence=self.EXTRACTION_CONFIDENCE,
                )

        except pymupdf.FileDataError as exc:
            raise DocumentParseError(
                f"Unable to parse PDF file: {file_path}"
            ) from exc