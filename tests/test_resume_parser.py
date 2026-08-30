from pathlib import Path

from src.resume_parser import extract_text_from_pdf


def test_resume_parser_requires_existing_file():

    fake_pdf = Path("tests/nonexistent_resume.pdf")

    try:
        extract_text_from_pdf(fake_pdf)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        assert True