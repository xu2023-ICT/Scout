---
phase: 01-upload-parse
plan: 01
subsystem: api, database, ui
tags: [fastapi, sqlalchemy, pydantic, aiosqlite, alembic, vue3, vite, tailwind, pinia, typescript]

# Dependency graph
requires: []

provides:
  - FastAPI app entry point with CORS, file-size limit middleware, lifespan DB setup
  - Async SQLAlchemy 2.0 engine (aiosqlite) with Base, get_db dependency injection
  - Resume and Paper SQLAlchemy ORM models with JSON columns and one-to-one relationship
  - Pydantic v2 schemas: ParsedResume, PaperParsed, ResumeRead, ResumeUpdate
  - pytest-asyncio conftest with async db_session and HTTP client fixtures
  - Vue 3 + Vite + Tailwind v4 frontend scaffold
  - Pinia resume store with loadParsed, saveEdits, confirmResume, reset
  - TypeScript interfaces mirroring all backend Pydantic schemas
  - Vue Router with /  (UploadView) and /review/:id (ReviewView) routes
  - /api proxy from Vite dev server (5173) to FastAPI (8000)

affects:
  - 01-upload-parse (plans 02-05 all import from these foundations)

# Tech tracking
tech-stack:
  added:
    - FastAPI 0.135.x (ASGI web framework)
    - SQLAlchemy 2.x async (ORM with aiosqlite driver)
    - Alembic 1.x (database migrations, async pattern)
    - Pydantic v2 (request/response schemas)
    - pytest-asyncio (async test fixtures)
    - httpx + ASGITransport (test HTTP client)
    - Vue 3.5.x + Vite 8.x (frontend framework + build tool)
    - Tailwind CSS v4 with @tailwindcss/vite plugin
    - Pinia (Vue state management)
    - Vue Router 4.x (SPA routing)
    - vee-validate + @vee-validate/zod + zod (form validation)
    - class-variance-authority + clsx + tailwind-merge (shadcn-vue utilities)
    - radix-vue + lucide-vue-next (shadcn-vue component primitives)
  patterns:
    - FastAPI lifespan context manager for DB table creation on startup
    - Async SQLAlchemy 2.0 with async_sessionmaker and get_db generator
    - Pydantic v2 ConfigDict(from_attributes=True) for ORM-to-schema mapping
    - Alembic async migration via create_async_engine in env.py run_async_migrations
    - pytest-asyncio function-scoped fixtures with full DB teardown per test
    - Pinia setup stores (composition API style) with error handling pattern
    - Vite /api proxy for CORS-free local development

key-files:
  created:
    - scout-backend/app/main.py
    - scout-backend/app/database.py
    - scout-backend/app/models/resume.py
    - scout-backend/app/schemas/resume.py
    - scout-backend/app/routers/__init__.py
    - scout-backend/alembic.ini
    - scout-backend/alembic/env.py
    - scout-backend/tests/conftest.py
    - scout-backend/.env.example
    - scout-backend/pyproject.toml
    - scout-frontend/vite.config.ts
    - scout-frontend/src/stores/resume.ts
    - scout-frontend/src/types/resume.ts
    - scout-frontend/src/router/index.ts
    - scout-frontend/src/services/api.ts
    - scout-frontend/src/views/UploadView.vue
    - scout-frontend/src/views/ReviewView.vue
    - scout-frontend/src/lib/utils.ts
    - scout-frontend/components.json
  modified:
    - scout-frontend/src/App.vue (stripped to bare RouterView)
    - scout-frontend/src/assets/main.css (Tailwind v4 @import + @theme tokens)

