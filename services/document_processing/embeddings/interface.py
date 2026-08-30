from dataclasses import dataclass
from typing import Protocol

from services.document_processing.structure import SectionType


@dataclass(frozen=True)
class EmbeddingInput:
    chunk_id: str
    text: str
    section_type: SectionType
    start_page: int
    end_page: int
    position: int


class EmbeddingPreparer(Protocol):
    def prepare(
        self,
        chunks,
    ) -> tuple[EmbeddingInput, ...]:
        """Prepare document chunks for embedding generation."""