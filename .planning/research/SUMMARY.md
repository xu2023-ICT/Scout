# Research Summary -- Scout

**Project:** Scout (AI Job Hunting Agent)
**Domain:** AI-powered autonomous job search + resume tailoring for Chinese market
**Researched:** 2026-04-10
**Overall Confidence:** HIGH

---

## Executive Summary

Scout occupies a genuine gap in the market. Existing tools are either resume editors (user pastes JD, gets keyword-stuffed output) or auto-apply bots (mass submission, 1-3% callback rate, platform bans). Nobody does what Scout proposes: proactive job search + deep company/role research + interview-prep content grounded in real forum data. The competitive landscape validates this positioning -- no Chinese-market tool combines autonomous search with per-job research and content generation.

The recommended build approach is a Python + FastAPI modular monolith with a Vue 3 SPA frontend. AI orchestration should use the raw Anthropic Python SDK with a custom agent loop (~100-200 lines), not LangChain or any framework. Web scraping uses Crawl4AI backed by Playwright. The architecture is straightforward: FastAPI handles HTTP + SSE, background tasks handle the multi-step pipeline (search -> scrape -> research -> generate), SQLite stores everything via SQLAlchemy (swap to PostgreSQL later with one config change). Start with FastAPI BackgroundTasks, migrate to Celery + Redis only when concurrency demands it.

The two existential risks are: (1) scraping reliability -- Boss Zhipin and Shixiseng use custom font encryption and aggressive anti-bot measures that will break naive scrapers immediately, and (2) AI output quality -- 33% of hiring managers detect AI-generated resumes in under 20 seconds, and hallucinated experience on a resume can end a candidate career. Both risks have known mitigations but must be addressed from day one, not bolted on later. A secondary but legally binding risk is PIPL compliance: sending Chinese users resume data to Anthropic overseas API constitutes cross-border data transfer and requires explicit user consent.

---

## Recommended Stack (one-liner per component)

| Component | Choice | Why This, Not That |
|-----------|--------|-------------------|
| **Backend runtime** | Python 3.12+ | The entire AI/scraping ecosystem is Python-first. Claude assists best in Python. |
| **Web framework** | FastAPI | Async-native, auto-generates API docs, Pydantic validation built in. Not Django (too heavy), not Flask (no async). |
| **Frontend** | Vue 3 + Vite + shadcn-vue + Tailwind | Lowest learning curve for a solo dev. Not React (steeper), not Streamlit (no routing, will rewrite). |
| **AI SDK** | anthropic Python SDK (direct) | Custom agent loop in ~100 lines. Not LangChain (massive abstraction), not Agent SDK (for code-editing agents). |
| **Scraping** | Crawl4AI + Playwright fallback | LLM-optimized output, built-in stealth mode, 51k+ stars. Not Scrapy (overkill), not Selenium (legacy). |
| **Search API** | Tavily | AI-agent-native search, 1,000 free credits/month. Not SerpAPI (only 100 free searches). |
| **Database** | SQLite + SQLAlchemy + Alembic | Zero setup, single-file. Swap to PostgreSQL by changing one connection string. |
| **PDF parsing** | PyMuPDF + PaddleOCR fallback | Fastest PDF parser. OCR fallback for image-based Chinese resumes. |
| **HTTP client** | httpx | Async-native, pairs with FastAPI. |
| **Task queue (later)** | Celery + Redis | Only when concurrent users demand it. Start with FastAPI BackgroundTasks. |
| **Frontend hosting** | Vercel (free) | One-click Vue SPA deploy. |
| **Backend hosting** | Railway ($5/mo) or Render (free) | Managed deploy from GitHub. |

---

## Table Stakes Features (must ship in v1)

Missing any of these and users will consider the product broken:

