---
phase: 01-upload-parse
plan: 03
subsystem: api, services
tags: [anthropic, claude-haiku-4-5, structured-outputs, json-schema, asyncio, pytest-mock]

# Dependency graph
requires:
  - 01-02-SUMMARY.md (parse_coordinator.parse_all returning resume_text/paper_text)

provides:
  - parse_resume_with_claude(markdown_text: str) -> dict: RESUME_SCHEMA-shaped dict via claude-haiku-4-5
  - parse_paper_with_claude(markdown_text: str) -> dict: PAPER_SCHEMA-shaped dict via claude-haiku-4-5
  - RESUME_SCHEMA: JSON schema for resume structured output (personal, education, work_experience, projects, skills)
  - PAPER_SCHEMA: JSON schema for paper structured output (title, authors, abstract, key_contributions, ...)
  - POST /api/upload now returns {"resume_id": int, "status": "parsed"} (Claude has run)
  - Resume.parsed_data now populated with RESUME_SCHEMA-shaped dict (not empty {})
  - Paper.parsed_data now populated with PAPER_SCHEMA-shaped dict

affects:
  - 01-upload-parse (plan 04+ frontend can now read structured parsed_data from GET /api/resume/{id})

# Tech tracking
tech-stack:
  added:
    - anthropic 0.93.x: Claude Haiku 4.5 structured output parsing via output_config.format
  patterns:
    - output_config.format json_schema mode: constrained decoding guarantees schema-valid JSON (no retries)
    - asyncio.gather for concurrent Claude calls: resume + paper parsed simultaneously per D-03
    - Lazy client initialization: get_client() returns cached _client, raises RuntimeError if API key missing
    - unittest.mock AsyncMock patch on parse_all: all tests avoid real API calls

key-files:
  created:
    - scout-backend/app/services/claude_parser.py
    - scout-backend/tests/test_claude_parser.py
  modified:
    - scout-backend/app/services/parse_coordinator.py
    - scout-backend/app/routers/upload.py
    - scout-backend/tests/test_upload_route.py
    - scout-backend/tests/test_resume_route.py

key-decisions:
  - "output_config.format json_schema with additionalProperties: False provides constrained decoding — Claude cannot produce JSON outside schema; eliminates 5% failure rate of prompt-only JSON extraction"
  - "claude-haiku-4-5 selected over claude-sonnet-4-5 for cost control (~$0.011 vs ~$0.033 per resume parse per RESEARCH.md cost estimates)"
  - "max_tokens=4096 for resume, 2048 for paper — prevents Pitfall 4 truncation on long CVs"
  - "Lazy _client singleton initialized on first call, not at import time — tests can patch get_client() without setting real ANTHROPIC_API_KEY"
  - "AsyncMock patch on app.routers.upload.parse_all rather than claude_parser directly — decouples upload tests from internal parsing implementation"
  - "test_upload_invalid_file_type_returns_422 kept as real call (no mock) — validate_file_type raises before Claude is ever called, testing the guard"

requirements-completed:
  - RESUME-02
  - RESUME-05

# Metrics
duration: 15min
completed: 2026-04-10
---

# Phase 1 Plan 03: Claude AI Parser for Resume and Paper Summary

**Claude Haiku 4.5 structured output parsing integrated into upload pipeline — RESUME_SCHEMA and PAPER_SCHEMA with json_schema constrained decoding; asyncio.gather concurrent parsing; 24/24 tests passing with zero real API calls**

## Performance

- **Duration:** 15 min
- **Completed:** 2026-04-10
- **Tasks:** 2
- **Files created:** 2 new, 4 modified

## Accomplishments

- **Task 1 (TDD):** `claude_parser.py` implemented with `parse_resume_with_claude` and `parse_paper_with_claude`. Both use `output_config.format` JSON schema mode (constrained decoding per RESEARCH.md "Don't Hand-Roll" table). Lazy `get_client()` singleton raises `RuntimeError` if `ANTHROPIC_API_KEY` is missing. 7 unit tests with mocked Anthropic client — zero real API calls during tests.
- **Task 2:** `parse_coordinator.parse_all` updated to run Claude parsing after text extraction, using `asyncio.gather(claude_resume(), claude_paper())` for concurrent calls per D-03. `upload.py` updated to store `result["parsed_resume"]` and `result["parsed_paper"]` in DB. Response status changed from `"extracted"` to `"parsed"`. All test files updated with `AsyncMock` patch on `parse_all`. Added `test_upload_stores_parsed_data` and `test_upload_status_is_parsed`.

## Task Commits

1. **Task 1: Claude parser service with mocked tests** — `8a8f6e0` (feat)
2. **Task 2: Wire Claude parsing into upload pipeline** — `d680d81` (feat)

## Schemas Documented

