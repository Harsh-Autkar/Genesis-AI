from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

from services.document_processing.ocr import (
    PDFPageRenderer,
    TesseractOCRService,
)


def create_ocr_test_image(path: Path) -> None:
    image = Image.new("RGB", (1800, 600), "white")
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "C:/Windows/Fonts/arial.ttf",
        64,
    )

    draw.text(
        (100, 140),
        "GENESIS AI OCR TEST",
        fill="black",
        font=font,
    )

    draw.text(
        (100, 280),
        "RESEARCH PAPER PROCESSING",
        fill="black",
        font=font,
    )

    image.save(path)


def test_tesseract_extracts_text_from_image(tmp_path):
    image_path = tmp_path / "ocr-test.png"
    create_ocr_test_image(image_path)

    service = TesseractOCRService()

    result = service.extract_page(
        str(image_path),
        page_number=1,
    )

    assert result.page_number == 1
    assert "GENESIS" in result.text.upper()
    assert "OCR" in result.text.upper()
    assert result.confidence > 0.0


def test_pdf_page_renderer_creates_image(tmp_path):
    pdf_path = tmp_path / "source.pdf"
    image_path = tmp_path / "rendered.png"

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "GENESIS AI RENDERED PAGE")
    document.save(pdf_path)
    document.close()

    renderer = PDFPageRenderer()

    result = renderer.render_page(
        str(pdf_path),
        page_number=1,
        output_path=str(image_path),
    )

    assert result == str(image_path)
    assert image_path.exists()
    assert image_path.stat().st_size > 0


def test_renderer_rejects_invalid_page_number(tmp_path):
    pdf_path = tmp_path / "source.pdf"
    image_path = tmp_path / "rendered.png"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    renderer = PDFPageRenderer()

    try:
        renderer.render_page(
            str(pdf_path),
            page_number=2,
            output_path=str(image_path),
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "exceeds PDF page count" in str(exc)