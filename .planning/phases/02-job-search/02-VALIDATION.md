---
phase: 2
slug: job-search
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio |
| **Config file** | `scout-backend/pyproject.toml` (`asyncio_mode = "auto"`) |
| **Quick run command** | `cd scout-backend && pytest tests/test_search_route.py -x` |
| **Full suite command** | `cd scout-backend && pytest tests/ -x` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd scout-backend && pytest tests/test_search_route.py -x`
- **After every plan wave:** Run `cd scout-backend && pytest tests/ -x`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | SCRAPE-02 | — | N/A | unit | `pytest tests/test_tavily_service.py -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 0 | SCRAPE-02 | — | N/A | integration | `pytest tests/test_search_route.py -x` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 0 | SCRAPE-03 | — | N/A | unit | `pytest tests/test_tavily_service.py::test_query_construction -x` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 0 | SCRAPE-04 | — | N/A | integration | `pytest tests/test_search_route.py::test_company_failure -x` | ❌ W0 | ⬜ pending |
| 02-01-05 | 01 | 0 | JOBS-01 | — | N/A | integration | `pytest tests/test_jobs_route.py -x` | ❌ W0 | ⬜ pending |
| 02-01-06 | 01 | 0 | JOBS-01 | — | N/A | integration | `pytest tests/test_jobs_route.py::test_manual_job -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_tavily_service.py` — unit tests for query construction and mock Tavily responses (SCRAPE-02, SCRAPE-03)
- [ ] `tests/test_search_route.py` — SSE endpoint integration tests, company failure path (SCRAPE-02, SCRAPE-04)
- [ ] `tests/test_jobs_route.py` — CRUD tests for jobs router, manual JD entry (JOBS-01)
- [ ] `tests/fixtures/mock_tavily.py` — shared mock for AsyncTavilyClient

*Existing `conftest.py` already provides `client` and `db_session` fixtures — reuse directly.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SSE real-time progress per company visible in browser | SCRAPE-02 | Browser streaming behavior cannot be replicated in pytest | Start backend, open /search, submit preferences, watch each company row update live |
| Auto-redirect to /dashboard after all companies complete | D-10 | Vue Router navigation is browser-only | Complete above test; confirm redirect fires |
| 「粘贴 JD」modal opens on failed company row click | SCRAPE-04 | Browser UI interaction | Simulate a Tavily failure (bad domain), click fallback button, confirm modal appears |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
