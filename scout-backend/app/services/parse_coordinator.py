import asyncio

from app.services.docx_parser import extract_docx_text
from app.services.pdf_parser import (
    extract_paper_front_matter,
    extract_pdf_text,
    validate_file_type,
)


async def parse_all(
    resume_bytes: bytes,
    resume_filename: str,
    paper_bytes: bytes | None,
    github_url: str | None,
) -> dict:
    """
    Extract text from resume and optional paper concurrently.
    Returns {"resume_text": str, "paper_text": str | None, "github_url": str | None}
    Raises ValueError for invalid file types or scanned PDFs.
    """
    # Validate file type by magic bytes before any processing
    file_type = validate_file_type(resume_filename, resume_bytes)

    async def extract_resume() -> str:
        if file_type == "pdf":
            return extract_pdf_text(resume_bytes)
        else:
            return extract_docx_text(resume_bytes)

    async def extract_paper() -> str | None:
        if paper_bytes is None:
            return None
        validate_file_type("paper.pdf", paper_bytes)  # must be PDF
        return extract_paper_front_matter(paper_bytes)

    # Run concurrently per D-03
    resume_text, paper_text = await asyncio.gather(
        extract_resume(), extract_paper(), return_exceptions=True
    )

    if isinstance(resume_text, Exception):
        raise resume_text
    if isinstance(paper_text, Exception):
        raise paper_text  # paper errors bubble up as 422

    return {
        "resume_text": resume_text,
        "paper_text": paper_text,
        "github_url": github_url,
    }
