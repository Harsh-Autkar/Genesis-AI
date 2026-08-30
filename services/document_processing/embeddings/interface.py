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


@dataclass(frozen=True)
class EmbeddingRecord:
    source_type: str
    source_id: str
    model_name: str
    model_version: str
    vector: tuple[float, ...]


class EmbeddingPreparer(Protocol):
    def prepare(
        self,
        chunks,
    ) -> tuple[EmbeddingInput, ...]:
        """Prepare document chunks for embedding generation."""


class EmbeddingGenerator(Protocol):
    def generate(
        self,
        inputs: tuple[EmbeddingInput, ...],
    ) -> tuple[EmbeddingRecord, ...]:
        """Generate embeddings for prepared document inputs."""