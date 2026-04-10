# Architecture Patterns

**Domain:** AI Job Hunting Agent Platform (Scout)
**Researched:** 2026-04-10

## Recommended Architecture

**Modular monolith** with async task queue. Do NOT split into microservices -- solo developer, greenfield, need to move fast. A single deployable unit with clear internal module boundaries gives you microservice-like separation without the operational overhead.

### System Overview (ASCII Diagram)

```
                          +------------------+
                          |   React / Next   |
                          |   Frontend       |
                          |                  |
                          |  - Upload UI     |
                          |  - Job Board     |
                          |  - SSE Listener  |
                          +--------+---------+
                                   |
                            HTTP / SSE
                                   |
                          +--------v---------+
                          |   FastAPI         |
                          |   API Layer       |
                          |                   |
                          |  /api/upload      |
                          |  /api/search      |
                          |  /api/jobs        |
                          |  /api/stream/{id} |
                          +--------+----------+
                                   |
                    +--------------+--------------+
                    |                             |
             +------v------+              +------v------+
             |   Redis     |              | PostgreSQL  |
             |             |              |             |
             | - Task Queue|              | - Users     |
             | - SSE Pub/  |              | - Resumes   |
             |   Sub       |              | - Jobs      |
             | - Cache     |              | - Content   |
             +------+------+              | - Runs      |
                    |                     +-------------+
             +------v------+
             |   Celery    |
             |   Workers   |
             |             |
             | +----------+|     +-----------------+
             | |Pipeline  ||---->| Scraper Module  |
             | |Orchestr. ||     | (Playwright)    |
             | +----------+|     +-----------------+
             |             |
             | +----------+|     +-----------------+
             | |AI Engine ||---->| Claude API      |
             | |          ||     | (Anthropic SDK) |
             | +----------+|     +-----------------+
             +-------------+

```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **Frontend** | Upload materials, display job board, show progress via SSE, present generated content | API Layer (HTTP, SSE) |
| **API Layer (FastAPI)** | REST endpoints, auth, file upload, SSE streaming, enqueue tasks | Frontend, Redis, PostgreSQL |
| **Task Queue (Redis + Celery)** | Async job orchestration, pipeline state, progress pub/sub | API Layer, Workers |
| **Pipeline Orchestrator** | Multi-step workflow: search -> scrape -> research -> generate. Manages step transitions, retries, HITL pauses | Scraper, AI Engine, PostgreSQL |
| **Scraper Module** | Playwright-based headless browser scraping with rate limiting, retry, User-Agent rotation | Boss Zhipin, Shixiseng, Niuker |
| **AI Engine** | Claude API calls for resume parsing, JD analysis, company research synthesis, content generation | Claude API (Anthropic SDK) |
| **PostgreSQL** | Persistent storage for all domain data | API Layer, Workers |
| **Redis** | Task broker, result backend, SSE pub/sub channel, short-lived cache | API Layer, Celery |

---

## Data Flow

### Primary Flow: User Triggers Scout Run

```
1. User uploads resume + materials
   Frontend --POST /api/upload--> API --> Parse & store in PostgreSQL
                                     --> Celery task: parse_resume(user_id)

2. User sets preferences & triggers search
   Frontend --POST /api/search--> API --> Celery task chain:
                                          search_jobs(user_id, prefs)
                                           |
                                           v
                                         For each job found:
                                           scrape_jd(job_id)
                                             |
                                             v
                                           research_company(job_id)
                                             |
                                             v
                                           generate_content(job_id, user_id)

3. Progress updates flow back via SSE
   Celery worker --> Redis PUBLISH progress:{run_id}
   API /api/stream/{run_id} --> Redis SUBSCRIBE --> SSE to Frontend

4. User reviews results on job board
   Frontend --GET /api/jobs/{run_id}--> API --> PostgreSQL --> JSON response
```

### Secondary Flow: Human-in-the-Loop (HITL) Interrupt

