import pytest
import fitz
from app.services.pdf_parser import extract_pdf_text, extract_paper_front_matter, validate_file_type


def make_text_pdf(text: str = "John Doe\njohn@example.com\nSoftware Engineer") -> bytes:
    """Create a minimal text-based PDF in memory."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text, fontsize=12)
    return doc.tobytes()


def make_minimal_pdf_bytes() -> bytes:
    """Create a near-empty PDF (simulates scanned — no selectable text)."""
    # A PDF with a blank page has 0 extractable chars
    doc = fitz.open()
    doc.new_page()
    return doc.tobytes()


class TestExtractPdfText:
    def test_extracts_text_from_text_pdf(self):
        pdf_bytes = make_text_pdf("John Doe\njohn@example.com\nSoftware Engineer at Acme")
        result = extract_pdf_text(pdf_bytes)
        assert "John" in result
        assert len(result) > 10

    def test_raises_for_scanned_pdf(self):
        # Blank page = 0 chars = treated as scanned
        pdf_bytes = make_minimal_pdf_bytes()
        with pytest.raises(ValueError, match="scanned"):
            extract_pdf_text(pdf_bytes)


class TestValidateFileType:
    def test_accepts_pdf_magic(self):
        pdf_bytes = make_text_pdf()
        assert validate_file_type("resume.pdf", pdf_bytes) == "pdf"

    def test_rejects_unknown_bytes(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            validate_file_type("malware.exe", b"\x4d\x5a\x90\x00" + b"\x00" * 100)