1. **Resume upload + AI parsing** -- PDF and Word. Chinese resume conventions (zhengzhi mianmao, jiguan, etc). Use LLM extraction, not regex.
2. **Resume structure display** -- Show what the system understood. Editable. Builds trust.
3. **JD keyword extraction + match scoring** -- Every competitor does this. Users expect it.
4. **ATS-friendly resume output** -- Single-column, standard headers, .docx format. 62% of employers reject non-ATS resumes.
5. **Per-job tailored resume generation** -- The core promise. Rewrite bullet points for each JD, do not just stuff keywords.
6. **Job listing display with filtering** -- City, salary, company size, industry. Sort by match score.
7. **Export as PDF/Word** -- Users must download and manually submit.
8. **Full Chinese language support** -- Not just i18n. Resume field conventions, JD terminology, platform jargon.
9. **User account + persistence** -- Users come back. History matters.

---

## Differentiators (Scout competitive edge)

These are what make Scout genuinely different. No competitor has them. Lean hard:

1. **Autonomous job search agent** -- User sets preferences once; Scout crawls Boss Zhipin, Shixiseng, etc. and surfaces matching jobs. Zero browsing. Start with Boss Zhipin only.
2. **Deep company research per job** -- Auto-research funding, news, products, tech blog, culture signals. Uses Tavily search + Claude synthesis.
3. **Interview question aggregation from Niuker** -- Scrape real interview questions for that specific company + role. Massive value in Chinese market where miangjing culture is dominant.
4. **Cross-JD keyword frequency analysis** -- Aggregate keywords across 10+ similar JDs. "React appears in 90% of similar JDs; GraphQL only in 15%." Genuinely novel.
5. **Interview talking points generation** -- Personalized answers grounded in real interview questions + company research. Not generic templates.
6. **GitHub repo analysis** -- Extract tech stack, contributions, stars. Feed into resume tailoring. Keep it simple (README + languages + stars).
7. **Paper/publication analysis** -- For the target demographic (grad students). Map academic work to JD relevance.

---

## Architecture in One Page

```
+-------------------+          +-------------------+
|   Vue 3 SPA       |   HTTP   |   FastAPI         |
|   (Vercel)        |--------->|   API Layer       |
|                   |<---------|   (Railway)       |
|   - Upload UI     |   SSE    |                   |
|   - Job Board     |          |   /api/upload     |
|   - Kanban        |          |   /api/search     |
|   - Track Changes |          |   /api/jobs       |
|   - SSE Listener  |          |   /api/stream/{id}|
+-------------------+          +--------+----------+
                                        |
                               +--------v----------+
                               |  Background Tasks  |
                               |  (BackgroundTasks  |
                               |   -> Celery later) |
                               |                    |
                               |  Pipeline:         |
                               |  1. Search jobs    |
                               |  2. Scrape JDs     |
                               |  3. Research co.   |
                               |  4. Generate docs  |
                               +---+------------+---+
                                   |            |
                          +--------v--+    +----v---------+
                          | Crawl4AI  |    | Claude API   |
                          | Playwright|    | (anthropic)  |
                          | Tavily    |    | Sonnet: bulk |
                          +-----------+    | Opus: final  |
                                           +--------------+
                                    |
                          +---------v---------+
                          |  SQLite           |
                          |  (-> PostgreSQL)  |
                          |                   |
                          |  users            |
                          |  user_materials   |
                          |  user_profiles    |
                          |  scout_runs       |
                          |  jobs             |
                          |  generated_content|
                          +-------------------+
```

**Key architectural decisions:**

- **Modular monolith, not microservices.** Solo dev, one deployable unit, clear internal boundaries.
- **SSE for progress, not WebSocket.** One-directional push is sufficient. HTTP-native, auto-reconnect, simpler.
- **BackgroundTasks first, Celery later.** Avoid Redis overhead until concurrent users demand it.
- **JSONB for semi-structured data.** JD parsed data, company info, interview data vary per platform. Do not over-normalize.
- **Repository pattern for data access.** Keep SQL out of task code. Makes testing trivial.
- **Idempotent tasks with DB checkpointing.** Every pipeline step persists results. Failures resume, not restart.
- **Model routing for cost control.** Haiku for classification, Sonnet for synthesis, Opus for final generation only.

