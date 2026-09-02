import os
from pathlib import Path

from PIL import Image
import pytesseract

from .interface import OCRPage


class TesseractOCRService:
    """Extract text from rendered document pages using Tesseract."""

    DEFAULT_WINDOWS_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def __init__(self, tesseract_cmd: str | None = None) -> None:
        configured_cmd = tesseract_cmd or os.getenv("TESSERACT_CMD")

        if configured_cmd:
            pytesseract.pytesseract.tesseract_cmd = configured_cmd
        elif (
            os.name == "nt"
            and Path(self.DEFAULT_WINDOWS_PATH).is_file()
        ):
            pytesseract.pytesseract.tesseract_cmd = (
                self.DEFAULT_WINDOWS_PATH
            )

    def extract_page(
        self,
        image_path: str,
        *,
        page_number: int,
    ) -> OCRPage:
        path = Path(image_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Image file not found: {image_path}"
            )

        with Image.open(path) as image:
            text = pytesseract.image_to_string(image)

            data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT,
            )

        confidences = [
            float(conf)
            for conf in data["conf"]
            if conf not in ("-1", "")
        ]

        confidence = (
            sum(confidences) / len(confidences) / 100
            if confidences
            else 0.0
        )

        return OCRPage(
            page_number=page_number,
            text=text,
            confidence=confidence,
        )