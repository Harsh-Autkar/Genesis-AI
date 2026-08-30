from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Reference:
    reference_id: str
    raw_text: str
    title: str | None
    authors: tuple[str, ...]
    year: int | None
    doi: str | None


@dataclass(frozen=True)
class CitationOccurrence:
    citation_id: str
    reference_id: str
    page_number: int
    context: str


@dataclass(frozen=True)
class ScholarlyDocument:
    references: tuple[Reference, ...]
    citations: tuple[CitationOccurrence, ...]


class ScholarlyExtractor(Protocol):
    def extract(self, document) -> ScholarlyDocument:
        """Extract references and citation occurrences from a document."""