```
1. AI Engine detects insufficient info for generation
   Worker --> Update run status to "needs_input" in PostgreSQL
          --> Redis PUBLISH progress:{run_id} with type="input_required"

2. Frontend receives SSE event, shows input modal
   User fills in missing info --> POST /api/runs/{run_id}/respond

3. API stores response, resumes Celery chain
   API --> Update PostgreSQL --> Celery task: resume_pipeline(run_id)
```

---

## Data Model

### Core Entities

```
users
  id              UUID PK
  email           VARCHAR UNIQUE
  created_at      TIMESTAMP
  preferences     JSONB          -- city, industry, job_type

user_materials
  id              UUID PK
  user_id         UUID FK -> users
  type            ENUM('resume', 'paper', 'github', 'other')
  file_path       VARCHAR        -- S3/local path for files
  url             VARCHAR        -- for GitHub links
  parsed_data     JSONB          -- AI-extracted structured data
  created_at      TIMESTAMP

user_profiles (parsed/structured resume data)
  id              UUID PK
  user_id         UUID FK -> users
  skills          JSONB          -- [{name, level, years}]
  experiences     JSONB          -- [{company, role, duration, highlights}]
  education       JSONB          -- [{school, degree, major, gpa}]
  projects        JSONB          -- [{name, description, tech_stack, url}]
  publications    JSONB          -- [{title, venue, year, contribution}]
  github_summary  JSONB          -- {top_repos, languages, stars}
  updated_at      TIMESTAMP

scout_runs (one "search session")
  id              UUID PK
  user_id         UUID FK -> users
  status          ENUM('queued','searching','scraping','researching',
                       'generating','needs_input','completed','failed')
  preferences     JSONB          -- snapshot of search params
  progress        JSONB          -- {total_jobs, completed, current_step}
  error_message   TEXT
  created_at      TIMESTAMP
  completed_at    TIMESTAMP

jobs
  id              UUID PK
  run_id          UUID FK -> scout_runs
  platform        VARCHAR        -- 'boss_zhipin', 'shixiseng'
  external_id     VARCHAR        -- platform-specific ID
  title           VARCHAR
  company_name    VARCHAR
  location        VARCHAR
  salary_range    VARCHAR
  jd_raw          TEXT           -- raw JD text
  jd_parsed       JSONB          -- {keywords, requirements, nice_to_haves}
  company_info    JSONB          -- {funding, products, tech_blog, culture}
  team_info       JSONB          -- {tech_stack, size, hiring_manager}
  interview_data  JSONB          -- {questions, process, difficulty}
  match_score     FLOAT          -- AI-computed relevance score
  status          ENUM('scraped','researched','generated','skipped')
  created_at      TIMESTAMP

generated_content
  id              UUID PK
  job_id          UUID FK -> jobs
  user_id         UUID FK -> users
  type            ENUM('resume', 'interview_script', 'cover_letter')
  content         TEXT           -- generated markdown/text
  metadata        JSONB          -- {model_used, tokens_used, generation_params}
  version         INT DEFAULT 1
  created_at      TIMESTAMP

hitl_interactions (human-in-the-loop)
  id              UUID PK
  run_id          UUID FK -> scout_runs
  job_id          UUID FK -> jobs (nullable)
  question        TEXT           -- what the AI is asking
  context         JSONB          -- why it needs this info
  response        TEXT           -- user's answer
  status          ENUM('pending', 'answered', 'skipped')
  created_at      TIMESTAMP
  answered_at     TIMESTAMP
```

### Why JSONB Over Normalized Tables

For `jd_parsed`, `company_info`, `team_info`, etc.: These are semi-structured data from scraping where the shape varies per platform and per listing. Normalizing them would create dozens of tables with sparse columns. JSONB in PostgreSQL gives you:
- Flexible schema per record
- GIN indexing for queries
- Easy evolution without migrations
- Good enough query performance for this scale

### Why Separate `user_profiles` From `user_materials`

Raw materials (PDFs, links) live in `user_materials`. The AI-extracted structured profile lives in `user_profiles`. This separation means:
- Re-parsing doesn't lose the originals
- Multiple materials contribute to one unified profile
- The profile is what gets passed to content generation

