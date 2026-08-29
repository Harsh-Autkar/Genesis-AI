from services.document_processing.parsing import PageText, ParsedDocument
from services.document_processing.structure import (
    HeuristicStructureDetector,
    SectionType,
)


def make_document(text: str) -> ParsedDocument:
    return ParsedDocument(
        page_count=1,
        pages=(PageText(page_number=1, text=text),),
        metadata={},
        extraction_method="test",
        extraction_confidence=1.0,
    )


def test_detects_common_research_sections():
    document = make_document(
        """
        ABSTRACT
        This paper introduces Genesis-AI.

        1 Introduction
        Research motivation and context.

        2 Methodology
        We describe the proposed method.

        3 Results
        The experimental results are reported.

        4 Conclusion
        We conclude the study.
        """
    )

    result = HeuristicStructureDetector().detect(document)

    section_types = [section.section_type for section in result.sections]

    assert section_types == [
        SectionType.ABSTRACT,
        SectionType.INTRODUCTION,
        SectionType.METHODS,
        SectionType.RESULTS,
        SectionType.CONCLUSION,
    ]


def test_preserves_original_heading():
    document = make_document(
        """
        2.1 Materials and Methods
        Experimental procedure.
        """
    )

    result = HeuristicStructureDetector().detect(document)

    section = result.sections[0]

    assert section.original_heading == "2.1 Materials and Methods"
    assert section.section_type == SectionType.METHODS
    assert section.start_page == 1
    assert section.end_page == 1


def test_unknown_heading_becomes_other():
    document = make_document(
        """
        5 Implementation Details
        System implementation information.
        """
    )

    result = HeuristicStructureDetector().detect(document)

    section = result.sections[0]

    assert section.section_type == SectionType.OTHER
    assert section.original_heading == "5 Implementation Details"


def test_multpage_section_preserves_page_range():
    document = ParsedDocument(
        page_count=2,
        pages=(
            PageText(
                page_number=1,
                text="1 Introduction\nFirst page content.",
            ),
            PageText(
                page_number=2,
                text="Continuation of introduction.",
            ),
        ),
        metadata={},
        extraction_method="test",
        extraction_confidence=1.0,
    )

    result = HeuristicStructureDetector().detect(document)

    section = result.sections[0]

    assert section.section_type == SectionType.INTRODUCTION
    assert section.start_page == 1
    assert section.end_page == 2
    assert "Continuation of introduction." in section.text


def test_no_detectable_structure_returns_empty_result():
    document = make_document(
        "This is ordinary body text without section headings."
    )

    result = HeuristicStructureDetector().detect(document)

    assert result.sections == ()
    assert result.structure_confidence == 0.0
    def test_numbered_body_sentence_is_not_heading():
     document = make_document(
        """
        1 We evaluated the proposed model on three datasets.
        The results are reported below.
        """
    )

    result = HeuristicStructureDetector().detect(document)

    assert result.sections == ()


def test_short_normal_sentence_is_not_heading():
    document = make_document(
        """
        We evaluate the model.
        This section contains ordinary research text.
        """
    )

    result = HeuristicStructureDetector().detect(document)

    assert result.sections == ()


def test_uppercase_acronym_in_body_is_not_heading():
    document = make_document(
        """
        CNN models were used for image classification.
        The evaluation follows the standard protocol.
        """
    )

    result = HeuristicStructureDetector().detect(document)

    assert result.sections == ()


def test_text_before_first_heading_is_not_lost():
    document = make_document(
        """
        This paragraph appears before the first detected section.

        1 Introduction
        This is the introduction text.
        """
    )

    result = HeuristicStructureDetector().detect(document)

    assert len(result.sections) == 1
    assert result.sections[0].section_type == SectionType.INTRODUCTION
    assert "This paragraph appears before" not in result.sections[0].text


def test_multiple_sections_are_closed_consistently():
    document = make_document(
        """
        ABSTRACT
        Abstract content.

        1 Introduction
        Introduction content.

        2 Methods
        Methods content.

        3 Results
        Results content.
        """
    )

    result = HeuristicStructureDetector().detect(document)

    assert len(result.sections) == 4
    assert result.sections[-1].section_type == SectionType.RESULTS
    assert result.sections[-1].text == "Results content."