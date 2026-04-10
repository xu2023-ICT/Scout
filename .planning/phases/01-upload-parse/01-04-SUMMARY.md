---
phase: 01-upload-parse
plan: "04"
subsystem: frontend-upload
tags: [vue3, upload, drag-drop, sse, progress]
requires:
  - 01-01-SUMMARY.md  # Vue 3 frontend scaffold
provides:
  - UploadView (drag-drop upload page with SSE progress)
  - UploadZone component (resume + paper + GitHub URL inputs)
  - ParseProgress component (step-by-step SSE progress display)
  - uploadWithProgress() API service with SSE + simulated-progress fallback
affects:
  - scout-frontend/src/views/UploadView.vue
  - scout-frontend/src/services/api.ts
tech-stack:
  added:
    - shadcn-vue UI primitives (Badge, Button, Input, Label, Card) — hand-crafted since shadcn-vue CLI schema changed in v2.5.3
  patterns:
    - SSE via fetch + ReadableStream (not EventSource — supports POST with body)
    - Simulated progress fallback when /upload/stream endpoint not yet available
    - Emit-based component communication: UploadZone emits progress/complete/error to UploadView
key-files:
  created:
    - scout-frontend/src/components/UploadZone.vue
    - scout-frontend/src/components/ParseProgress.vue
    - scout-frontend/src/components/ui/badge/Badge.vue
    - scout-frontend/src/components/ui/badge/index.ts
    - scout-frontend/src/components/ui/button/Button.vue
    - scout-frontend/src/components/ui/button/index.ts
    - scout-frontend/src/components/ui/input/Input.vue
    - scout-frontend/src/components/ui/input/index.ts
    - scout-frontend/src/components/ui/label/Label.vue
    - scout-frontend/src/components/ui/label/index.ts
    - scout-frontend/src/components/ui/card/Card.vue
    - scout-frontend/src/components/ui/card/index.ts
  modified:
    - scout-frontend/src/views/UploadView.vue (stub → full implementation)
    - scout-frontend/src/services/api.ts (added uploadWithProgress + SSE logic)
    - scout-frontend/src/assets/main.css (added --color-destructive-foreground)
    - scout-frontend/components.json (removed invalid 'framework' key)
key-decisions:
  - "SSE via fetch+ReadableStream (not EventSource): POST requests with body aren't supported by EventSource API"
  - "Simulated progress fallback: frontend works independently of backend plan 02 SSE endpoint"
  - "Hand-crafted shadcn-vue primitives: shadcn-vue CLI v2.5.3 changed schema and rejected components.json; manual creation is equivalent and avoids re-init"
requirements-completed:
  - RESUME-01
  - RESUME-04
duration: "~20 min"
completed: "2026-04-10"
---

# Phase 1 Plan 04: Frontend Upload View Summary

Upload page frontend complete — drag-and-drop resume upload with SSE-streamed parsing progress and auto-redirect to /review/{id} on completion.

## What Was Built

### UploadZone component (`scout-frontend/src/components/UploadZone.vue`)

Prop/emit contract:
- **Emits:** `progress(UploadProgressEvent)`, `complete(resumeId: number)`, `error(message: string)`
- **No props** — self-contained upload form

Features:
- Drag-and-drop zone for resume (D-01): `@dragover.prevent`, `@dragleave.prevent`, `@drop.prevent`
- Resume required (PDF/.docx), paper PDF optional, GitHub URL optional (D-02)
- All three inputs on one page, submitted together as a single FormData (D-03)
- Client-side file type validation (PDF/DOCX only, 20 MB max) — shows inline error before submission
- Submit button disabled when no resume selected

### ParseProgress component (`scout-frontend/src/components/ParseProgress.vue`)

Prop/emit contract:
- **Props:** `currentEvent: UploadProgressEvent | null`, `errorMessage: string`, `hasPaper: boolean`
- **Emits:** `retry()`

