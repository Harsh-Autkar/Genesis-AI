from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str


@dataclass(frozen=True)
class ParsedDocument:
    page_count: int
    pages: tuple[PageText, ...]
    metadata: dict[str, str]
    extraction_method: str
    extraction_confidence: float


class DocumentParser(Protocol):
    def parse(self, file_path: str) -> ParsedDocument:
        """Parse a PDF into a canonical document representation."""