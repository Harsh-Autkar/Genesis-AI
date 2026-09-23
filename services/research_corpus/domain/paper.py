from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class AccessStatus(StrEnum):
    UNKNOWN = "unknown"
    OPEN_ACCESS = "open_access"
    PARTIAL = "partial"
    RESTRICTED = "restricted"


class ProcessingStatus(StrEnum):
    DISCOVERED = "discovered"
    METADATA_READY = "metadata_ready"
    FULL_TEXT_AVAILABLE = "full_text_available"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


@dataclass(frozen=True)
class PaperAuthor:
    name: str
    author_id: str | None = None
    orcid: str | None = None


@dataclass(frozen=True)
class PaperProvenance:
    source: str
    source_id: str
    retrieved_at: str


@dataclass(frozen=True)
class ResearchPaper:
    """
    Canonical representation of a scholarly work in Genesis AI.

    This model represents existing research discovered through the
    research corpus. It is intentionally independent of any specific
    scholarly provider such as OpenAlex or Semantic Scholar.
    """

    paper_id: str
    title: str
    abstract: str | None
    authors: tuple[PaperAuthor, ...]
    publication_date: date | None
    venue: str | None
    doi: str | None

    external_ids: tuple[tuple[str, str], ...]
    source: str

    domains: tuple[str, ...]
    topics: tuple[str, ...]

    access_status: AccessStatus
    full_text_location: str | None

    processing_status: ProcessingStatus

    provenance: PaperProvenance