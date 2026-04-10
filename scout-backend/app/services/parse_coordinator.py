import asyncio

from app.services.claude_parser import parse_paper_with_claude, parse_resume_with_claude
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
    Full pipeline: extract text -> parse with Claude concurrently.

    Returns:
      {
        "resume_text": str,
        "paper_text": str | None,
        "parsed_resume": dict,        # RESUME_SCHEMA shape (from claude_parser)
        "parsed_paper": dict | None,  # PAPER_SCHEMA shape (from claude_parser)
        "github_url": str | None,
      }

    Raises ValueError for invalid file types or scanned PDFs.
    Raises RuntimeError if ANTHROPIC_API_KEY is not set.
    Per D-03: resume and paper are parsed concurrently via asyncio.gather.
    """
    # Validate file type by magic bytes before any processing
    file_type = validate_file_type(resume_filename, resume_bytes)

    # Step 1: Extract text (sync I/O, fast)
    if file_type == "pdf":
        resume_text = extract_pdf_text(resume_bytes)
    else:
        resume_text = extract_docx_text(resume_bytes)

    paper_text: str | None = None
    if paper_bytes is not None:
        validate_file_type("paper.pdf", paper_bytes)
        paper_text = extract_paper_front_matter(paper_bytes)

    # Step 2: Parse with Claude concurrently (async network I/O, ~3-8s per D-03)
    async def claude_resume() -> dict:
        return await parse_resume_with_claude(resume_text)

    async def claude_paper() -> dict | None:
        if paper_text is None:
            return None
        return await parse_paper_with_claude(paper_text)

    parsed_resume, parsed_paper = await asyncio.gather(
        claude_resume(), claude_paper(), return_exceptions=True
    )

    if isinstance(parsed_resume, Exception):
        raise parsed_resume
    if isinstance(parsed_paper, Exception):
        raise parsed_paper  # paper failure should not silently swallow; bubble up as 422

    return {
        "resume_text": resume_text,
        "paper_text": paper_text,
        "parsed_resume": parsed_resume,
        "parsed_paper": parsed_paper,
        "github_url": github_url,
    }
