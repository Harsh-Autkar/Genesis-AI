from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from services.document_processing.parsing import ParsedDocument


class SectionType(StrEnum):
    TITLE = "title"
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    RELATED_WORK = "related_work"
    METHODS = "methods"
    EXPERIMENTS = "experiments"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    OTHER = "other"


@dataclass(frozen=True)
class DocumentSection:
    section_type: SectionType
    original_heading: str
    text: str
    start_page: int
    end_page: int
    confidence: float


@dataclass(frozen=True)
class StructuredDocument:
    sections: tuple[DocumentSection, ...]
    structure_confidence: float


class StructureDetector(Protocol):
    def detect(self, document: ParsedDocument) -> StructuredDocument:
        """Detect and normalize the structure of a parsed research document."""