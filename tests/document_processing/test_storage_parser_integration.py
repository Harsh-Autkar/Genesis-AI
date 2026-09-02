from pathlib import Path

import pymupdf

from services.document_processing.parsing import PyMuPDFParser
from services.document_processing.storage import LocalFileStorage


def create_test_pdf(path: Path) -> None:
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text((72, 72), "Genesis-AI Integration Test")
    page.insert_text((72, 100), "Stored PDF parsing works.")

    document.save(path)
    document.close()


def test_stored_pdf_can_be_resolved_and_parsed(tmp_path):
    storage = LocalFileStorage(tmp_path / "uploads")

    source_pdf = tmp_path / "source.pdf"
    create_test_pdf(source_pdf)

    with source_pdf.open("rb") as file:
        stored = storage.store(
            file,
            storage_key="projects/project-123/papers/paper-456/versions/v1/original.pdf",
            content_type="application/pdf",
        )

    stored_path = storage.resolve_path(storage_key=stored.storage_key)

    parsed = PyMuPDFParser().parse(str(stored_path))

    assert parsed.page_count == 1
    assert "Genesis-AI Integration Test" in parsed.pages[0].text
    assert "Stored PDF parsing works." in parsed.pages[0].text