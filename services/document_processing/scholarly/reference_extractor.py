import re

from services.document_processing.structure import (
    SectionType,
    StructuredDocument,
)

from .interface import Reference


_REFERENCE_START = re.compile(r"(?m)^\s*\[\s*(\d+)\s*\]\s*")
_YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
_DOI_PATTERN = re.compile(
    r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b",
    re.IGNORECASE,
)


class BaselineReferenceExtractor:
    """Extract basic bibliographic references from a structured document."""

    def extract_references(
        self,
        document: StructuredDocument,
    ) -> tuple[Reference, ...]:
        reference_section = next(
            (
                section
                for section in document.sections
                if section.section_type == SectionType.REFERENCES
            ),
            None,
        )

        if reference_section is None:
            return ()

        entries = self._split_references(reference_section.text)

        return tuple(
            self._build_reference(index, entry)
            for index, entry in enumerate(entries, start=1)
        )

    @staticmethod
    def _split_references(text: str) -> list[str]:
        matches = list(_REFERENCE_START.finditer(text))

        if not matches:
            return [text.strip()] if text.strip() else []

        references: list[str] = []

        for index, match in enumerate(matches):
            start = match.start()
            end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            )

            entry = text[start:end].strip()

            if entry:
                references.append(entry)

        return references

    @staticmethod
    def _build_reference(index: int, raw_text: str) -> Reference:
        year_match = _YEAR_PATTERN.search(raw_text)
        doi_match = _DOI_PATTERN.search(raw_text)

        return Reference(
            reference_id=f"ref-{index}",
            raw_text=raw_text,
            title=None,
            authors=(),
            year=int(year_match.group()) if year_match else None,
            doi=doi_match.group() if doi_match else None,
        )