---

## Pipeline Orchestrator Design

### Why Plain Python + Celery, NOT LangGraph

LangGraph is powerful but adds significant complexity for a solo developer:
- Steep learning curve for graph-based state machines
- Debugging is harder with framework abstraction
- Infrastructure overhead (checkpointing, persistence)
- The pipeline here is fundamentally linear with conditional branching -- not a complex graph

**Use Celery chains and chords instead.** They provide:
- Simple sequential step chaining (`chain`)
- Parallel fan-out for per-job processing (`chord`/`group`)
- Built-in retries with exponential backoff
- Result tracking via Redis backend
- Mature, battle-tested, well-documented

### Pipeline Steps as Celery Tasks

```python
# Pseudo-code for pipeline structure

# Step 1: Search across platforms (parallel)
search_group = group(
    search_boss_zhipin.s(user_id, prefs),
    search_shixiseng.s(user_id, prefs),
)

# Step 2: For each found job, sequential sub-pipeline
def per_job_pipeline(job_id, user_id):
    return chain(
        scrape_full_jd.s(job_id),
        research_company.s(job_id),
        check_info_sufficient.s(job_id, user_id),  # may pause for HITL
        generate_content.s(job_id, user_id),
    )

# Step 3: Fan out per-job pipelines
# After search completes, dynamically create per-job chains
@app.task
def orchestrate_run(run_id):
    run = get_run(run_id)
    job_ids = run_search(run)  # Step 1
    
    for job_id in job_ids:
        per_job_pipeline(job_id, run.user_id).apply_async()
```

### HITL Interrupt Pattern

When `check_info_sufficient` determines more info is needed:

1. Task updates `scout_runs.status = 'needs_input'`
2. Creates a `hitl_interactions` record with the question
3. Publishes SSE event via Redis pub/sub
4. Task **returns without raising** -- the chain stops naturally
5. When user responds via API, a new task `resume_pipeline(run_id, job_id)` is enqueued
6. The resumed task picks up from `generate_content` step

This is simpler than LangGraph's checkpoint-based interrupt because:
- State is in the database, not in a framework-managed checkpoint
- No special resume mechanism -- just enqueue a new task
- The "pause" is just "don't enqueue the next step yet"

---

## Scraper Module Architecture

### Design Principles

1. **Playwright over Selenium** -- faster, more modern, better async support, built-in auto-waiting
2. **One scraper class per platform** -- `BossZhipinScraper`, `ShixisengScraper` with shared base
3. **Rate limiting at the scraper level** -- not the task level
4. **Respect the sites** -- delays, rotating User-Agents, no login-required endpoints

### Scraper Base Class

```python
class BaseScraper:
    """All scrapers inherit this for consistent rate limiting and retry."""
    
    RATE_LIMIT_DELAY = (2, 5)     # random delay range in seconds
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 2            # exponential backoff multiplier
    CONCURRENT_LIMIT = 2          # max concurrent pages per domain
    
    async def scrape_with_retry(self, url):
        """Retry with exponential backoff + jitter."""
        for attempt in range(self.MAX_RETRIES):
            try:
                await self.rate_limit_delay()
                return await self._do_scrape(url)
            except RateLimitError:
                wait = self.BACKOFF_FACTOR ** attempt + random.uniform(0, 1)
                await asyncio.sleep(wait)
        raise ScrapingFailedError(url)
    
    async def rate_limit_delay(self):
        """Random delay between requests to avoid detection."""
        delay = random.uniform(*self.RATE_LIMIT_DELAY)
        await asyncio.sleep(delay)
```

### Boss Zhipin Specific Notes

Based on research into Boss Zhipin's anti-scraping measures:
- **API endpoint exists**: `https://www.zhipin.com/wapi/zpgeek/search/joblist.json` returns JSON -- prefer this over HTML parsing
- **Required headers**: Cookie, User-Agent, Referer must be set correctly
- **Detection avoidance**: Use `playwright-extra` with stealth plugin to mask headless browser signals
- **IP throttling**: Implement per-domain rate limiting; if blocked, the system should gracefully degrade (skip platform, notify user)
- **No login scraping**: Only scrape publicly accessible JD pages -- the project explicitly avoids login-required endpoints