---

## Critical Risks (top 5, ranked)

### 1. Scraping breaks on day one (CRITICAL)

Boss Zhipin uses custom font-file encryption (woff), CAPTCHA after ~10 pages, IP bans after ~6 CAPTCHAs. Shixiseng has similar font encryption. Naive scrapers produce garbled salary/company data.

**Mitigation:** Font-file interception with fontTools decoder. Strict rate limiting (3-5s random delays, max 100 req/hr). Playwright with stealth plugin. Circuit breaker pattern -- stop scraping a platform after N failures, fall back to manual JD input. Build scraper adapter pattern so each platform is a pluggable module.

### 2. AI-generated resumes get candidates rejected (CRITICAL)

33% of hiring managers detect AI resumes in <20 seconds. Telltale words: "synergize," "transformative," "pivotal," "spearheaded." LLMs default to a generic polished "resume voice."

**Mitigation:** Preserve user writing style. Maintain AI-word blocklist. Require concrete metrics from actual experience. Diff-based output showing exactly what changed and why. Run QA through AI detectors. Never fabricate -- report skill gaps to user instead.

### 3. Content hallucination destroys user careers (CRITICAL)

LLMs will invent skills, inflate titles, fabricate metrics when asked to "optimize" a resume for a JD the user does not fully match.

**Mitigation:** Strict grounding constraint -- only use information from uploaded materials. Separate "rephrase" (safe) from "add" (requires user confirmation). Cross-reference every generated claim against source materials. Confidence scoring per modification.

### 4. API costs spiral before finding product-market fit (HIGH)

50 jobs x 5 LLM calls x 4K tokens = real money. A single user session could cost $5-15 without optimization.

**Mitigation:** Model routing (Haiku/Sonnet/Opus tiering cuts costs 60-80%). Prompt caching (cache_control parameter, 90% reduction on cached tokens). Batch API for non-real-time work (50% discount). Token budgets per call. Cache company research across users. User-provided API key option.

### 5. PIPL compliance violation (HIGH)

Resume data is sensitive PII. Sending it to Anthropic overseas API is cross-border data transfer under PIPL. No "legitimate interest" exception exists -- explicit consent required. Fines up to RMB 50M.

**Mitigation:** Explicit consent flow before any processing. Privacy policy in Chinese. Data minimization (do not send full resume for every call). Retention policy with auto-delete. Encryption at rest. Inform users about cross-border transfer.

---

## Build Order Recommendation

### Phase 1: Vertical Slice (Foundation)

Build one complete path through the system, even if crude.

**What to build:**
- Database models (SQLite + SQLAlchemy)
- Resume upload endpoint (FastAPI + file storage)
- Resume parsing with PyMuPDF + Claude for structure extraction
- Manual JD input (user pastes JD text -- skip scraping entirely)
- Claude integration for one tailored resume generation
- Simple Vue frontend: upload resume, paste JD, see generated resume
- Chinese language support throughout

**Why first:** Validates the core value proposition (AI-generated tailored resume) without any scraping complexity. Get something you can demo and test with real users. If the generated resume quality is bad, nothing else matters.

**Pitfalls to address here:** Resume content hallucination (P4), AI-detectable output (P3), Chinese PDF parsing (P7). Build the grounding constraints and diff-based output into the prompt architecture from the start.

**Features delivered:** T1, T2, T3, T5, T8, T9 (partial)

**Research needed:** No -- well-documented patterns for all components.

### Phase 2: Async Pipeline + Scraping

Move long-running work off the request cycle. Add autonomous search.

**What to build:**
- BackgroundTasks integration for pipeline steps
- SSE progress streaming to frontend
- Playwright + Crawl4AI setup with stealth mode
- Boss Zhipin scraper with font decryption
- Font-file decoder utility (reusable for Shixiseng)
- Rate limiting, circuit breakers, scraper adapter pattern
- JD parsing pipeline (scrape -> extract keywords -> match score)
- Job listing display with filtering

