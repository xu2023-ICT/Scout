import io
from unittest.mock import AsyncMock, patch

import fitz
import pytest
from docx import Document


def make_pdf_bytes(text="John Doe Engineer") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    # Insert enough text to exceed the 100-char scanned-PDF detection threshold
    full_text = text + "\nSoftware Engineer | john@example.com | github.com/johndoe\nExperience: 5 years Python, FastAPI, SQLAlchemy, Docker, AWS"
    page.insert_text((50, 50), full_text, fontsize=12)
    return doc.tobytes()


def make_docx_bytes(text="Jane Smith Developer") -> bytes:
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


MOCK_PARSE_RESULT = {
    "resume_text": "John Doe Software Engineer",
    "paper_text": None,
    "parsed_resume": {
        "personal": {"name": "John Doe", "email": "john@example.com",
                     "phone": "", "location": "", "linkedin": "", "github": "",
                     "website": "", "summary": ""},
        "education": [], "work_experience": [], "projects": [],
        "skills": {"languages": [], "frameworks": [], "tools": [], "other": []}
    },
    "parsed_paper": None,
    "github_url": None,
}

MOCK_PARSE_RESULT_WITH_GITHUB = {
    **MOCK_PARSE_RESULT,
    "github_url": "https://github.com/charlie",
}

MOCK_PARSE_RESULT_WITH_PAPER = {
    "resume_text": "Diana Researcher",
    "paper_text": "Abstract: This paper presents a novel approach",
    "parsed_resume": {
        "personal": {"name": "Diana Researcher", "email": "", "phone": "",
                     "location": "", "linkedin": "", "github": "", "website": "", "summary": ""},
        "education": [], "work_experience": [], "projects": [],
        "skills": {"languages": [], "frameworks": [], "tools": [], "other": []}
    },
    "parsed_paper": {
        "title": "A Novel Approach",
        "authors": ["Diana Researcher"],
        "abstract": "Abstract: This paper presents a novel approach",
        "venue": "NeurIPS 2024",
        "year": "2024",
        "doi": "",
        "keywords": [],
        "key_contributions": ["Novel contribution 1"],
        "methodology_summary": "",
        "results_summary": "",
    },
    "github_url": None,
}


class TestUploadEndpoint:
    async def test_upload_pdf_resume_returns_resume_id(self, client):
        pdf_bytes = make_pdf_bytes("Alice Developer at Acme")
        with patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT):
            response = await client.post(
                "/api/upload",
                files={"resume": ("resume.pdf", pdf_bytes, "application/pdf")},
            )
        assert response.status_code == 200
        data = response.json()
        assert "resume_id" in data
        assert isinstance(data["resume_id"], int)
        assert data["status"] == "parsed"

    async def test_upload_docx_resume_returns_resume_id(self, client):
        docx_bytes = make_docx_bytes("Bob Engineer at Tech Corp")
        with patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT):
            response = await client.post(
                "/api/upload",
                files={
                    "resume": (
                        "resume.docx",
                        docx_bytes,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
            )
        assert response.status_code == 200
        assert "resume_id" in response.json()

    async def test_upload_with_github_url(self, client):
        pdf_bytes = make_pdf_bytes("Charlie Hacker")
        with patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT_WITH_GITHUB):
            response = await client.post(
                "/api/upload",
                files={"resume": ("resume.pdf", pdf_bytes, "application/pdf")},
                data={"github_url": "https://github.com/charlie"},
            )
        assert response.status_code == 200
        resume_id = response.json()["resume_id"]
        # Fetch and verify github_url stored
        get_resp = await client.get(f"/api/resume/{resume_id}")
        assert get_resp.json()["github_url"] == "https://github.com/charlie"

    async def test_upload_with_paper_pdf(self, client):
        pdf_bytes = make_pdf_bytes("Diana Researcher")
        paper_bytes = make_pdf_bytes("Abstract: This paper presents a novel approach")
        with patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT_WITH_PAPER):
            response = await client.post(
                "/api/upload",
                files={
                    "resume": ("resume.pdf", pdf_bytes, "application/pdf"),
                    "paper": ("paper.pdf", paper_bytes, "application/pdf"),
                },
            )
        assert response.status_code == 200

    async def test_upload_invalid_file_type_returns_422(self, client):
        # Invalid file type is caught by parse_all (real call), which raises ValueError -> 422
        response = await client.post(
            "/api/upload",
            files={
                "resume": (
                    "malware.exe",
                    b"MZ\x90\x00" + b"\x00" * 100,
                    "application/octet-stream",
                )
            },
        )
        assert response.status_code == 422

    async def test_upload_stores_parsed_data(self, client):
        """Verify that parsed_data from Claude is stored in the DB (not empty dict)."""
        pdf_bytes = make_pdf_bytes("John Doe")
        with patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT):
            upload_resp = await client.post(
                "/api/upload",
                files={"resume": ("resume.pdf", pdf_bytes, "application/pdf")},
            )
        assert upload_resp.status_code == 200
        resume_id = upload_resp.json()["resume_id"]

        get_resp = await client.get(f"/api/resume/{resume_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["parsed_data"]["personal"]["name"] == "John Doe"

    async def test_upload_status_is_parsed(self, client):
        """Verify response status is 'parsed' (not 'extracted') after Claude runs."""
        pdf_bytes = make_pdf_bytes("Eve Status Test")
        with patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT):
            response = await client.post(
                "/api/upload",
                files={"resume": ("resume.pdf", pdf_bytes, "application/pdf")},
            )
        assert response.json()["status"] == "parsed"


class TestResumeRoutes:
    async def test_get_resume_not_found(self, client):
        response = await client.get("/api/resume/99999")
        assert response.status_code == 404

    async def test_get_resume_returns_data(self, client):
        pdf_bytes = make_pdf_bytes("Eve Engineer")
        with patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT):
            upload_resp = await client.post(
                "/api/upload",
                files={"resume": ("resume.pdf", pdf_bytes, "application/pdf")},
            )
        resume_id = upload_resp.json()["resume_id"]
        get_resp = await client.get(f"/api/resume/{resume_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == resume_id
