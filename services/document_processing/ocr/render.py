from pathlib import Path

import pymupdf


class PDFPageRenderer:
    """Render PDF pages to raster images for OCR."""

    def render_page(
        self,
        pdf_path: str,
        *,
        page_number: int,
        output_path: str,
        dpi: int = 200,
    ) -> str:
        pdf = Path(pdf_path)
        output = Path(output_path)

        if not pdf.is_file():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if page_number < 1:
            raise ValueError("page_number must be at least 1.")

        if dpi <= 0:
            raise ValueError("dpi must be greater than 0.")

        output.parent.mkdir(parents=True, exist_ok=True)

        with pymupdf.open(pdf) as document:
            if page_number > len(document):
                raise ValueError(
                    f"page_number {page_number} exceeds PDF page count "
                    f"{len(document)}."
                )

            page = document[page_number - 1]

            scale = dpi / 72
            matrix = pymupdf.Matrix(scale, scale)

            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            pixmap.save(output)

        return str(output)