**Why second:** Scraping is the riskiest technical component. Build it after the core generation pipeline works, so if scraping is blocked, the product still works with manual JD input as fallback. The async pipeline is prerequisite for scraping (which is slow).

**Pitfalls to address here:** Font encryption (P1, P2), IP bans (P1), silent pipeline failures (P5), scraper structure breakage (P11).

**Features delivered:** D1, T6, T3 (enhanced)

**Research needed:** YES -- Boss Zhipin anti-scraping specifics change frequently. Need real-time testing during implementation.

### Phase 3: Deep Research + Content Generation

The "wow" factor -- what makes Scout genuinely different.

**What to build:**
- Company research module (Tavily search + Claude synthesis)
- Niuker interview question scraping
- Cross-JD keyword frequency analysis
- Interview talking points generation
- ATS-optimized output formatting
- Track-changes view (diff between original and modified resume)
- Per-change approval UI

**Why third:** These are differentiators, not table stakes. The product is useful without them (Phase 1+2 is already a job aggregator + resume tailor). But these features are what make users stay and recommend Scout.

**Pitfalls to address here:** ATS keyword stuffing (P8), user trust/opacity (P9), outdated miangjing (P13), context window overflow (P14).

**Features delivered:** D2, D3, D4, D5, T4, T9 (full)

**Research needed:** YES -- Niuker scraping specifics, interview data freshness handling.

### Phase 4: User Management + Polish

Round out the product experience.

**What to build:**
- Auth system (JWT or session-based)
- User profile persistence + history
- Job kanban board (Discovered -> Researched -> Generated -> Applied)
- GitHub repo analysis (simple: README + languages + stars)
- Paper/publication analysis
- HITL interrupt flow (pipeline pauses, asks user, resumes)
- Cost tracking dashboard
- PIPL consent flow + privacy policy
- Export improvements

**Why fourth:** These features make the product feel complete, but each phase before this is independently useful. Ship and get feedback before polishing.

**Pitfalls to address here:** PIPL compliance (P10), GitHub overengineering (P12).

**Features delivered:** T7, D6, D7, D8

**Research needed:** No -- standard patterns for auth, kanban, and profile management.

### Phase 5: Scale Readiness (if traction)

Only if the product gains users.

**What to build:**
- Migrate SQLite to PostgreSQL
- Add Celery + Redis for concurrent pipeline execution
- Shixiseng scraper (using shared font decoder)
- Proxy rotation pool for scraping
- Batch API integration for cost reduction
- User-provided API key support

**Why last:** Premature scaling is a waste. Validate first.

---

## Decisions Made By Research

These are settled. Do not relitigate.

