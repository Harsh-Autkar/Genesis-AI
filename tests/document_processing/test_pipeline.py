from pathlib import Path

from services.document_processing.chunks import DocumentChunk
from services.document_processing.embeddings import (
    EmbeddingInput,
    EmbeddingRecord,
)
from services.document_processing.parsing import PageText, ParsedDocument
from services.document_processing.pipeline import (
    DefaultDocumentProcessingPipeline,
)
from services.document_processing.scholarly import ScholarlyDocument
from services.document_processing.storage import StoredFile
from services.document_processing.structure import (
    DocumentSection,
    SectionType,
    StructuredDocument,
)


class FakeStorage:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.resolved_keys: list[str] = []

    def resolve_path(self, *, storage_key: str) -> Path:
        self.resolved_keys.append(storage_key)
        return self.file_path


class FakeParser:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def parse(self, file_path: str) -> ParsedDocument:
        self.calls.append("parse")

        return ParsedDocument(
            page_count=1,
            pages=(PageText(page_number=1, text="paper text"),),
            metadata={},
            extraction_method="test",
            extraction_confidence=1.0,
        )


class FakeStructureDetector:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def detect(self, document: ParsedDocument) -> StructuredDocument:
        self.calls.append("structure")

        return StructuredDocument(
            sections=(
                DocumentSection(
                    section_type=SectionType.INTRODUCTION,
                    original_heading="Introduction",
                    text="paper text",
                    start_page=1,
                    end_page=1,
                    confidence=1.0,
                ),
            ),
            structure_confidence=1.0,
        )


class FakeScholarlyExtractor:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def extract(
        self,
        document: StructuredDocument,
    ) -> ScholarlyDocument:
        self.calls.append("scholarly")

        return ScholarlyDocument(
            references=(),
            citations=(),
        )


class FakeChunker:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def chunk(
        self,
        document: StructuredDocument,
    ) -> tuple[DocumentChunk, ...]:
        self.calls.append("chunk")

        return (
            DocumentChunk(
                chunk_id="chunk-1",
                text="paper text",
                section_type=SectionType.INTRODUCTION,
                start_page=1,
                end_page=1,
                position=0,
            ),
        )


class FakeEmbeddingPreparer:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def prepare(
        self,
        chunks: tuple[DocumentChunk, ...],
    ) -> tuple[EmbeddingInput, ...]:
        self.calls.append("prepare")

        return (
            EmbeddingInput(
                chunk_id="chunk-1",
                text="paper text",
                section_type=SectionType.INTRODUCTION,
                start_page=1,
                end_page=1,
                position=0,
            ),
        )


class FakeEmbeddingGenerator:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def generate(
        self,
        inputs: tuple[EmbeddingInput, ...],
    ) -> tuple[EmbeddingRecord, ...]:
        self.calls.append("generate")

        return (
            EmbeddingRecord(
                source_type="paper_chunk",
                source_id="chunk-1",
                model_name="test-model",
                model_version="test-v1",
                vector=(0.1, 0.2, 0.3),
            ),
        )


def test_pipeline_orchestrates_components_in_order(tmp_path):
    calls: list[str] = []

    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"test-pdf")

    storage = FakeStorage(pdf_path)

    pipeline = DefaultDocumentProcessingPipeline(
        storage=storage,
        parser=FakeParser(calls),
        structure_detector=FakeStructureDetector(calls),
        scholarly_extractor=FakeScholarlyExtractor(calls),
        chunker=FakeChunker(calls),
        embedding_preparer=FakeEmbeddingPreparer(calls),
        embedding_generator=FakeEmbeddingGenerator(calls),
    )

    result = pipeline.run("papers/test-paper.pdf")

    assert storage.resolved_keys == ["papers/test-paper.pdf"]

    assert calls == [
        "parse",
        "structure",
        "scholarly",
        "chunk",
        "prepare",
        "generate",
    ]

    assert result.structured_document.structure_confidence == 1.0
    assert len(result.scholarly_document.references) == 0
    assert len(result.chunks) == 1
    assert len(result.embeddings) == 1


def test_pipeline_rejects_missing_stored_document(tmp_path):
    missing_path = tmp_path / "missing.pdf"

    pipeline = DefaultDocumentProcessingPipeline(
        storage=FakeStorage(missing_path),
        parser=FakeParser([]),
        structure_detector=FakeStructureDetector([]),
        scholarly_extractor=FakeScholarlyExtractor([]),
        chunker=FakeChunker([]),
        embedding_preparer=FakeEmbeddingPreparer([]),
        embedding_generator=FakeEmbeddingGenerator([]),
    )

    try:
        pipeline.run("papers/missing.pdf")
    except FileNotFoundError as exc:
        assert "papers/missing.pdf" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")