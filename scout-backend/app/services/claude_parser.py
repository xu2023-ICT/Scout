"""
Claude Haiku 4.5 structured output parser for resumes and academic papers.

Uses output_config.format JSON schema mode for guaranteed valid JSON output
(no hand-rolled parsing or retry loops needed per RESEARCH.md "Don't Hand-Roll" table).

Cost estimates (per RESEARCH.md):
  - Resume parse: ~$0.011 per call (claude-haiku-4-5, ~3,000 input + ~1,500 output tokens)
  - Paper parse:  ~$0.009 per call (claude-haiku-4-5, ~5,000 input + ~800 output tokens)
  - Total per upload session: ~$0.02
"""

import json
import os

import anthropic

# ---------------------------------------------------------------------------
# Client factory (lazy initialization, env var read at first call)
# ---------------------------------------------------------------------------

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    """Return a cached Anthropic client. Raises RuntimeError if API key is missing."""
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Set it in your .env file. See .env.example."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


# ---------------------------------------------------------------------------
# JSON schemas
# ---------------------------------------------------------------------------

# RESUME_SCHEMA — from RESEARCH.md Pattern 3 (verbatim, with additionalProperties: False)
RESUME_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "personal": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "location": {"type": "string"},
                "linkedin": {"type": "string"},
                "github": {"type": "string"},
                "website": {"type": "string"},
                "summary": {"type": "string"},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "field": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "gpa": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["institution", "degree"],
                "additionalProperties": False,
            },
        },
        "work_experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "title": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "location": {"type": "string"},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["company", "title"],
                "additionalProperties": False,
            },
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "technologies": {"type": "array", "items": {"type": "string"}},
                    "url": {"type": "string"},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        },
        "skills": {
            "type": "object",
            "properties": {
                "languages": {"type": "array", "items": {"type": "string"}},
                "frameworks": {"type": "array", "items": {"type": "string"}},
                "tools": {"type": "array", "items": {"type": "string"}},
                "other": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": False,
        },
    },
    "required": ["personal", "education", "work_experience", "skills"],
    "additionalProperties": False,
}

# PAPER_SCHEMA — from RESEARCH.md Paper Extraction section (verbatim)
PAPER_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "authors": {"type": "array", "items": {"type": "string"}},
        "abstract": {"type": "string"},
        "venue": {"type": "string"},
        "year": {"type": "string"},
        "doi": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "key_contributions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "methodology_summary": {"type": "string"},
        "results_summary": {"type": "string"},
    },
    "required": ["title", "authors", "abstract", "key_contributions"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Parser functions
# ---------------------------------------------------------------------------


async def parse_resume_with_claude(markdown_text: str) -> dict:
    """
    Parse resume markdown into RESUME_SCHEMA-shaped dict.

    Uses claude-haiku-4-5 with output_config.format for guaranteed valid JSON.
    max_tokens=4096 prevents truncation on long CVs (RESEARCH.md Pitfall 4).

    Args:
        markdown_text: LLM-ready markdown from pdf_parser.extract_pdf_text()
                       or docx_parser.extract_docx_text()

    Returns:
        dict matching RESUME_SCHEMA (personal, education, work_experience,
        projects, skills)

    Raises:
        RuntimeError: if ANTHROPIC_API_KEY is not set
        anthropic.AuthenticationError: if API key is invalid
    """
    client = get_client()
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,  # Pitfall 4: set high to avoid truncation on long resumes
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract all resume information from the following resume text. "
                    "Be thorough — capture every bullet point, date, and detail exactly as written. "
                    "Do not infer or add information not present in the text. "
                    "If a field is not present, use an empty string or empty array.\n\n"
                    f"Resume text:\n{markdown_text}"
                ),
            }
        ],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": RESUME_SCHEMA,
            }
        },
    )
    return json.loads(response.content[0].text)


async def parse_paper_with_claude(markdown_text: str) -> dict:
    """
    Extract academic paper metadata from front-matter markdown.

    Uses claude-haiku-4-5 with output_config.format for guaranteed valid JSON.
    max_tokens=2048 is sufficient for structured paper metadata output.

    Args:
        markdown_text: first N pages of paper PDF via pdf_parser.extract_paper_front_matter()

    Returns:
        dict matching PAPER_SCHEMA (title, authors, abstract, key_contributions, ...)

    Raises:
        RuntimeError: if ANTHROPIC_API_KEY is not set
        anthropic.AuthenticationError: if API key is invalid
    """
    client = get_client()
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,  # paper metadata output is smaller than full resume
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract the academic paper metadata from the following text. "
                    "Focus on: title, authors, abstract, publication venue (journal/conference), "
                    "year, DOI, keywords, and key contributions (3-5 bullet points summarizing "
                    "what is novel about this paper).\n\n"
                    f"Paper text:\n{markdown_text}"
                ),
            }
        ],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": PAPER_SCHEMA,
            }
        },
    )
    return json.loads(response.content[0].text)
