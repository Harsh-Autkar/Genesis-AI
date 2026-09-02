from services.document_processing.chunks import DocumentChunk

from .interface import EmbeddingInput


class BasicEmbeddingPreparer:
    """Convert document chunks into canonical embedding inputs."""

    def prepare(
        self,
        chunks: tuple[DocumentChunk, ...],
    ) -> tuple[EmbeddingInput, ...]:
        return tuple(
            EmbeddingInput(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                section_type=chunk.section_type,
                start_page=chunk.start_page,
                end_page=chunk.end_page,
                position=chunk.position,
            )
            for chunk in chunks
        )