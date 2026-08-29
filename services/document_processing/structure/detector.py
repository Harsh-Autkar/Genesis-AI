import re

from services.document_processing.parsing import ParsedDocument

from .interface import (
    DocumentSection,
    SectionType,
    StructuredDocument,
)


SECTION_ALIASES: dict[SectionType, set[str]] = {
    SectionType.ABSTRACT: {
        "abstract",
        "summary",
    },
    SectionType.INTRODUCTION: {
        "introduction",
        "background",
    },
    SectionType.RELATED_WORK: {
        "related work",
        "literature review",
        "related literature",
        "state of the art",
    },
    SectionType.METHODS: {
        "method",
        "methods",
        "methodology",
        "materials and methods",
        "research methodology",
    },
    SectionType.EXPERIMENTS: {
        "experiment",
        "experiments",
        "experimental setup",
        "experimental study",
    },
    SectionType.RESULTS: {
        "result",
        "results",
        "findings",
        "experimental results",
    },
    SectionType.DISCUSSION: {
        "discussion",
        "analysis and discussion",
    },
    SectionType.CONCLUSION: {
        "conclusion",
        "conclusions",
        "future work",
        "conclusion and future work",
    },
    SectionType.REFERENCES: {
        "reference",
        "references",
        "bibliography",
    },
}


_NUMBER_PREFIX = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*|[IVXLCDM]+)[.)]?\s+",
    re.IGNORECASE,
)


def normalize_heading(heading: str) -> str:
    normalized = _NUMBER_PREFIX.sub("", heading.strip())
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip().lower()


def classify_heading(heading: str) -> tuple[SectionType, float]:
    normalized = normalize_heading(heading)

    for section_type, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return section_type, 1.0

    return SectionType.OTHER, 0.5


def looks_like_heading(line: str) -> bool:
    stripped = line.strip()

    if not stripped:
        return False

    if len(stripped) > 120:
        return False

    words = stripped.split()

    if len(words) > 12:
        return False

    if stripped.endswith((".", ",", ";", ":")):
        return False

    normalized = normalize_heading(stripped)

    # Known section heading.
    if any(
        normalized in aliases
        for aliases in SECTION_ALIASES.values()
    ):
        return True

    # Numbered heading, e.g. "1 Introduction" or "2.1 Methodology".
    if _NUMBER_PREFIX.match(stripped):
        heading_text = _NUMBER_PREFIX.sub("", stripped).strip()

        if not heading_text:
            return False

        if len(heading_text.split()) > 8:
            return False

        if heading_text.endswith((".", ",", ";", ":")):
            return False

        return heading_text[0].isupper()

    # Short all-uppercase headings such as "ABSTRACT".
    if stripped.isupper() and len(words) <= 8:
        return True

    return False

    normalized = normalize_heading(stripped)

    return any(
        normalized in aliases
        for aliases in SECTION_ALIASES.values()
    )


class HeuristicStructureDetector:
    """Detect common research-paper sections using text heuristics."""

    def detect(self, document: ParsedDocument) -> StructuredDocument:
        sections: list[DocumentSection] = []

        current_heading: str | None = None
        current_type: SectionType | None = None
        current_confidence = 0.0
        current_start_page: int | None = None
        current_text: list[str] = []

        def flush(end_page: int) -> None:
            if current_heading is None or current_start_page is None:
                return

            sections.append(
                DocumentSection(
                    section_type=current_type or SectionType.OTHER,
                    original_heading=current_heading,
                    text="\n".join(current_text).strip(),
                    start_page=current_start_page,
                    end_page=end_page,
                    confidence=current_confidence,
                )
            )

        for page in document.pages:
            lines = page.text.splitlines()

            for line in lines:
                if looks_like_heading(line):
                    if current_heading is not None:
                        flush(page.page_number)

                    section_type, confidence = classify_heading(line)

                    current_heading = line.strip()
                    current_type = section_type
                    current_confidence = confidence
                    current_start_page = page.page_number
                    current_text = []
                elif current_heading is not None:
                    current_text.append(line)

        if current_heading is not None:
            flush(document.page_count)

        if not sections:
            return StructuredDocument(
                sections=(),
                structure_confidence=0.0,
            )

        average_confidence = sum(
            section.confidence for section in sections
        ) / len(sections)

        return StructuredDocument(
            sections=tuple(sections),
            structure_confidence=average_confidence,
        )