from services.document_processing.structure import StructuredDocument

from .citation_extractor import BaselineCitationExtractor
from .interface import ScholarlyDocument
from .reference_extractor import BaselineReferenceExtractor


class BaselineScholarlyExtractor:
    """Combine baseline reference and citation extraction."""

    def __init__(
        self,
        reference_extractor: BaselineReferenceExtractor | None = None,
        citation_extractor: BaselineCitationExtractor | None = None,
    ) -> None:
        self.reference_extractor = (
            reference_extractor or BaselineReferenceExtractor()
        )
        self.citation_extractor = (
            citation_extractor or BaselineCitationExtractor()
        )

    def extract(
        self,
        document: StructuredDocument,
    ) -> ScholarlyDocument:
        references = self.reference_extractor.extract_references(document)
        citations = self.citation_extractor.extract_citations(
            document,
            references,
        )

        return ScholarlyDocument(
            references=references,
            citations=citations,
        )