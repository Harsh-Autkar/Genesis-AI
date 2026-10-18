from typing import Protocol

from services.research_corpus.domain import ResearchPaper


class LiteratureRepository(Protocol):
    """Persistence contract for scholarly literature."""

    def save(
        self,
        paper: ResearchPaper,
    ) -> ResearchPaper:
        """Persist a research paper and return the stored representation."""
        ...

    def get_by_paper_id(
        self,
        paper_id: str,
    ) -> ResearchPaper | None:
        """Retrieve a paper by its provider-qualified Genesis paper ID."""
        ...

    def find_by_external_id(
        self,
        *,
        provider: str,
        external_id: str,
    ) -> ResearchPaper | None:
        """Find a paper using a provider-specific identifier."""
        ...

    def find_by_doi(
        self,
        doi: str,
    ) -> ResearchPaper | None:
        """Find a paper by normalized DOI."""
        ...