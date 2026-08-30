import re

from services.document_processing.structure import (
    SectionType,
    StructuredDocument,
)

from .interface import CitationOccurrence, Reference


_CITATION_PATTERN = re.compile(
    r"\[(\d+(?:\s*[,;-]\s*\d+)*)\]"
)


class BaselineCitationExtractor:
    """Extract numeric citation occurrences from document sections."""

    def extract_citations(
        self,
        document: StructuredDocument,
        references: tuple[Reference, ...],
    ) -> tuple[CitationOccurrence, ...]:
        reference_map = {
            reference.reference_id: reference
            for reference in references
        }

        citations: list[CitationOccurrence] = []
        citation_counter = 0

        for section in document.sections:
            if section.section_type == SectionType.REFERENCES:
                continue

            for match in _CITATION_PATTERN.finditer(section.text):
                numbers = self._expand_numbers(match.group(1))

                context = self._extract_context(
                    section.text,
                    match.start(),
                    match.end(),
                )

                for number in numbers:
                    reference_id = f"ref-{number}"

                    if reference_id not in reference_map:
                        continue

                    citation_counter += 1

                    citations.append(
                        CitationOccurrence(
                            citation_id=f"cit-{citation_counter}",
                            reference_id=reference_id,
                            page_number=section.start_page,
                            context=context,
                        )
                    )

        return tuple(citations)

    @staticmethod
    def _expand_numbers(value: str) -> list[int]:
        numbers: list[int] = []

        for part in re.split(r"\s*[,;]\s*", value):
            if "-" in part or "–" in part:
                bounds = re.split(r"\s*[-–]\s*", part)

                if len(bounds) != 2:
                    continue

                start, end = map(int, bounds)
                numbers.extend(range(start, end + 1))
            else:
                numbers.append(int(part))

        return numbers

    @staticmethod
    def _extract_context(
        text: str,
        start: int,
        end: int,
    ) -> str:
        sentence_start = max(
            text.rfind(".", 0, start) + 1,
            text.rfind("!", 0, start) + 1,
            text.rfind("?", 0, start) + 1,
        )

        sentence_end_candidates = [
            position
            for position in (
                text.find(".", end),
                text.find("!", end),
                text.find("?", end),
            )
            if position != -1
        ]

        sentence_end = (
            min(sentence_end_candidates) + 1
            if sentence_end_candidates
            else len(text)
        )

        return text[sentence_start:sentence_end].strip()