### RESUME_SCHEMA (top-level required fields)
```json
{
  "required": ["personal", "education", "work_experience", "skills"],
  "additionalProperties": false
}
```
`personal` requires `name`; `education` items require `institution`, `degree`; `work_experience` items require `company`, `title`.

### PAPER_SCHEMA (top-level required fields)
```json
{
  "required": ["title", "authors", "abstract", "key_contributions"],
  "additionalProperties": false
}
```
`key_contributions` is an array of strings (3-5 novel contribution bullet points).

## asyncio.gather Concurrent Parsing Pattern

```python
parsed_resume, parsed_paper = await asyncio.gather(
    claude_resume(), claude_paper(), return_exceptions=True
)
if isinstance(parsed_resume, Exception):
    raise parsed_resume
```

Resume and paper are parsed concurrently per D-03. If either raises (e.g., `AuthenticationError`), it is re-raised after gather and converted to HTTP 422 by the route handler.

## Mock Strategy (No Real API Calls)

- **claude_parser tests:** `patch("app.services.claude_parser.get_client")` returns a `MagicMock` whose `.messages.create()` returns a mock response with serialized JSON.
- **upload/resume route tests:** `patch("app.routers.upload.parse_all", new_callable=AsyncMock, return_value=MOCK_PARSE_RESULT)` bypasses the entire parsing pipeline — tests focus on DB storage and HTTP behavior.
- `test_upload_invalid_file_type_returns_422` is the only test without a mock — `validate_file_type` raises `ValueError` before Claude is ever called, so no API key is needed.

## Status Field Change

| Before (Plan 02) | After (Plan 03) |
|------------------|-----------------|
| `{"status": "extracted"}` | `{"status": "parsed"}` |
| `parsed_data = {}` | `parsed_data = {RESUME_SCHEMA shape}` |
| `paper.parsed_data = {"raw_text": ...}` | `paper.parsed_data = {PAPER_SCHEMA shape}` |

## Test Coverage

| Test File | Tests | What Verified |
|-----------|-------|---------------|
| test_claude_parser.py | 7 | Schema structure, model=claude-haiku-4-5, max_tokens=4096, return shape |
| test_upload_route.py | 9 | status="parsed", parsed_data stored, mocked pipeline |
| test_resume_route.py | 2 | PUT/confirm with mocked upload |
| test_pdf_parser.py | 4 | Unchanged (existing) |
| test_docx_parser.py | 2 | Unchanged (existing) |
| **Total** | **24** | All passing |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] test_resume_route.py needed AsyncMock patch after parse_coordinator change**
- **Found during:** Task 2 (first test run)
- **Issue:** `test_resume_route.py` calls `/api/upload` which now invokes `parse_all` → `parse_resume_with_claude` → `get_client()` → fails with `RuntimeError: ANTHROPIC_API_KEY not set` in test environment.
- **Fix:** Added `MOCK_PARSE_RESULT` and `MOCK_PARSE_RESULT_GRACE` fixtures to `test_resume_route.py`; wrapped upload calls with `patch("app.routers.upload.parse_all", new_callable=AsyncMock)`.
- **Files modified:** `tests/test_resume_route.py`
- **Verification:** 24/24 tests pass
- **Commit:** d680d81

---

**Total deviations:** 1 auto-fixed (missing mock in test_resume_route.py)
**Impact:** No production code changed. Test files updated to be consistent with new pipeline behavior.

## Known Stubs

None — `Resume.parsed_data` is now fully populated with Claude's structured output. The stub from Plan 02 is resolved.

## Threat Surface Scan

Threat mitigations from plan's threat model implemented:

| Threat ID | Mitigation Status |
|-----------|-------------------|
| T-03-02: Claude response tampering | Implemented — `output_config.format.json_schema` constrained decoding; no code execution path |
| T-03-03: ANTHROPIC_API_KEY disclosure | Implemented — key read from env var only; .env in .gitignore from Plan 01 |
| T-03-06: Prompt injection via resume | Implemented — structured outputs use constrained decoding; schema-locked response |

## Next Phase Readiness

- Ready for Plan 04: SSE streaming frontend — `GET /api/resume/{id}` returns fully populated `parsed_data` with `personal.name`, `education`, `work_experience`, `projects`, `skills`
- All 24 tests green; no real API key required for test suite

---
*Phase: 01-upload-parse*
*Completed: 2026-04-10*

## Self-Check

Verifying key files exist on disk:
- scout-backend/app/services/claude_parser.py: EXISTS
- scout-backend/tests/test_claude_parser.py: EXISTS
- scout-backend/app/services/parse_coordinator.py: EXISTS (modified)
- scout-backend/app/routers/upload.py: EXISTS (modified)

Commits verified: 8a8f6e0 (Task 1), d680d81 (Task 2)

## Self-Check: PASSED
