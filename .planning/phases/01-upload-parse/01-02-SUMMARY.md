---
phase: 01-upload-parse
plan: 02
subsystem: api, services
tags: [fastapi, pymupdf, pymupdf4llm, python-docx, asyncio, sqlalchemy, pytest]

# Dependency graph
requires:
  - 01-01-SUMMARY.md (FastAPI app, DB models, schemas, conftest fixtures)

provides:
  - POST /api/upload: multipart file upload accepting PDF/DOCX resume + optional paper PDF + github_url form field
  - GET /api/resume/{id}: fetch stored resume data (parsed_data, github_url, confirmed, paper)
  - PUT /api/resume/{id}: update parsed_data with ResumeUpdate schema
  - POST /api/resume/{id}/confirm: mark resume confirmed=True
  - extract_pdf_text(pdf_bytes) -> str: LLM-ready markdown via pymupdf4llm; raises ValueError for scanned PDFs
  - extract_paper_front_matter(pdf_bytes, max_pages=4) -> str: first N pages only
  - extract_docx_text(docx_bytes) -> str: body + headers + table cells
  - validate_file_type(filename, file_bytes) -> str: magic-byte validation returning 'pdf' or 'docx'
  - parse_all(resume_bytes, resume_filename, paper_bytes, github_url) -> dict: parallel asyncio.gather orchestration

affects:
  - 01-upload-parse (plan 03 calls parse_coordinator.parse_all and adds Claude parsing on top)

# Tech tracking
tech-stack:
  added:
    - PyMuPDF (fitz) 1.25.x: PDF text extraction via fitz.open(stream=bytes)
    - pymupdf4llm 0.0.x: convert PDF pages to LLM-ready markdown
    - python-docx 1.1.x: Word .docx parsing (paragraphs, headers, tables)
  patterns:
    - UploadFile bytes read in route handler before any await (prevents FastAPI UploadFile closure bug)
    - Magic-byte file validation (not Content-Type or extension) for spoofing resistance
    - asyncio.gather with return_exceptions=True for parallel resume+paper extraction
    - Scanned PDF detection: total_chars < 100 threshold; OCR attempted via pymupdf4llm use_ocr=True; ValueError raised if result < 50 chars
    - python-docx header extraction via doc.sections[n].header.paragraphs (contact info pitfall avoided)
    - FastAPI 422 returned for ValueError from services (invalid file type, scanned PDF)

key-files:
  created:
    - scout-backend/app/services/__init__.py
    - scout-backend/app/services/pdf_parser.py
    - scout-backend/app/services/docx_parser.py
    - scout-backend/app/services/parse_coordinator.py
    - scout-backend/app/routers/upload.py
    - scout-backend/tests/test_pdf_parser.py
    - scout-backend/tests/test_docx_parser.py
    - scout-backend/tests/test_upload_route.py
    - scout-backend/tests/test_resume_route.py
  modified:
    - scout-backend/app/routers/__init__.py (added upload_router include)
    - .gitignore (added *.db pattern)

key-decisions:
  - "Magic-byte validation (not Content-Type/extension) implements T-02-01 threat mitigation — DOCX identified by PK\\x03\\x04 ZIP magic, PDF by %PDF"
  - "Scanned PDF threshold set at total_chars < 100 with OCR fallback; if OCR markdown < 50 chars after strip, raise ValueError rather than pass empty text to Claude"
  - "parse_coordinator uses asyncio.gather(return_exceptions=True) so resume and paper extraction run concurrently; exceptions re-raised after gather completes"
  - "Test helper PDFs include enough text (>100 chars) to exceed scanned-PDF detection threshold — short fitz-generated PDFs with <100 chars would falsely trigger scanned detection"
  - "parsed_data stored as {} at upload time; Plan 03 (Claude parsing) will populate the field"

requirements-completed:
  - RESUME-01
  - RESUME-04

# Metrics
duration: 18min
completed: 2026-04-10
---

# Phase 1 Plan 02: Upload API and File Parsing Services Summary

**POST /api/upload accepts PDF/DOCX resume + optional paper PDF, validates by magic bytes, extracts text with PyMuPDF/python-docx in parallel via asyncio.gather, saves Resume row to SQLite, returns resume_id — all 15 pytest tests passing**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-10T07:15:00Z
- **Completed:** 2026-04-10T07:33:00Z
- **Tasks:** 2
- **Files created:** 9 new, 2 modified

## Accomplishments

- **Task 1:** PDF and Word text extractors implemented with TDD. `extract_pdf_text` uses pymupdf4llm for LLM-ready markdown, detects scanned PDFs (< 100 chars) and raises clear ValueError. `extract_docx_text` covers body paragraphs + section headers + table cells (avoids python-docx pitfall 3). `validate_file_type` checks magic bytes. 6 unit tests passing.
- **Task 2:** Upload route + parse_coordinator + integration tests. `POST /api/upload` reads all file bytes before any await (UploadFile closure bug prevention), validates file type, runs parallel extraction via asyncio.gather, saves Resume (+ optional Paper) to DB. All four endpoints functional. 9 integration tests passing.
- **Full suite:** 15/15 tests passing (`pytest tests/ -x -q`)

