from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.resume import Paper, Resume
from app.schemas.resume import ParsedResume, ResumeUpdate
from app.services.parse_coordinator import parse_all

router = APIRouter(tags=["upload"])


@router.post("/upload")
async def upload_resume(
    resume: UploadFile = File(..., description="PDF or Word resume (required)"),
    paper: UploadFile | None = File(None, description="Academic paper PDF (optional)"),
    github_url: str | None = Form(None, description="GitHub profile URL (optional)"),
    db: AsyncSession = Depends(get_db),
):
    # CRITICAL: Read ALL bytes BEFORE any await that could close the file (RESEARCH.md Pitfall 1)
    resume_bytes = await resume.read()
    paper_bytes = await paper.read() if paper else None

    try:
        result = await parse_all(
            resume_bytes=resume_bytes,
            resume_filename=resume.filename or "resume",
            paper_bytes=paper_bytes,
            github_url=github_url,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Save resume row (parsed_data is {} until Plan 03 Claude parsing)
    resume_row = Resume(
        filename=resume.filename or "resume",
        raw_text=result["resume_text"],
        parsed_data={},
        github_url=result["github_url"],
        confirmed=False,
    )
    db.add(resume_row)
    await db.flush()  # get resume_row.id before committing

    # Save paper row if paper was uploaded
    if result["paper_text"] and paper:
        paper_row = Paper(
            resume_id=resume_row.id,
            filename=paper.filename or "paper.pdf",
            parsed_data={"raw_text": result["paper_text"]},  # Claude fills this in Plan 03
        )
        db.add(paper_row)

    await db.commit()
    await db.refresh(resume_row)

    return {"resume_id": resume_row.id, "status": "extracted"}


@router.get("/resume/{resume_id}", response_model=dict)
async def get_resume(resume_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")

    # Fetch associated paper if any
    paper_result = await db.execute(select(Paper).where(Paper.resume_id == resume_id))
    paper = paper_result.scalar_one_or_none()

    return {
        "id": resume.id,
        "filename": resume.filename,
        "parsed_data": resume.parsed_data,
        "github_url": resume.github_url,
        "confirmed": resume.confirmed,
        "created_at": resume.created_at.isoformat(),
        "paper": paper.parsed_data if paper else None,
    }


@router.put("/resume/{resume_id}")
async def update_resume(
    resume_id: int,
    update: ResumeUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")

    resume.parsed_data = update.parsed_data.model_dump()
    if update.github_url is not None:
        resume.github_url = update.github_url
    await db.commit()
    return {"status": "updated"}


@router.post("/resume/{resume_id}/confirm")
async def confirm_resume(resume_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")
    resume.confirmed = True
    await db.commit()
    return {"status": "confirmed", "resume_id": resume_id}
