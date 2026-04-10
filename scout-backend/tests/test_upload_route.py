import io

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


class TestUploadEndpoint:
    async def test_upload_pdf_resume_returns_resume_id(self, client):
        pdf_bytes = make_pdf_bytes("Alice Developer at Acme")
        response = await client.post(
            "/api/upload",
            files={"resume": ("resume.pdf", pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "resume_id" in data
        assert isinstance(data["resume_id"], int)
        assert data["status"] == "extracted"

    async def test_upload_docx_resume_returns_resume_id(self, client):
        docx_bytes = make_docx_bytes("Bob Engineer at Tech Corp")
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
        response = await client.post(
            "/api/upload",
            files={
                "resume": ("resume.pdf", pdf_bytes, "application/pdf"),
                "paper": ("paper.pdf", paper_bytes, "application/pdf"),
            },
        )
        assert response.status_code == 200

    async def test_upload_invalid_file_type_returns_422(self, client):
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


class TestResumeRoutes:
    async def test_get_resume_not_found(self, client):
        response = await client.get("/api/resume/99999")
        assert response.status_code == 404

    async def test_get_resume_returns_data(self, client):
        pdf_bytes = make_pdf_bytes("Eve Engineer")
        upload_resp = await client.post(
            "/api/upload",
            files={"resume": ("resume.pdf", pdf_bytes, "application/pdf")},
        )
        resume_id = upload_resp.json()["resume_id"]
        get_resp = await client.get(f"/api/resume/{resume_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == resume_id