Features:
- Animated progress bar (`width: pct%` with CSS transition)
- Step labels: Extracting text → Parsing resume → Parsing paper (if `hasPaper`) → Saving → Complete
- Active step highlighted in primary color, completed steps dimmed
- Error state shows error message + "Try Again" button

### UploadView page (`scout-frontend/src/views/UploadView.vue`)

Single-column scrolling layout (D-05), no left-right split:
1. Header with title/description
2. Card containing UploadZone (pre-upload) OR ParseProgress (during parsing) OR done state
3. Info cards (what's parsed, data privacy) — hidden during parsing/done states
4. On complete: `resumeStore.loadParsed(id)` → 800ms delay → `router.push('/review/${resumeId}')`

### api.ts upload service

`uploadWithProgress(formData, onProgress)`:
1. **Primary path**: `POST /api/upload/stream` — reads SSE via `fetch + ReadableStream.getReader()`. Parses `data:` lines, emits each step event, returns `resume_id` from `done` event.
2. **Fallback path**: `POST /api/upload` — emits simulated progress at 1.2s intervals while waiting for response, emits `done` on success.

## SSE Fallback Strategy

EventSource API doesn't support POST with body, so SSE is implemented via `fetch + ReadableStream`. If `/upload/stream` returns non-200 or has no body, the function falls back to regular POST with simulated progress ticks — allowing the frontend to work independently while Plan 02's SSE endpoint is developed in parallel (Wave 2).

## File Validation Approach

- **Client-side**: MIME type check + file extension check (`.pdf`, `.docx`) + 20 MB size limit → inline error shown in UI before any network request
- **Server-side enforcement**: Plan 02's backend validates magic bytes and enforces size limits (T-02-01, FileSizeLimitMiddleware)
- Per threat model T-04-01: client validation is UX only; server is the real enforcement layer

## shadcn-vue UI Components

Hand-crafted (shadcn-vue CLI v2.5.3 rejected existing `components.json` due to schema change):
- `Badge` — file size chip, variants: default/secondary/destructive/outline
- `Button` — primary/outline/ghost/secondary, sizes: sm/default/lg
- `Input` — v-model compatible, inherits attrs for type/placeholder
- `Label` — associates with input via `for` prop
- `Card` — rounded border container used as upload zone wrapper

## Deviations from Plan

### [Rule 3 - Blocking] shadcn-vue CLI rejected components.json

- **Found during:** Task 1 setup
- **Issue:** `npx shadcn-vue@latest add badge button...` failed — CLI v2.5.3 changed its schema and rejected the existing `components.json` with `"framework": "vite"` key
- **Fix:** Removed invalid `"framework"` key from `components.json`; created all 5 UI component families (Badge, Button, Input, Label, Card) manually as equivalent shadcn-vue style components
- **Files modified:** `scout-frontend/components.json`, `scout-frontend/src/components/ui/*/`
- **Commit:** f8ca68c

### [Rule 1 - Bug] TypeScript error in uploadWithSimulatedProgress

- **Found during:** Task 1 verification (build)
- **Issue:** `steps[stepIdx++]` typed as `UploadProgressEvent | undefined` — TS strict mode rejects passing undefined to `onProgress()`
- **Fix:** Extracted to `const step = steps[stepIdx]`, guarded with `if (step)` before calling `onProgress(step)`
- **Files modified:** `scout-frontend/src/services/api.ts`
- **Commit:** f8ca68c

**Total deviations:** 2 auto-fixed (1 Rule 3 blocking, 1 Rule 1 bug). **Impact:** No plan scope change — all planned components delivered as specified.

## Self-Check

- [x] `scout-frontend/src/components/UploadZone.vue` exists
- [x] `scout-frontend/src/components/ParseProgress.vue` exists
- [x] `scout-frontend/src/views/UploadView.vue` updated (full implementation)
- [x] `scout-frontend/src/services/api.ts` updated (uploadWithProgress added)
- [x] `npm run build` exits 0 (verified, no TypeScript errors)
- [x] Commits f8ca68c and 00f7fa3 exist

## Self-Check: PASSED
