from pathlib import Path

import pymupdf

from services.document_processing.ocr import OCRFallbackParser


def create_text_pdf(path: Path) -> None:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Genesis-AI digital PDF")
    document.save(path)
    document.close()


def create_scanned_pdf(path: Path) -> None:
    image_path = path.parent / "scanned-page.png"

    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (1800, 600), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 64)

    draw.text(
        (100, 150),
        "GENESIS AI SCANNED PAPER",
        fill="black",
        font=font,
    )

    draw.text(
        (100, 290),
        "OCR FALLBACK TEST",
        fill="black",
        font=font,
    )

    image.save(image_path)

    document = pymupdf.open()
    page = document.new_page(width=image.width, height=image.height)

    page.insert_image(
        page.rect,
        filename=str(image_path),
    )

    document.save(path)
    document.close()


def test_text_pdf_does_not_trigger_ocr(tmp_path):
    pdf_path = tmp_path / "digital.pdf"
    create_text_pdf(pdf_path)

    result = OCRFallbackParser().parse(str(pdf_path))

    assert result.extraction_method == "pymupdf"
    assert "Genesis-AI digital PDF" in result.pages[0].text


def test_scanned_pdf_triggers_ocr(tmp_path):
    pdf_path = tmp_path / "scanned.pdf"
    create_scanned_pdf(pdf_path)

    result = OCRFallbackParser().parse(str(pdf_path))

    assert result.extraction_method == "ocr"
    assert result.page_count == 1
    assert "GENESIS" in result.pages[0].text.upper()
    assert "OCR" in result.pages[0].text.upper()
    assert result.extraction_confidence > 0.0