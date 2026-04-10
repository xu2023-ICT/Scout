---
phase: 1
slug: upload-parse
status: complete
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio + httpx (AsyncClient) |
| **Config file** | `pyproject.toml` — none yet; Wave 0 creates it |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v --tb=short`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-T1 | 01 | 1 | RESUME-01 | T-01-01 | File type validated server-side | unit | `pytest tests/conftest.py -x -q` | ❌ W0 | ⬜ pending |
| 01-02-T1 | 02 | 2 | RESUME-01 | T-01-01 | Only PDF/DOCX accepted; size ≤10MB enforced | unit | `pytest tests/test_pdf_parser.py tests/test_docx_parser.py -x -q` | ❌ W0 | ⬜ pending |
| 01-02-T2 | 02 | 2 | RESUME-04 | T-01-02 | Paper PDF and GitHub URL stored correctly | integration | `pytest tests/test_upload_route.py -x -q` | ❌ W0 | ⬜ pending |
| 01-03-T1 | 03 | 3 | RESUME-02, RESUME-05 | — | Claude mock returns valid schema; no real API calls in CI | unit (mock) | `pytest tests/test_claude_parser.py -x -q` | ❌ W0 | ⬜ pending |
| 01-03-T2 | 03 | 3 | RESUME-03 | — | PUT /resume/{id} updates DB; POST /confirm sets confirmed=True | integration | `pytest tests/test_resume_route.py -x -q` | ❌ W0 | ⬜ pending |
| 01-04-T1 | 04 | 2 | RESUME-01 | T-01-01 | Frontend validates file type before upload | manual | Open browser, try uploading .exe — should be rejected | N/A | ✅ green |
| 01-04-T2 | 04 | 2 | RESUME-01 | — | SSE progress events received during parse | manual | Upload valid PDF, check DevTools > Network > SSE stream | N/A | ✅ green |
| 01-05-T1 | 05 | 4 | RESUME-02, RESUME-03, RESUME-05 | — | Form displays all sections; save updates server | manual | E2E: upload → parse → review form → edit → confirm | N/A | ✅ green |
| 01-05-T2 | 05 | 4 | RESUME-03 | — | No add/delete entry buttons visible (D-07) | manual | Inspect form — no + / trash buttons on work/education/project sections | N/A | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pyproject.toml` — pytest config with `asyncio_mode = "auto"`
- [ ] `tests/conftest.py` — async DB session fixture with rollback isolation
- [ ] `tests/fixtures/sample_resume.pdf` — minimal text-based PDF for tests
- [ ] `tests/fixtures/sample_resume.docx` — minimal Word doc for tests
- [ ] `tests/fixtures/sample_paper.pdf` — academic paper first page (abstract + authors)
- [ ] `tests/test_pdf_parser.py` — stubs for RESUME-01 (PDF path)
- [ ] `tests/test_docx_parser.py` — stubs for RESUME-01 (Word path)
- [ ] `tests/test_claude_parser.py` — stubs for RESUME-02, RESUME-05 (Claude API mocked)
- [ ] `tests/test_upload_route.py` — stubs for RESUME-01, RESUME-04
- [ ] `tests/test_resume_route.py` — stubs for RESUME-03

Framework install (Wave 0): `pip install pytest pytest-asyncio httpx aiosqlite`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Upload page drag-drop works | RESUME-01 | Browser interaction | Drag a PDF onto the upload zone; confirm file name appears |
| SSE progress shown during parse | RESUME-01 | Real-time streaming | Upload valid PDF; confirm step labels appear sequentially |
| Form fields editable | RESUME-03 | DOM interaction | Click each field; confirm it becomes an editable input |
| No add/delete buttons | RESUME-03 (D-07) | Visual inspection | Confirm no + or trash icons on work/education/project entries |
| Confirm button triggers save | RESUME-03 | Integration E2E | Click Confirm; verify redirect and server DB updated |
| GitHub link shown read-only | RESUME-04 | Visual inspection | Submit with GitHub URL; confirm it appears in Personal Info as non-editable text |
| Paper metadata displayed | RESUME-05 | Visual inspection | Upload paper PDF; confirm title, authors, key contributions shown in Paper section |
