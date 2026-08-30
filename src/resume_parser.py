from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract text from a PDF resume.

    Parameters
    ----------
    pdf_path:
        Path to the resume PDF.

    Returns
    -------
    str
        Extracted text from all PDF pages.

    Raises
    ------
    FileNotFoundError
        If the PDF does not exist.

    ValueError
        If the supplied file is not a PDF.
    """

    pdf_path = Path(pdf_path)

    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"Resume file not found: {pdf_path}"
        )

    # --------------------------------------------------------
    # CHECK EXTENSION
    # --------------------------------------------------------

    if pdf_path.suffix.lower() != ".pdf":

        raise ValueError(
            "Only PDF files are supported."
        )

    # --------------------------------------------------------
    # READ PDF
    # --------------------------------------------------------

    reader = PdfReader(str(pdf_path))

    extracted_pages = []

    for page in reader.pages:

        try:

            text = page.extract_text()

        except Exception:
            text = None

        if text:

            extracted_pages.append(
                text.strip()
            )

    # --------------------------------------------------------
    # COMBINE ALL PAGES
    # --------------------------------------------------------

    resume_text = "\n".join(
        extracted_pages
    )

    return resume_text.strip()