## Task Commits

1. **Task 1: PDF and Word text extraction services** - `298ecdd` (feat)
2. **Task 2: Upload route, parse_coordinator, integration tests** - `4f087fe` (feat)

## Endpoints Created

| Method | Path | Behavior |
|--------|------|----------|
| POST | `/api/upload` | Accepts resume (PDF/DOCX required) + paper PDF (optional) + github_url (optional form field). Validates magic bytes. Returns `{"resume_id": int, "status": "extracted"}` |
| GET | `/api/resume/{id}` | Returns resume data including parsed_data, github_url, confirmed, created_at, paper |
| PUT | `/api/resume/{id}` | Updates parsed_data via ResumeUpdate (ParsedResume schema validated) |
| POST | `/api/resume/{id}/confirm` | Sets Resume.confirmed = True |

## File Validation Approach

- **Magic bytes only** — not Content-Type header or filename extension
- PDF: first 4 bytes = `%PDF`
- DOCX: first 4 bytes = `PK\x03\x04` (ZIP container)
- Any other magic bytes → HTTP 422 with "Unsupported file type" message
- Implements T-02-01 (Spoofing) threat mitigation from plan's threat model

## asyncio.gather Parallel Extraction Pattern

```python
resume_text, paper_text = await asyncio.gather(
    extract_resume(), extract_paper(), return_exceptions=True
)
if isinstance(resume_text, Exception):
    raise resume_text
```

Resume and paper PDFs are extracted concurrently. If either raises ValueError, it is re-raised after gather completes and converted to HTTP 422 by the route handler.

## Test Coverage

| Test File | Requirements Covered | Tests |
|-----------|---------------------|-------|
| test_pdf_parser.py | RESUME-01 (PDF path), T-02-01 (magic bytes), Pitfall 2 (scanned PDF) | 4 |
| test_docx_parser.py | RESUME-01 (Word path), Pitfall 3 (headers + tables) | 2 |
| test_upload_route.py | RESUME-01 (PDF+DOCX upload), RESUME-04 (paper+github_url), T-02-01 (invalid type 422) | 7 |
| test_resume_route.py | RESUME-03 (PUT edit, confirm) | 2 |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test PDF helper generated text too short for scanned-PDF detection threshold**
- **Found during:** Task 2 (first GREEN phase run)
- **Issue:** `make_pdf_bytes()` in test helpers used `fitz.open().insert_text()` with short text (< 100 chars), which triggered the scanned-PDF detection threshold (`total_chars < 100`). The blank-page OCR path then returned < 50 chars, raising ValueError and causing all upload tests to return 422 instead of 200.
- **Fix:** Updated `make_pdf_bytes()` in `test_upload_route.py` and `test_resume_route.py` to append a longer suffix so the inserted text exceeds 100 chars. The scanned-PDF test in `test_pdf_parser.py` uses a blank page (0 chars) which still correctly triggers the detection.
- **Files modified:** `tests/test_upload_route.py`, `tests/test_resume_route.py`
- **Verification:** All 15 tests pass; `test_raises_for_scanned_pdf` continues to pass with blank-page fixture
- **Commit:** 4f087fe

---

**Total deviations:** 1 auto-fixed (bug in test helper)
**Impact:** No production code changed. Test helpers adjusted to reflect real-world usage (actual resumes always have > 100 extractable chars).

## Known Stubs

- `Resume.parsed_data` stored as `{}` at upload time — Plan 03 (Claude parsing) populates this field with structured resume data. The GET /api/resume/{id} endpoint returns the empty dict until Plan 03 runs.

This stub is intentional — Plan 02's goal is extraction only; Claude parsing is Plan 03.

## Threat Surface Scan

All security mitigations from the plan's threat model are implemented:

| Threat | Mitigation Status |
|--------|-------------------|
| T-02-01: Content-Type spoofing | Implemented — validate_file_type checks magic bytes |
| T-02-02: Filename path traversal | Not applicable — filename stored as string only, never passed to os.path |
| T-02-03: Oversized file DoS | Already in place — FileSizeLimitMiddleware from Plan 01 |
| T-02-06: PUT accepts arbitrary parsed_data | Implemented — ResumeUpdate uses ParsedResume Pydantic model with type validation |

## Next Phase Readiness

- Ready for Plan 03: Claude parsing — `parse_coordinator.parse_all` already returns `resume_text` and `paper_text`; Plan 03 adds `claude_parser.parse_resume_with_claude(resume_text)` and saves structured data to `Resume.parsed_data`
- All 15 tests green; conftest fixtures reused without modification

---
*Phase: 01-upload-parse*
*Completed: 2026-04-10*

## Self-Check

Verifying key files exist on disk:
- scout-backend/app/services/pdf_parser.py: EXISTS
- scout-backend/app/services/docx_parser.py: EXISTS
- scout-backend/app/services/parse_coordinator.py: EXISTS
- scout-backend/app/routers/upload.py: EXISTS
- scout-backend/tests/test_upload_route.py: EXISTS
- scout-backend/tests/test_resume_route.py: EXISTS

Commits verified: 298ecdd (Task 1), 4f087fe (Task 2)

## Self-Check: PASSED
