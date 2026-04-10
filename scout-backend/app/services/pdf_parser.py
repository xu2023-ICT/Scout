import fitz  # PyMuPDF
import pymupdf4llm

ALLOWED_MAGIC = {
    b"%PDF": "pdf",
    b"PK\x03\x04": "docx",  # DOCX is a ZIP container
}


def validate_file_type(filename: str, file_bytes: bytes) -> str:
    """Returns 'pdf' or 'docx'. Raises ValueError for unsupported types."""
    for magic, file_type in ALLOWED_MAGIC.items():
        if file_bytes[: len(magic)] == magic:
            return file_type
    raise ValueError(
        f"Unsupported file type for '{filename}'. "
        "Please upload a PDF (.pdf) or Word document (.docx)."
    )


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Returns LLM-ready markdown string. Raises ValueError if scanned PDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_chars = sum(len(page.get_text()) for page in doc)

    if total_chars < 100:
        try:
            md_text = pymupdf4llm.to_markdown(doc, use_ocr=True)
        except Exception:
            doc.close()
            raise ValueError(
                "This PDF appears to be a scanned image. Please upload a text-based PDF. "
                "If you only have a scanned copy, convert it to text-based PDF first."
            )
        if len(md_text.strip()) < 50:
            doc.close()
            raise ValueError(
                "Could not extract text from this PDF (scanned or image-only). "
                "Please upload a text-based PDF."
            )
    else:
        md_text = pymupdf4llm.to_markdown(doc)

    doc.close()
    return md_text


def extract_paper_front_matter(pdf_bytes: bytes, max_pages: int = 4) -> str:
    """Extract only first N pages of paper PDF to keep token cost low."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = list(range(min(max_pages, len(doc))))
    md_text = pymupdf4llm.to_markdown(doc, pages=pages)
    doc.close()
    return md_text