key-decisions:
  - "Used Tailwind CSS v4 with @tailwindcss/vite plugin (not v3) — installed version was 4.x; adapted CSS variable syntax from @layer base to @theme block"
  - "shadcn-vue init skipped (interactive CLI fails non-interactively); peer deps installed manually + components.json created by hand"
  - "Tailwind CSS variables defined using @theme {} block (v4 syntax) instead of CSS custom properties in @layer base (v3 syntax)"
  - "FileSizeLimitMiddleware checks Content-Length header on all POST requests; rejects > 20MB with HTTP 413"
  - "Paper model has one-to-one relationship with Resume via back_populates for easy ORM joins in Plans 02-05"
  - "pytest uses function-scoped fixtures with full create_all/drop_all per test for clean isolation"

patterns-established:
  - "Pattern: FastAPI lifespan + Base.metadata.create_all for zero-config DB setup in development"
  - "Pattern: Alembic async env.py using run_async_migrations() for asyncio compatibility"
  - "Pattern: Pinia store error handling — isLoading/error refs updated in try/catch/finally"
  - "Pattern: Vue Router lazy-loads ReviewView to keep initial bundle small"

requirements-completed:
  - RESUME-01
  - RESUME-02
  - RESUME-03
  - RESUME-04
  - RESUME-05

# Metrics
duration: 14min
completed: 2026-04-10
---

# Phase 1 Plan 01: Full-Stack Scaffold Summary

**FastAPI async backend with SQLAlchemy 2.0/aiosqlite ORM models + Pydantic v2 schemas, paired with Vue 3 + Tailwind v4 + Pinia frontend scaffold — all foundations Plans 02-05 build on**

## Performance

- **Duration:** 14 min
- **Started:** 2026-04-10T06:56:32Z
- **Completed:** 2026-04-10T07:10:35Z
- **Tasks:** 2
- **Files created:** 29 (backend: 16, frontend: 19, minus scaffold removals)

## Accomplishments

- Backend: FastAPI app with CORS (localhost:5173 only), 20MB file-size limit middleware, lifespan DB auto-create — imports cleanly, pytest discovers conftest without errors
- Backend: SQLAlchemy 2.0 async models (Resume + Paper with JSON columns, FK relationship), Pydantic v2 schemas (ParsedResume, PaperParsed, ResumeRead, ResumeUpdate), async test fixtures
- Frontend: Vue 3 + Vite + Tailwind v4 build succeeds with zero TypeScript errors; Pinia store, typed interfaces, router, and /api proxy all in place

## Task Commits

1. **Task 1: Backend project structure, models, schemas, and test scaffold** - `c60568b` (feat)
2. **Task 2: Vue 3 frontend with shadcn-vue and Pinia router scaffold** - `ac72394` (feat)
3. **Cleanup: scaffold support files + .gitignore update** - `14450ec` (chore)

**Plan metadata:** (see docs commit below)

## Files Created/Modified

- `scout-backend/app/main.py` — FastAPI app with lifespan, CORS, FileSizeLimitMiddleware, /api router
- `scout-backend/app/database.py` — Async engine, AsyncSessionLocal, Base, get_db
- `scout-backend/app/models/resume.py` — Resume + Paper ORM models with JSON columns and relationship
- `scout-backend/app/schemas/resume.py` — All Pydantic v2 schemas (ParsedResume, PaperParsed, ResumeRead, ResumeUpdate)
- `scout-backend/app/routers/__init__.py` — Stub health-check router at /api/health
- `scout-backend/alembic.ini` + `alembic/env.py` — Async Alembic migration setup
- `scout-backend/tests/conftest.py` — db_session and client fixtures (function scope, full teardown)
- `scout-backend/.env.example` — Documents ANTHROPIC_API_KEY and DATABASE_URL
- `scout-frontend/vite.config.ts` — Tailwind plugin + /api proxy to localhost:8000
- `scout-frontend/src/stores/resume.ts` — Pinia store: loadParsed, saveEdits, confirmResume, reset
- `scout-frontend/src/types/resume.ts` — TypeScript interfaces matching all backend Pydantic schemas
- `scout-frontend/src/router/index.ts` — Routes: / (UploadView), /review/:id (ReviewView)
- `scout-frontend/src/services/api.ts` — fetch helpers: getResume, updateResume, confirmResume
- `scout-frontend/src/assets/main.css` — Tailwind v4 @import + @theme CSS variable tokens

