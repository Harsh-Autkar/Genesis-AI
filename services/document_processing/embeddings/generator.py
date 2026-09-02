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
        
        
from sentence_transformers import SentenceTransformer

from .interface import EmbeddingInput, EmbeddingRecord


class SentenceTransformerEmbeddingGenerator:
    """Generate embeddings using a local Sentence Transformers model."""

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    MODEL_VERSION = "v1"

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device="cpu")

    def generate(
        self,
        inputs: tuple[EmbeddingInput, ...],
    ) -> tuple[EmbeddingRecord, ...]:
        if not inputs:
            return ()

        embeddings = self.model.encode(
            [item.text for item in inputs],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return tuple(
            EmbeddingRecord(
                source_type="paper_chunk",
                source_id=item.chunk_id,
                model_name=self.model_name,
                model_version=self.MODEL_VERSION,
                vector=tuple(float(value) for value in embedding),
            )
            for item, embedding in zip(inputs, embeddings, strict=True)
        )