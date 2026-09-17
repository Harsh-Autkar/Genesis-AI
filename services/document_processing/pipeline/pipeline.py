from pathlib import Path

from services.document_processing.chunks import (
    DocumentChunk,
    ParagraphChunker,
)
from services.document_processing.embeddings import (
    BasicEmbeddingPreparer,
    EmbeddingGenerator,
    EmbeddingPreparer,
    SentenceTransformerEmbeddingGenerator,
)
from services.document_processing.ocr import OCRFallbackParser
from services.document_processing.scholarly import (
    BaselineScholarlyExtractor,
    ScholarlyDocument,
)
from services.document_processing.storage import LocalFileStorage
from services.document_processing.structure import (
    HeuristicStructureDetector,
    StructuredDocument,
)

from .interface import PipelineResult


class DefaultDocumentProcessingPipeline:
    """Default MVP orchestration for research-paper processing."""

    def __init__(
        self,
        *,
        storage: LocalFileStorage,
        parser: OCRFallbackParser | None = None,
        structure_detector: HeuristicStructureDetector | None = None,
        scholarly_extractor: BaselineScholarlyExtractor | None = None,
        chunker: ParagraphChunker | None = None,
        embedding_preparer: EmbeddingPreparer | None = None,
        embedding_generator: EmbeddingGenerator | None = None,
    ) -> None:
        self.storage = storage
        self.parser = parser or OCRFallbackParser()
        self.structure_detector = (
            structure_detector or HeuristicStructureDetector()
        )
        self.scholarly_extractor = (
            scholarly_extractor or BaselineScholarlyExtractor()
        )
        self.chunker = chunker or ParagraphChunker()
        self.embedding_preparer = (
            embedding_preparer or BasicEmbeddingPreparer()
        )
        self.embedding_generator = (
            embedding_generator
            or SentenceTransformerEmbeddingGenerator()
        )

    def run(self, storage_key: str) -> PipelineResult:
        """Run the complete document-processing workflow."""

        file_path = self.storage.resolve_path(
        storage_key=storage_key,
            )
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Stored document does not exist: {storage_key}"
            )

        parsed_document = self.parser.parse(str(file_path))

        structured_document = self.structure_detector.detect(
            parsed_document
        )

        scholarly_document = self.scholarly_extractor.extract(
            structured_document
        )

        chunks = self.chunker.chunk(structured_document)

        embedding_inputs = self.embedding_preparer.prepare(chunks)

        embeddings = self.embedding_generator.generate(
            embedding_inputs
        )

        return PipelineResult(
            structured_document=structured_document,
            scholarly_document=scholarly_document,
            chunks=chunks,
            embeddings=embeddings,
        )