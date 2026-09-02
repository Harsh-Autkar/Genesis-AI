import re
from uuid import uuid4

from services.document_processing.structure import StructuredDocument

from .interface import DocumentChunk


class ParagraphChunker:
    """Split structured sections into deterministic, provenance-preserving chunks."""

    def __init__(self, max_characters: int = 2000) -> None:
        if max_characters <= 0:
            raise ValueError("max_characters must be greater than 0.")

        self.max_characters = max_characters

    def chunk(
        self,
        document: StructuredDocument,
    ) -> tuple[DocumentChunk, ...]:
        chunks: list[DocumentChunk] = []
        position = 0

        for section in document.sections:
            paragraphs = self._split_paragraphs(section.text)

            for paragraph in paragraphs:
                for text in self._split_large_paragraph(paragraph):
                    position += 1

                    chunks.append(
                        DocumentChunk(
                            chunk_id=str(uuid4()),
                            text=text,
                            section_type=section.section_type,
                            start_page=section.start_page,
                            end_page=section.end_page,
                            position=position,
                        )
                    )

        return tuple(chunks)

    @staticmethod
    def _split_paragraphs(text: str) -> list[str]:
        return [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]

    def _split_large_paragraph(self, paragraph: str) -> list[str]:
        if len(paragraph) <= self.max_characters:
            return [paragraph]

        return [
            paragraph[start:start + self.max_characters].strip()
            for start in range(0, len(paragraph), self.max_characters)
            if paragraph[start:start + self.max_characters].strip()
        ]