## Decisions Made

- **Tailwind v4 syntax:** The installed Tailwind was v4 (not v3). Tailwind v4 removed `@layer base` for CSS variable theming — switched to `@theme {}` block syntax. The `border-border` utility class (v3 shadcn pattern) was dropped in favor of plain CSS on body.
- **shadcn-vue init skipped:** The interactive CLI cannot run non-interactively. Installed all peer deps manually (`class-variance-authority`, `clsx`, `tailwind-merge`, `radix-vue`, `lucide-vue-next`) and created `components.json` by hand. Plans 02-05 can use `npx shadcn-vue@latest add <component>` when the config file is present.
- **Paper relationship:** Added `relationship("Paper", back_populates="resume", uselist=False)` on Resume to enable ORM-level eager loading in Plan 03's GET endpoint.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Tailwind v4 @theme syntax instead of v3 @layer base**
- **Found during:** Task 2 (npm run build verification)
- **Issue:** Build failed with `Cannot apply unknown utility class border-border` — the v3 CSS variable pattern (`@layer base { * { @apply border-border; } }`) is not valid in Tailwind v4
- **Fix:** Rewrote `main.css` to use `@import "tailwindcss"` + `@theme {}` block with explicit HSL values; removed `@layer base` block with unknown utility
- **Files modified:** `scout-frontend/src/assets/main.css`
- **Verification:** `npm run build` exits 0 with zero errors
- **Committed in:** ac72394

**2. [Rule 3 - Blocking] shadcn-vue interactive init cannot run non-interactively**
- **Found during:** Task 2 (npx shadcn-vue@latest init)
- **Issue:** `npx shadcn-vue@latest init --yes --defaults` returned "No Tailwind CSS configuration found" and "No import alias found" errors — requires interactive terminal
- **Fix:** Manually installed all shadcn-vue peer dependencies and created `components.json` with correct config; Tailwind CSS installed separately via `@tailwindcss/vite` plugin
- **Files modified:** `scout-frontend/components.json`, `scout-frontend/package.json`
- **Verification:** Build succeeds; `npx shadcn-vue@latest add <component>` will work with the components.json present
- **Committed in:** ac72394

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both fixes necessary to get the build passing. The shadcn-vue workaround is transparent to Plans 02-05 which just call `npx shadcn-vue@latest add button card` etc.

## Issues Encountered

- pip install failed with `WinError 32` (file locked by another process) on the `anthropic` package — resolved by installing remaining deps first; anthropic was already installed globally
- `npm create vue@latest` does not support `--no-eslint` flag in v3.22.2; used `--typescript --router --pinia` only (ESLint was not selected interactively, it was skipped)

## User Setup Required

None — no external service configuration required for this scaffold plan. `ANTHROPIC_API_KEY` will be required starting Plan 02 when Claude parsing is implemented.

## Known Stubs

- `scout-frontend/src/views/UploadView.vue` — Stub placeholder; full implementation in Plan 04
- `scout-frontend/src/views/ReviewView.vue` — Stub placeholder; full implementation in Plan 05
- `scout-backend/app/routers/__init__.py` — Health-check only; upload router added in Plan 03

These stubs are intentional — this plan's goal is the scaffold foundation, not the feature implementation.

## Next Phase Readiness

- Ready for Plan 02: PDF/Word text extraction services (PyMuPDF, python-docx)
- All imports clean, DB engine verified, frontend build passes
- `ANTHROPIC_API_KEY` must be set in `.env` (copied from `.env.example`) before Plan 03 Claude parsing runs

---
*Phase: 01-upload-parse*
*Completed: 2026-04-10*

## Self-Check: PASSED

All key files found on disk. All three task commits (`c60568b`, `ac72394`, `14450ec`) exist in git log.