| Decision | Settled Answer | Why It Is Final |
|----------|---------------|----------------|
| Backend language | Python | AI/scraping ecosystem is Python-first. No contest. |
| Web framework | FastAPI | Async-native, auto-docs, Pydantic. Lighter than Django, better than Flask. |
| Frontend framework | Vue 3 | Lowest learning curve for solo dev. SSR unnecessary for dashboard SPA. |
| AI orchestration | Raw anthropic SDK | LangChain adds massive abstraction for a sequential agent. Custom loop is ~100 lines. |
| Primary scraper | Crawl4AI | LLM-optimized output, built-in stealth, largest open-source crawler. |
| Database (start) | SQLite | Zero setup. SQLAlchemy makes migration to PostgreSQL a config change. |
| Auto-apply | DO NOT BUILD | Triggers platform bans, violates ToS, 1-3% callback rate, 33% of hiring managers detect and reject. |
| LinkedIn scraping | DO NOT BUILD (v1) | LinkedIn litigates aggressively. Legal risk disproportionate to value. Use search APIs instead. |
| Cover letter gen | DEFER to v2 | Cover letters uncommon in Chinese job market. Not a priority. |
| Keyword optimization target | 70-80%, not 100% | Modern ATS penalizes keyword stuffing. Semantic matching is standard. |
| Resume truthfulness | STRICT -- never fabricate | Report gaps to user instead of filling them. One viral "Scout faked my resume" story kills the product. |
| Progress reporting | SSE, not WebSocket | One-directional push is sufficient. HTTP-native, simpler, auto-reconnect. |
| Task queue (MVP) | BackgroundTasks, not Celery | Avoid Redis overhead until concurrent users demand it. |

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Python + FastAPI is the dominant AI backend stack 2025-2026. Vue 3 learning curve advantage is well-documented. All libraries verified on PyPI with recent releases. |
| Features | MEDIUM-HIGH | Competitive landscape well-mapped. Chinese market specifics based on domain knowledge + partial search results. Anti-feature recommendations strongly supported by employer survey data. |
| Architecture | MEDIUM-HIGH | Modular monolith pattern well-established. Pipeline + checkpoint pattern validated by Amazon/Zylos research. Boss Zhipin API endpoint details need real-time verification. |
| Pitfalls | HIGH | Anti-scraping mechanisms confirmed by multiple CSDN/52pojie sources. AI detection stats from Gartner/Stanford. PIPL requirements from legal sources. |
| Deployment | MEDIUM | Railway/Render are solid today but pricing/features change frequently. Verify before deploying. |

**Overall confidence: HIGH**

### Gaps to Address

1. **Boss Zhipin scraping specifics change frequently.** Font encryption and anti-bot measures are an arms race. Must test during implementation, not just research.
2. **Shixiseng anti-scraping details are less documented** than Boss Zhipin. May need trial-and-error during Phase 2/5.
3. **PaddleOCR setup complexity on different platforms** (Windows/Linux/Mac) needs verification. May have CUDA dependency issues.
4. **Tavily free tier limits in practice** -- 1,000 credits/month sounds generous but need to measure actual per-job consumption.
5. **PIPL cross-border data transfer requirements** for a student project vs. a commercial product -- legal gray area. Implement consent flow regardless.

---

## Sources

**Primary (HIGH confidence):**
- [FastAPI official docs](https://fastapi.tiangolo.com/) -- framework capabilities, SSE support
- [Anthropic Python SDK](https://pypi.org/project/anthropic/) -- tool use, agent patterns
- [Crawl4AI docs v0.8.x](https://docs.crawl4ai.com/) -- scraping capabilities, stealth mode
- [Claude tool use tutorial](https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent) -- agent loop pattern
- [PIPL legal text](https://www.china-briefing.com/doing-business-guide/china/company-establishment/pipl-personal-information-protection-law) -- compliance requirements
- [Gartner 2025 survey](https://www.gartner.com/en/newsroom/press-releases/2025-07-31-gartner-survey-shows-just-26-percent-of-job-applicants-trust-ai-will-fairly-evaluate-them) -- user trust data

**Secondary (MEDIUM confidence):**
- [Boss Zhipin anti-scraping - CSDN](https://blog.csdn.net/m0_62074330/article/details/145246276) -- font encryption specifics
- [Amazon agent evaluation - AWS](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/) -- pipeline reliability patterns
- [Resume fraud research - Crosschq](https://www.crosschq.com/blog/resume-fraud-the-600-billion-crisis-transforming-how-organizations-verify-talent-in-2025) -- hallucination risks
- [Claude cost optimization - DEV](https://dev.to/whoffagents/claude-api-cost-optimization-caching-batching-and-60-token-reduction-in-production-3n49) -- caching/batching strategies

**Tertiary (needs validation during implementation):**
- Boss Zhipin API endpoint (/wapi/zpgeek/search/joblist.json) -- may have changed
- Shixiseng font-based anti-scraping specifics -- less documented
- PaddleOCR system requirements for target deployment platform

---
*Research completed: 2026-04-10*
*Ready for roadmap: yes*
