from pathlib import Path

import pymupdf
import pytest

from services.document_processing.parsing import (
    DocumentParseError,
    PyMuPDFParser,
)


def create_test_pdf(path: Path) -> None:
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text((72, 72), "Genesis-AI Test Paper")
    page.insert_text((72, 100), "This is the first page.")

    page = document.new_page()
    page.insert_text((72, 72), "Second Page")
    page.insert_text((72, 100), "This page verifies multi-page extraction.")

    document.save(path)
    document.close()


def test_parser_extracts_pages_and_text(tmp_path):
    pdf_path = tmp_path / "research-paper.pdf"
    create_test_pdf(pdf_path)

    parser = PyMuPDFParser()
    result = parser.parse(str(pdf_path))

    assert result.page_count == 2
    assert len(result.pages) == 2

    assert result.pages[0].page_number == 1
    assert "Genesis-AI Test Paper" in result.pages[0].text
    assert "This is the first page." in result.pages[0].text

    assert result.pages[1].page_number == 2
    assert "Second Page" in result.pages[1].text


def test_parser_returns_canonical_metadata(tmp_path):
    pdf_path = tmp_path / "metadata-paper.pdf"

    document = pymupdf.open()
    document.set_metadata(
        {
            "title": "Genesis-AI Metadata Test",
            "author": "Genesis-AI",
        }
    )

    page = document.new_page()
    page.insert_text((72, 72), "Metadata test")
    document.save(pdf_path)
    document.close()

    result = PyMuPDFParser().parse(str(pdf_path))

    assert result.metadata["title"] == "Genesis-AI Metadata Test"
    assert result.metadata["author"] == "Genesis-AI"
    assert result.extraction_method == "pymupdf"
    assert result.extraction_confidence == 1.0


def test_parser_rejects_missing_file(tmp_path):
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        PyMuPDFParser().parse(str(missing_path))


def test_parser_rejects_corrupt_pdf(tmp_path):
    corrupt_pdf = tmp_path / "corrupt.pdf"
    corrupt_pdf.write_bytes(b"this is not a valid PDF")

    with pytest.raises(DocumentParseError):
        PyMuPDFParser().parse(str(corrupt_pdf))


def test_parser_preserves_unicode_text(tmp_path):
    pdf_path = tmp_path / "unicode.pdf"

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Genesis-AI - Resume Delta research",
    )
    document.save(pdf_path)
    document.close()

    result = PyMuPDFParser().parse(str(pdf_path))

    assert "Genesis-AI" in result.pages[0].text
    assert "Resume" in result.pages[0].text


def test_parser_handles_pdf_with_no_extractable_text(tmp_path):
    pdf_path = tmp_path / "empty-text.pdf"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    result = PyMuPDFParser().parse(str(pdf_path))

    assert result.page_count == 1
    assert result.pages[0].text.strip() == ""