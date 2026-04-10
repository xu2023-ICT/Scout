import json
import pytest
from unittest.mock import patch, MagicMock
from app.services.claude_parser import (
    parse_resume_with_claude,
    parse_paper_with_claude,
    RESUME_SCHEMA,
    PAPER_SCHEMA,
)

SAMPLE_RESUME_OUTPUT = {
    "personal": {"name": "Alice Developer", "email": "alice@example.com",
                 "phone": "555-1234", "location": "Beijing", "linkedin": "",
                 "github": "", "website": "", "summary": "Senior SWE"},
    "education": [{"institution": "Peking University", "degree": "MS",
                   "field": "Computer Science", "start_date": "2020",
                   "end_date": "2023", "gpa": "3.9", "description": ""}],
    "work_experience": [{"company": "Acme Corp", "title": "Software Engineer",
                         "start_date": "2023-06", "end_date": "Present",
                         "location": "Beijing", "bullets": ["Built scalable APIs"]}],
    "projects": [],
    "skills": {"languages": ["Python", "TypeScript"],
                "frameworks": ["FastAPI", "Vue 3"], "tools": [], "other": []}
}

SAMPLE_PAPER_OUTPUT = {
    "title": "A Novel Approach to Attention Mechanisms",
    "authors": ["Alice Developer", "Bob Researcher"],
    "abstract": "We propose a new attention mechanism...",
    "venue": "NeurIPS 2024",
    "year": "2024",
    "doi": "10.1234/example",
    "keywords": ["attention", "transformer"],
    "key_contributions": [
        "Reduced attention complexity from O(n^2) to O(n log n)",
        "Achieved SOTA on GLUE benchmark"
    ],
    "methodology_summary": "We use sparse attention patterns...",
    "results_summary": "89.2 F1 on SQuAD, 2x speedup"
}


def make_mock_response(data: dict) -> MagicMock:
    mock = MagicMock()
    mock.content = [MagicMock(text=json.dumps(data))]
    return mock


class TestParseResumeWithClaude:
    async def test_returns_dict_with_required_keys(self):
        with patch("app.services.claude_parser.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = make_mock_response(SAMPLE_RESUME_OUTPUT)
            mock_get_client.return_value = mock_client

            result = await parse_resume_with_claude("Alice Developer\nSoftware Engineer")

        assert "personal" in result
        assert "education" in result
        assert "work_experience" in result
        assert "skills" in result

    async def test_personal_has_name(self):
        with patch("app.services.claude_parser.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = make_mock_response(SAMPLE_RESUME_OUTPUT)
            mock_get_client.return_value = mock_client

            result = await parse_resume_with_claude("Alice Developer")

        assert result["personal"]["name"] == "Alice Developer"

    async def test_uses_haiku_model(self):
        with patch("app.services.claude_parser.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = make_mock_response(SAMPLE_RESUME_OUTPUT)
            mock_get_client.return_value = mock_client

            await parse_resume_with_claude("test resume")

            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["model"] == "claude-haiku-4-5"
            assert call_kwargs["max_tokens"] == 4096


class TestParsePaperWithClaude:
    async def test_returns_dict_with_required_keys(self):
        with patch("app.services.claude_parser.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = make_mock_response(SAMPLE_PAPER_OUTPUT)
            mock_get_client.return_value = mock_client

            result = await parse_paper_with_claude("Abstract: This paper presents...")

        assert "title" in result
        assert "authors" in result
        assert "key_contributions" in result
        assert "abstract" in result

    async def test_key_contributions_is_list(self):
        with patch("app.services.claude_parser.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = make_mock_response(SAMPLE_PAPER_OUTPUT)
            mock_get_client.return_value = mock_client

            result = await parse_paper_with_claude("paper front matter")

        assert isinstance(result["key_contributions"], list)
        assert len(result["key_contributions"]) >= 1


class TestSchemaStructure:
    def test_resume_schema_has_required_top_level(self):
        required = RESUME_SCHEMA["required"]
        assert "personal" in required
        assert "education" in required
        assert "work_experience" in required
        assert "skills" in required

    def test_paper_schema_has_key_contributions(self):
        required = PAPER_SCHEMA["required"]
        assert "key_contributions" in required
        props = PAPER_SCHEMA["properties"]
        assert props["key_contributions"]["type"] == "array"
