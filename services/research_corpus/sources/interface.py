from typing import Protocol

from services.research_corpus.domain import ResearchPaper


class ScholarlySource(Protocol):
    """
    Provider-independent interface for scholarly research sources.

    Implementations may connect to OpenAlex, Semantic Scholar,
    Crossref, arXiv, or other legitimate scholarly sources.
    """

    @property
    def name(self) -> str:
        """Return the unique source name."""
        ...

    def search_papers(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> tuple[ResearchPaper, ...]:
        """Search the source and return normalized research papers."""
        ...

    def get_paper(
        self,
        paper_id: str,
    ) -> ResearchPaper | None:
        """Retrieve and normalize a single research paper."""
        ...

    def get_related_papers(
        self,
        paper_id: str,
        *,
        limit: int = 10,
    ) -> tuple[ResearchPaper, ...]:
        """Return papers related to the requested paper."""
        ...

    def get_citations(
        self,
        paper_id: str,
        *,
        limit: int = 10,
    ) -> tuple[ResearchPaper, ...]:
        """Return papers that cite the requested paper."""
        ...