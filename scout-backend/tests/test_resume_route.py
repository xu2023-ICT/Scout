import fitz
import pytest
from unittest.mock import AsyncMock, patch


def make_pdf_bytes(text="Frank Developer") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    # Insert enough text to exceed the 100-char scanned-PDF detection threshold
    full_text = text + "\nSoftware Engineer | frank@example.com | github.com/frank\nExperience: 5 years Python, FastAPI, SQLAlchemy, Docker, AWS"
    page.insert_text((50, 50), full_text, fontsize=12)
    return doc.tobytes()


SAMPLE_PARSED = {
    "personal": {
        "name": "Frank Developer",
        "email": "frank@example.com",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "website": "",
        "summary": "",
    },
    "education": [],
    "work_experience": [],
    "projects": [],
    "skills": {"languages": [], "frameworks": [], "tools": [], "other": []},
}

MOCK_PARSE_RESULT = {
    "resume_text": "Frank Developer Software Engineer",
    "paper_text": None,
    "parsed_resume": SAMPLE_PARSED,
    "parsed_paper": None,
    "github_url": None,
}

MOCK_PARSE_RESULT_GRACE = {
    "resume_text": "Grace Researcher Software Engineer",
    "paper_text": None,
    "parsed_resume": {
        "personal": {"name": "Grace Researcher", "email": "", "phone": "",
                     "location": "", "linkedin": "", "github": "", "website": "", "summary": ""},
        "education": [], "work_experience": [], "projects": [],
        "skills": {"languages": [], "frameworks": [], "tools": [], "other": []}
    },
    "parsed_paper": None,
    "github_url": None,
}


class TestResumeEdit:
    async def test_put_updates_parsed_data(self, client):
        pdf_bytes = make_pdf_bytes("Frank Developer")
        with patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT):
            upload_resp = await client.post(
                "/api/upload",
                files={"resume": ("resume.pdf", pdf_bytes, "application/pdf")},
            )
        resume_id = upload_resp.json()["resume_id"]

        put_resp = await client.put(
            f"/api/resume/{resume_id}",
            json={"parsed_data": SAMPLE_PARSED, "github_url": None},
        )
        assert put_resp.status_code == 200
        assert put_resp.json()["status"] == "updated"

    async def test_confirm_sets_confirmed_true(self, client):
        pdf_bytes = make_pdf_bytes("Grace Researcher")
        with patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT_GRACE):
            upload_resp = await client.post(
                "/api/upload",
                files={"resume": ("resume.pdf", pdf_bytes, "application/pdf")},
            )
        resume_id = upload_resp.json()["resume_id"]

        confirm_resp = await client.post(f"/api/resume/{resume_id}/confirm")
        assert confirm_resp.status_code == 200
        assert confirm_resp.json()["status"] == "confirmed"

        get_resp = await client.get(f"/api/resume/{resume_id}")
        assert get_resp.json()["confirmed"] is True
