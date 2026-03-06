"""Tests for app.utils.pdf_exporter."""

from app.utils.pdf_exporter import generate_pdf_report


def test_generate_pdf_returns_bytes():
    output = {"Section A": "Some content here."}
    result = generate_pdf_report(output)
    assert isinstance(result, bytes)


def test_generate_pdf_starts_with_pdf_header():
    output = {"Test": "content"}
    result = generate_pdf_report(output)
    # PDF files begin with the magic bytes %PDF
    assert result[:4] == b"%PDF"


def test_generate_pdf_handles_multiple_sections():
    output = {
        "Analyzer Output": "- Bug found\n- Style issue",
        "QA Review": "- Looks good",
        "Generated Tests": "def test_foo(): pass",
    }
    result = generate_pdf_report(output)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_generate_pdf_handles_empty_dict():
    result = generate_pdf_report({})
    assert isinstance(result, bytes)


def test_generate_pdf_handles_special_characters():
    output = {"Section": "code with <tags> & 'quotes' and \"double quotes\""}
    # Should not raise
    result = generate_pdf_report(output)
    assert isinstance(result, bytes)