### Shixiseng (实习僧) Notes

- No official public API found
- HTML scraping via Scrapy/Playwright is the standard approach
- Simpler anti-scraping compared to Boss Zhipin
- Data available: job title, city, work days/week, duration, salary, company info

---

## AI Engine: Context Engineering for Content Generation

### What to Pass to Claude for Resume Generation

The quality of generated resumes depends entirely on what context Claude receives. Structure the prompt in layers:

```
Layer 1: System Prompt (fixed)
  - Role: Expert resume writer for Chinese job market
  - Output format: Structured resume sections
  - Constraints: Truthful (never fabricate), keyword-optimized, concise

Layer 2: User Profile (from user_profiles table)
  - Full parsed resume data (skills, experiences, education, projects)
  - GitHub analysis summary
  - Paper contributions

Layer 3: Job Context (from jobs table)
  - Parsed JD with keyword frequency analysis
  - Company background (funding, products, culture)
  - Team tech stack preferences
  - Interview data (common questions, process)

Layer 4: Market Context (aggregated)
  - Common keywords across similar JDs (what the market actually wants)
  - Salary benchmarks for this role type

Layer 5: Task-Specific Instructions
  - "Generate a resume tailored for {job_title} at {company_name}"
  - "Emphasize these top-5 matching skills: {skills}"
  - "Mirror these JD keywords naturally: {keywords}"
  - "Highlight this project because it aligns with {company_product}"
```

### Token Budget Strategy

With Claude's 200K context window, budget roughly:
- System prompt: ~500 tokens
- User profile: ~2,000 tokens (even detailed resumes)
- Job context: ~3,000 tokens (JD + company + team + interviews)
- Market context: ~1,000 tokens (aggregated keywords)
- Instructions: ~500 tokens
- **Total input: ~7,000 tokens** -- well within limits

For the interview script generation, include interview questions from Niuker/Glassdoor as additional context (~2,000 tokens more).

### Cost Control

- Use `claude-sonnet` for bulk operations (JD parsing, keyword extraction) -- cheaper, fast enough
- Use `claude-opus` only for final resume/script generation where quality matters most
- Cache company research results -- same company info reused across multiple job listings
- Batch JD parsing: parse multiple JDs in one API call where possible

---

## Real-Time Progress: SSE Architecture

### Why SSE, Not WebSocket

- **Simpler**: One-directional server-to-client push is all we need
- **HTTP-native**: Works through proxies, CDNs, load balancers without special config
- **Auto-reconnect**: Built into the EventSource browser API
- **2025 standard**: FastAPI has native SSE support; it's the standard for AI streaming

### Implementation Pattern

```python
# API endpoint
@app.get("/api/stream/{run_id}")
async def stream_progress(run_id: str):
    async def event_generator():
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"progress:{run_id}")
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield {
                    "event": "progress",
                    "data": message["data"]
                }
    return EventSourceResponse(event_generator())

# Worker publishes progress
def publish_progress(run_id, step, detail):
    redis.publish(f"progress:{run_id}", json.dumps({
        "step": step,          # "searching", "scraping", "researching", "generating"
        "detail": detail,      # "Scraping JD for Software Engineer at ByteDance"
        "progress": 0.45,      # 0.0 to 1.0
        "timestamp": now()
    }))
```

---

## Patterns to Follow

### Pattern 1: Repository Pattern for Data Access

Separate database queries from business logic. Each entity gets a repository class.

```python
class JobRepository:
    async def create(self, job_data: dict) -> Job: ...
    async def get_by_run(self, run_id: str) -> list[Job]: ...
    async def update_status(self, job_id: str, status: str): ...
    async def get_with_content(self, job_id: str) -> JobWithContent: ...
```

**Why:** Makes testing easier (mock the repo), keeps SQL out of task code, single place to optimize queries.

