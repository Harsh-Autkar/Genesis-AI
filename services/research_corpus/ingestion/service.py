from dataclasses import dataclass

from services.research_corpus.domain.paper import ResearchPaper
from services.research_corpus.persistence.repository import (
    PostgreSQLLiteratureRepository,
)
from services.research_corpus.sources.interface import ScholarlySource


@dataclass(frozen=True)
class IngestionResult:
    query: str
    retrieved: int
    new_papers: int
    existing_papers: int
    failed_papers: int
    saved_paper_ids: tuple[str, ...]
    failed_paper_ids: tuple[str, ...]


class ResearchCorpusIngestionService:
    """
    Coordinates scholarly discovery and corpus persistence.

    Scholarly-source-specific behavior remains behind ScholarlySource,
    while persistence remains behind PostgreSQLLiteratureRepository.
    """

    def __init__(
        self,
        source: ScholarlySource,
        repository: PostgreSQLLiteratureRepository,
    ) -> None:
        self._source = source
        self._repository = repository

    def ingest(self, query: str, *, limit: int = 50) -> IngestionResult:
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("query must not be empty")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        papers = self._source.search_papers(
            normalized_query,
            limit=limit,
        )

        new_papers = 0
        existing_papers = 0
        failed_papers = 0

        saved_paper_ids: list[str] = []
        failed_paper_ids: list[str] = []

        seen_paper_ids: set[str] = set()

        for paper in papers:
            if paper.paper_id in seen_paper_ids:
                existing_papers += 1
                continue

            seen_paper_ids.add(paper.paper_id)

            if self._exists(paper):
                existing_papers += 1
                continue

            try:
                self._repository.save(paper)
            except Exception:
                failed_papers += 1
                failed_paper_ids.append(paper.paper_id)
                continue

            new_papers += 1
            saved_paper_ids.append(paper.paper_id)

        return IngestionResult(
            query=normalized_query,
            retrieved=len(papers),
            new_papers=new_papers,
            existing_papers=existing_papers,
            failed_papers=failed_papers,
            saved_paper_ids=tuple(saved_paper_ids),
            failed_paper_ids=tuple(failed_paper_ids),
        )

    def _exists(self, paper: ResearchPaper) -> bool:
        if self._repository.get_by_paper_id(paper.paper_id) is not None:
            return True

        if paper.doi:
            if self._repository.find_by_doi(paper.doi) is not None:
                return True

        for provider, external_id in paper.external_ids:
            if (
                self._repository.find_by_external_id(
                    provider=provider,
                    external_id=external_id,
                )
                is not None
            ):
                return True

        return False
