from dataclasses import dataclass

from services.research_corpus.domain.paper import ResearchPaper
from services.research_corpus.sources.interface import ScholarlySource


@dataclass(frozen=True)
class RetrievalCandidate:
    rank: int
    paper: ResearchPaper
    source: str


class RetrievalService:
    """
    Retrieves scholarly candidate papers through a ScholarlySource.

    RetrievalService is deliberately independent of provider-specific
    implementations. Ranking here preserves the source-provided ordering;
    semantic ranking and reranking are separate future capabilities.
    """

    def __init__(self, source: ScholarlySource) -> None:
        self._source = source

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> tuple[RetrievalCandidate, ...]:
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("query must not be empty")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        papers = self._source.search_papers(
            normalized_query,
            limit=limit,
        )

        return tuple(
            RetrievalCandidate(
                rank=index,
                paper=paper,
                source=self._source.name,
            )
            for index, paper in enumerate(papers, start=1)
        )
