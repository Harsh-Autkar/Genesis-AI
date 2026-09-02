from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class OCRPage:
    page_number: int
    text: str
    confidence: float


@dataclass(frozen=True)
class OCRDocument:
    pages: tuple[OCRPage, ...]
    overall_confidence: float


class OCRService(Protocol):
    def extract_page(
        self,
        image_path: str,
        *,
        page_number: int,
    ) -> OCRPage:
        """Extract text from one rendered document page."""