### Pattern 2: Task Idempotency

Every Celery task should be safe to retry without side effects.

```python
@app.task(bind=True, max_retries=3)
def scrape_full_jd(self, job_id):
    job = JobRepo.get(job_id)
    if job.status == 'scraped':  # already done
        return job_id            # idempotent -- skip
    try:
        data = scraper.scrape(job.url)
        JobRepo.update(job_id, jd_raw=data, status='scraped')
        return job_id
    except Exception as exc:
        self.retry(exc=exc, countdown=2 ** self.request.retries)
```

**Why:** Network failures, worker restarts, duplicate messages are inevitable. Idempotent tasks handle all of these.

### Pattern 3: Configuration as Environment Variables

```
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-...
SCRAPE_RATE_LIMIT_MIN=2
SCRAPE_RATE_LIMIT_MAX=5
SCRAPE_MAX_CONCURRENT=2
```

**Why:** 12-factor app principles. Easy to change between dev/staging/prod. Secrets never in code.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: LLM Calls in the Request Cycle

**What:** Calling Claude API directly in a FastAPI endpoint handler.
**Why bad:** Claude calls take 5-30 seconds. HTTP connections time out. Users see loading spinners. Server threads block.
**Instead:** Always enqueue LLM work as Celery tasks. Return immediately with a `run_id`. Stream progress via SSE.

### Anti-Pattern 2: Monolithic Prompts

**What:** Stuffing everything (resume + all JDs + all company info) into one giant prompt.
**Why bad:** Token waste, poor quality (model loses focus), expensive, slow.
**Instead:** Process each job independently. One focused prompt per generation task. Use the layered context structure described above.

### Anti-Pattern 3: Storing Files in PostgreSQL

**What:** Storing PDF binary data as BYTEA columns.
**Why bad:** Database bloat, slow backups, can't serve files directly.
**Instead:** Store files on local filesystem (MVP) or S3 (production). Store only the file path in the database.

### Anti-Pattern 4: Scraping Without Circuit Breakers

**What:** Continuing to hit a platform after getting blocked/rate-limited.
**Why bad:** IP gets permanently banned, wastes resources, may trigger legal issues.
**Instead:** Implement circuit breaker -- after N consecutive failures on a platform, stop scraping that platform for this run. Log it. Notify user via SSE.

---

## Suggested Build Order

Build in this order to get a working end-to-end flow as early as possible:

### Phase 1: Vertical Slice (Week 1-2)

Build one complete path through the system, even if crude:

1. **Database models** (PostgreSQL + SQLAlchemy/SQLModel)
2. **Resume upload endpoint** (FastAPI + file storage)
3. **Manual JD input** (skip scraping -- user pastes a JD URL or text)
4. **Claude integration** for resume parsing + one resume generation
5. **Simple frontend** to upload, paste JD, see result

**Why first:** Validates the core value proposition (AI-generated tailored resume) without the complexity of scraping or async pipelines. Get something you can demo.

### Phase 2: Async Pipeline (Week 3-4)

1. **Redis + Celery setup**
2. **Pipeline orchestrator** (chain: parse -> generate)
3. **SSE progress streaming**
4. **Frontend progress UI**

**Why second:** Moves long-running work off the request cycle. Essential before adding scraping (which is slow).

### Phase 3: Scraping (Week 5-6)

1. **Playwright setup + base scraper class**
2. **Boss Zhipin scraper** (API-based first, Playwright fallback)
3. **JD parsing with Claude** (extract keywords, requirements)
4. **Integrate scraping into pipeline** (search -> scrape -> parse -> generate)

**Why third:** Scraping is the riskiest component (anti-scraping measures, legal gray area). Build it after the core pipeline works. If scraping fails, the system still works with manual JD input.

### Phase 4: Deep Research + HITL (Week 7-8)

1. **Company research module** (web search + Claude synthesis)
2. **Interview data scraping** (Niuker/Glassdoor)
3. **Match scoring** (AI-computed job-user fit)
4. **HITL interrupt flow** (pause pipeline, ask user, resume)
5. **Interview script generation**

