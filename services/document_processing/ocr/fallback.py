from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf

from services.document_processing.parsing import (
    PageText,
    ParsedDocument,
    PyMuPDFParser,
)

from .render import PDFPageRenderer
from .tesseract import TesseractOCRService


class OCRFallbackParser:
    """Use PyMuPDF first and OCR only when no text is extractable."""

    EXTRACTION_METHOD = "ocr"

    def __init__(
        self,
        primary_parser: PyMuPDFParser | None = None,
        renderer: PDFPageRenderer | None = None,
        ocr_service: TesseractOCRService | None = None,
    ) -> None:
        self.primary_parser = primary_parser or PyMuPDFParser()
        self.renderer = renderer or PDFPageRenderer()
        self.ocr_service = ocr_service or TesseractOCRService()

    def parse(self, file_path: str) -> ParsedDocument:
        primary = self.primary_parser.parse(file_path)

        if any(page.text.strip() for page in primary.pages):
            return primary

        return self._parse_with_ocr(file_path)

    def _parse_with_ocr(self, file_path: str) -> ParsedDocument:
        pdf_path = Path(file_path)

        with TemporaryDirectory(prefix="genesis-ai-ocr-") as temp_dir:
            temp_path = Path(temp_dir)
            ocr_pages = []

            for page_number in range(1, self._page_count(pdf_path) + 1):
                image_path = temp_path / f"page-{page_number}.png"

                self.renderer.render_page(
                    str(pdf_path),
                    page_number=page_number,
                    output_path=str(image_path),
                )

                ocr_pages.append(
                    self.ocr_service.extract_page(
                        str(image_path),
                        page_number=page_number,
                    )
                )

        return ParsedDocument(
            page_count=len(ocr_pages),
            pages=tuple(
                PageText(
                    page_number=page.page_number,
                    text=page.text,
                )
                for page in ocr_pages
            ),
            metadata={},
            extraction_method=self.EXTRACTION_METHOD,
            extraction_confidence=(
                sum(page.confidence for page in ocr_pages)
                / len(ocr_pages)
                if ocr_pages
                else 0.0
            ),
        )

    @staticmethod
    def _page_count(pdf_path: Path) -> int:
        with pymupdf.open(pdf_path) as document:
            return len(document)