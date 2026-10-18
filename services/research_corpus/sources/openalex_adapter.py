from datetime import date, datetime, timezone
from typing import Any, Callable

from services.research_corpus.domain import (
    AccessStatus,
    PaperAuthor,
    PaperProvenance,
    ProcessingStatus,
    ResearchPaper,
)

from .openalex_client import OpenAlexClient


class OpenAlexAdapter:
    """Convert OpenAlex works into Genesis AI ResearchPaper objects."""

    def __init__(
    self,
    client: OpenAlexClient,
    *,
    clock: Callable[[], datetime] | None = None,
) -> None:
     self.client = client
     self.clock = clock or (
        lambda: datetime.now(timezone.utc)
    )

    @property
    def name(self) -> str:
        return "openalex"

    def search_papers(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> tuple[ResearchPaper, ...]:
        works = self.client.search_works(
            query,
            limit=limit,
        )

        return tuple(
            self._normalize_work(work)
            for work in works
        )

    def get_paper(
        self,
        paper_id: str,
    ) -> ResearchPaper | None:
        work = self.client.get_work(paper_id)

        if work is None:
            return None

        return self._normalize_work(work)

    def get_related_papers(
        self,
        paper_id: str,
        *,
        limit: int = 10,
    ) -> tuple[ResearchPaper, ...]:
        raise NotImplementedError(
            "OpenAlex related-paper retrieval will be implemented "
            "after the core work adapter."
        )

    def get_citations(
        self,
        paper_id: str,
        *,
        limit: int = 10,
    ) -> tuple[ResearchPaper, ...]:
        raise NotImplementedError(
            "OpenAlex citation retrieval will be implemented "
            "after the core work adapter."
        )

    def _normalize_work(
        self,
        work: dict[str, Any],
    ) -> ResearchPaper:
        openalex_id = self._extract_openalex_id(work)

        return ResearchPaper(
            paper_id=f"openalex:{openalex_id}",
            title=self._extract_title(work),
            abstract=self._reconstruct_abstract(work),
            authors=self._extract_authors(work),
            publication_date=self._extract_publication_date(work),
            venue=self._extract_venue(work),
            doi=self._extract_doi(work),
            external_ids=self._extract_external_ids(
                work,
                openalex_id,
            ),
            source="openalex",
            domains=self._extract_domains(work),
            topics=self._extract_topics(work),
            access_status=self._extract_access_status(work),
            full_text_location=self._extract_full_text_location(
                work,
            ),
            processing_status=ProcessingStatus.DISCOVERED,
            provenance=PaperProvenance(
            source="openalex",
            source_id=openalex_id,
            retrieved_at=self.clock().isoformat(),
            ),
        )

    @staticmethod
    def _extract_openalex_id(
        work: dict[str, Any],
    ) -> str:
        raw_id = work.get("id")

        if not raw_id:
            raise ValueError("OpenAlex work is missing id")

        return str(raw_id).rstrip("/").split("/")[-1]

    @staticmethod
    def _extract_title(
        work: dict[str, Any],
    ) -> str:
        title = work.get("display_name")

        if not title:
            raise ValueError(
                "OpenAlex work is missing display_name"
            )

        return str(title).strip()

    @staticmethod
    def _reconstruct_abstract(
        work: dict[str, Any],
    ) -> str | None:
        inverted_index = work.get("abstract_inverted_index")

        if not inverted_index:
            return None

        words: list[tuple[int, str]] = []

        for word, positions in inverted_index.items():
            for position in positions:
                words.append((position, word))

        words.sort(key=lambda item: item[0])

        return " ".join(
            word
            for _, word in words
        )

    @staticmethod
    def _extract_authors(
        work: dict[str, Any],
    ) -> tuple[PaperAuthor, ...]:
        authors: list[PaperAuthor] = []

        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})

            name = author.get("display_name")

            if not name:
                continue

            author_id = author.get("id")

            if author_id:
                author_id = str(author_id).rstrip("/").split("/")[-1]

            authors.append(
                PaperAuthor(
                    name=str(name),
                    author_id=author_id,
                    orcid=author.get("orcid"),
                )
            )

        return tuple(authors)

    @staticmethod
    def _extract_publication_date(
        work: dict[str, Any],
    ) -> date | None:
        raw_date = work.get("publication_date")

        if not raw_date:
            return None

        return date.fromisoformat(str(raw_date))

    @staticmethod
    def _extract_venue(
        work: dict[str, Any],
    ) -> str | None:
        primary_location = work.get("primary_location") or {}
        source = primary_location.get("source") or {}

        display_name = source.get("display_name")

        return (
            str(display_name).strip()
            if display_name
            else None
        )

    @staticmethod
    def _extract_doi(
        work: dict[str, Any],
    ) -> str | None:
        doi = work.get("doi")

        if not doi:
            return None

        return str(doi).removeprefix(
            "https://doi.org/"
        ).strip()

    @staticmethod
    def _extract_external_ids(
        work: dict[str, Any],
        openalex_id: str,
    ) -> tuple[tuple[str, str], ...]:
        identifiers: list[tuple[str, str]] = [
            ("openalex", openalex_id),
        ]

        doi = OpenAlexAdapter._extract_doi(work)

        if doi:
            identifiers.append(("doi", doi))

        ids = work.get("ids") or {}

        for provider in ("pmid", "pmcid", "mag"):
            value = ids.get(provider)

            if value:
                identifiers.append(
                    (provider, str(value))
                )

        return tuple(identifiers)

    @staticmethod
    def _extract_domains(
        work: dict[str, Any],
    ) -> tuple[str, ...]:
        domains: list[str] = []

        for topic in work.get("topics", []):
            domain = topic.get("domain") or {}
            display_name = domain.get("display_name")

            if display_name:
                domains.append(str(display_name))

        return tuple(dict.fromkeys(domains))

    @staticmethod
    def _extract_topics(
        work: dict[str, Any],
    ) -> tuple[str, ...]:
        topics: list[str] = []

        for topic in work.get("topics", []):
            display_name = topic.get("display_name")

            if display_name:
                topics.append(str(display_name))

        return tuple(dict.fromkeys(topics))

    @staticmethod
    def _extract_access_status(
        work: dict[str, Any],
    ) -> AccessStatus:
        open_access = work.get("open_access") or {}

        if open_access.get("is_oa") is True:
            return AccessStatus.OPEN_ACCESS

        return AccessStatus.UNKNOWN

    @staticmethod
    def _extract_full_text_location(
        work: dict[str, Any],
    ) -> str | None:
        open_access = work.get("open_access") or {}

        url = open_access.get("oa_url")

        if url:
            return str(url)

        best_oa_location = work.get(
            "best_oa_location"
        ) or {}

        url = best_oa_location.get("pdf_url")

        if url:
            return str(url)

        return None

   