**Why fourth:** These are differentiators, not table stakes. The product is useful without them (just less differentiated).

### Phase 5: Polish + User Management (Week 9-10)

1. **Auth system** (simple JWT or session-based)
2. **Job board kanban view**
3. **History and saved runs**
4. **Cost tracking** (tokens used per run)
5. **Error handling + retry UI**

---

## Key Architectural Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **Boss Zhipin blocks scraping** | HIGH | HIGH | Design scraper as pluggable module. Support manual JD input as fallback. Implement circuit breakers. | 
| **Claude API costs escalate** | MEDIUM | HIGH | Use Sonnet for bulk work, Opus only for final generation. Cache company research. Track token usage per run. Let users bring own API key (v2). |
| **Pipeline state corruption** | MEDIUM | MEDIUM | Idempotent tasks, status tracking in PostgreSQL, ability to retry individual steps. |
| **Celery/Redis adds operational complexity** | LOW | MEDIUM | For MVP, consider using FastAPI's built-in `BackgroundTasks` instead of Celery. Migrate to Celery when processing more than one run concurrently. |
| **HITL interrupts are complex** | MEDIUM | MEDIUM | Implement as simple database-driven state machine, not framework-level checkpointing. Start without HITL (Phase 4). |
| **Legal risk from scraping** | MEDIUM | LOW | Only scrape publicly accessible pages. Respect robots.txt. Add delays. No login-based scraping. Include disclaimer. |

---

## Scalability Considerations

| Concern | MVP (10 users) | Growth (1K users) | Scale (10K+ users) |
|---------|---------------|--------------------|--------------------|
| **Task processing** | FastAPI BackgroundTasks | Celery + 1 Redis | Celery + multiple workers + Redis Cluster |
| **Database** | Single PostgreSQL | PostgreSQL with read replica | PostgreSQL with partitioning by user_id |
| **File storage** | Local filesystem | S3 / MinIO | S3 with CDN |
| **Scraping** | Sequential, single IP | Rate-limited, single IP | Proxy rotation pool |
| **LLM calls** | Direct API calls | API with retry queue | API with load balancing + fallback models |
| **Progress updates** | SSE via in-process | SSE via Redis pub/sub | SSE via Redis pub/sub + connection pooling |

**Key insight:** Start with the simplest option in each row. The architecture supports upgrading each concern independently because of clean component boundaries.

---

## Sources

- [FastAPI SSE Documentation](https://fastapi.tiangolo.com/tutorial/server-sent-events/) -- HIGH confidence
- [FastAPI + Celery Architecture Guide 2025](https://medium.com/@dewasheesh.rana/celery-redis-fastapi-the-ultimate-2025-production-guide-broker-vs-backend-explained-5b84ef508fa7) -- MEDIUM confidence
- [LangChain HITL Documentation](https://docs.langchain.com/oss/python/langchain/human-in-the-loop) -- HIGH confidence
- [Boss Zhipin Scraping Technical Analysis (CSDN)](https://blog.csdn.net/m0_62074330/article/details/145246276) -- MEDIUM confidence
- [Playwright Scraping Guide 2025](https://www.browserless.io/blog/scraping-with-playwright-a-developer-s-guide-to-scalable-undetectable-data-extraction) -- MEDIUM confidence
- [Python Background Tasks Comparison 2025](https://devproportal.com/languages/python/python-background-tasks-celery-rq-dramatiq-comparison-2025/) -- MEDIUM confidence
- [SSE Streaming for AI Agents](https://akanuragkumar.medium.com/streaming-ai-agents-responses-with-server-sent-events-sse-a-technical-case-study-f3ac855d0755) -- MEDIUM confidence
- [AI Resume Screening Multi-Agent Framework](https://arxiv.org/abs/2504.02870) -- HIGH confidence
- [Web Scraping Rate Limiting Complete Guide 2026](https://www.scrapehero.com/rate-limiting-in-web-scraping/) -- MEDIUM confidence
