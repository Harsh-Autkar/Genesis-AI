from dataclasses import dataclass
from typing import Protocol

from services.document_processing.structure import SectionType


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    section_type: SectionType
    start_page: int
    end_page: int
    position: int


class Chunker(Protocol):
    def chunk(
        self,
        document,
    ) -> tuple[DocumentChunk, ...]:
        """Split a structured document into provenance-preserving chunks."""