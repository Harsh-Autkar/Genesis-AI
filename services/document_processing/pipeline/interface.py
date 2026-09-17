from dataclasses import dataclass

from services.document_processing.chunks import DocumentChunk
from services.document_processing.embeddings import EmbeddingRecord
from services.document_processing.scholarly import ScholarlyDocument
from services.document_processing.structure import StructuredDocument


@dataclass(frozen=True)
class PipelineResult:
    """Outputs produced by document-processing orchestration."""

    structured_document: StructuredDocument
    scholarly_document: ScholarlyDocument
    chunks: tuple[DocumentChunk, ...]
    embeddings: tuple[EmbeddingRecord, ...]


class DocumentProcessingPipeline:
    """Orchestrate document processing components."""

    def run(self, storage_key: str) -> PipelineResult:
        """Process a stored research paper through the pipeline."""
        raise NotImplementedError