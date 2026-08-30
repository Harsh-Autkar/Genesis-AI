from .interface import (
    CitationOccurrence,
    Reference,
    ScholarlyDocument,
    ScholarlyExtractor,
)
from .reference_extractor import BaselineReferenceExtractor

__all__ = [
    "Reference",
    "CitationOccurrence",
    "ScholarlyDocument",
    "ScholarlyExtractor",
    "BaselineReferenceExtractor",
    "BaselineCitationExtractor","BaselineScholarlyExtractor",
]

from .citation_extractor import BaselineCitationExtractor

from .extractor import BaselineScholarlyExtractor