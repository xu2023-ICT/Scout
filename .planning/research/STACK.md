# Stack Research -- Scout (AI Job Hunting Agent)

**Researched:** 2026-04-10
**Mode:** Ecosystem
**Overall confidence:** HIGH

---

## Recommended Stack

### Backend: Python + FastAPI

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.12 or 3.13 | Runtime | Industry standard for AI/ML/scraping. Massive ecosystem. Solo dev with limited coding experience will find Python the most forgiving and well-documented language. |
| FastAPI | 0.135.x | Web framework & API layer | Async-native, auto-generates OpenAPI docs, excellent type hints with Pydantic, fastest Python web framework. Learning curve is minimal -- route decorators feel intuitive. |
| Uvicorn | latest | ASGI server | Default server for FastAPI. Production-ready with `--workers` flag. |
| Pydantic | v2 (bundled with FastAPI) | Data validation & serialization | Already required by FastAPI. Use for all data models (resume schemas, job listings, API responses). |
| python-multipart | latest | File upload handling | Required by FastAPI for resume PDF/Word uploads. |

**Why Python over Node.js:**
- The entire AI/scraping ecosystem is Python-first: Anthropic SDK, Crawl4AI, Playwright, BeautifulSoup, PDF parsing libraries -- all have their best implementations in Python.
- Claude will be assisting with coding; Python is Claude's strongest language for AI agent patterns.
- For a solo dev who is a research grad student, Python's readability and "one obvious way to do it" philosophy reduces cognitive overhead.
- Node.js would require constant context-switching between Python AI tools and a JS backend. Not worth it.

**Confidence:** HIGH -- Python + FastAPI is the dominant stack for AI-powered backends in 2025-2026. FastAPI has 80k+ GitHub stars and is the fastest-growing Python web framework.

---

### Frontend: Vue 3 + Vite + shadcn-vue

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Vue 3 | 3.5.x | UI framework | Gentlest learning curve among major frameworks. Template syntax feels like HTML. Perfect for a solo dev with limited frontend experience. |
| Vite | 7.x or 8.x | Build tool & dev server | Default bundler for Vue ecosystem. Instant HMR, near-zero config. |
| shadcn-vue | latest | UI component library | Beautiful, accessible components out of the box. Copy-paste model means you own the code. Dashboard examples available. |
| Tailwind CSS | 4.x | Utility CSS | Bundled with shadcn-vue. No need to write custom CSS for 90% of the UI. |
| Pinia | latest | State management | Official Vue state manager. Simple, type-safe, intuitive. |
| Vue Router | latest | Routing | Official router. File-based routing with unplugin-vue-router if desired. |
| TypeScript | 5.x | Type safety | Vue 3 has first-class TS support. Catches bugs early. Optional but recommended. |

**Why Vue over React/Next.js:**
- Vue's learning curve is significantly lower than React's. For a solo dev building a dashboard, Vue gets you to "working UI" faster.
- No need for SSR/SSG (this is a dashboard app, not a content site), so Next.js's killer features are irrelevant.
- shadcn-vue provides dashboard templates nearly identical to shadcn/ui (React), so no loss in component quality.
- Vue Vben Admin (31k+ stars) provides a production-ready dashboard scaffold with Vue 3 + shadcn-vue if you want a head start.

**Why not plain HTML/JS or Streamlit:**
- Streamlit is tempting for prototyping but hits a wall fast: no custom layouts, no real routing, no component reuse. You'd rewrite it.
- Plain HTML/JS lacks component architecture. A job tracking dashboard with multiple views needs it.

**Confidence:** HIGH -- Vue 3 is mature, well-documented, and objectively easier to learn for beginners than React.

---

### AI & Agent Orchestration: Anthropic Python SDK (Direct) + Custom Agent Loop

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| anthropic (Python SDK) | ~0.92.x | Claude API access | Official SDK. Handles auth, streaming, tool use, retries. Direct and well-documented. |
| Custom agentic loop | N/A | Multi-step agent orchestration | Write a simple while-loop that calls Claude with tools, executes tool results, feeds back. 100-200 lines of code. Full control, no framework overhead. |

**Why NOT LangChain / LangGraph:**
- LangChain introduces a massive abstraction layer (Chains, Runnables, LCEL) that a solo dev must learn on top of Python, FastAPI, and everything else. Its learning curve is steep and its abstractions are leaky.
- LangGraph adds even more complexity for stateful agent graphs. Scout's workflow is sequential (search -> scrape -> analyze -> generate), not a complex graph.
- For this project's agent pattern (sequential multi-step with tool use), Claude's native tool-use API is sufficient and far simpler.

**Why NOT Claude Agent SDK (claude-agent-sdk):**
- The Agent SDK bundles Claude Code and is designed for code-editing agents (file read/write, bash execution). It's overkill for a web backend that needs to call search APIs and scrape websites.
- It requires Claude Code CLI bundled in. Unnecessary dependency for a web service.
- The raw `anthropic` SDK gives you tool use, streaming, and everything you need with zero extra baggage.

**Why NOT PydanticAI:**
- PydanticAI (15k stars) is a solid framework, but it's yet another abstraction. For a solo dev, directly using the `anthropic` SDK means one less layer to debug. The project's agent needs are simple enough that a framework adds overhead without proportional benefit.

**Agent pattern (recommended):**
```python
# Pseudocode -- the actual agent loop is ~100 lines
async def run_agent(task, tools):
    messages = [{"role": "user", "content": task}]
    while True:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            tools=tools,
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            return extract_text(response)
        # Execute tool calls, append results, continue loop
        messages = append_tool_results(messages, response)
```

**Confidence:** HIGH -- Anthropic's own documentation recommends this pattern for tool-use agents. The Claude Agent SDK is explicitly for Claude Code-style agents, not web backends.

---

### Web Scraping: Crawl4AI + Playwright (fallback)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Crawl4AI | 0.8.x | Primary web scraper | LLM-optimized output (clean markdown/JSON). Built on Playwright internally. Anti-bot stealth mode, async, handles JS-rendered pages. 51k+ GitHub stars, most popular AI-focused crawler. |
| Playwright | 1.58.x | Fallback / complex interactions | When Crawl4AI can't handle a specific page (e.g., complex JS interactions on Boss zhipin), drop down to raw Playwright for fine-grained control. |
| playwright-stealth | latest | Anti-detection | Patches Playwright to evade basic bot detection (navigator.webdriver, headless fingerprints). Important for Chinese job platforms. |
| BeautifulSoup4 | 4.x | HTML parsing helper | For quick parsing of already-fetched HTML when Crawl4AI's extraction is insufficient. Lightweight, no browser needed. |

**Why Crawl4AI over raw Playwright/Scrapy:**
- Crawl4AI outputs LLM-ready markdown and structured JSON. Since Scout feeds scraped content directly to Claude for analysis, this eliminates a manual HTML-to-text conversion step.
- It wraps Playwright internally, so you get browser automation without writing low-level browser scripts.
- Anti-bot features (stealth mode, proxy support, random delays) are built in.
- Scrapy is powerful but designed for large-scale distributed crawling. Scout scrapes tens of pages per session, not millions. Scrapy's learning curve and infrastructure overhead (Scrapy Cloud, middleware pipelines) are not justified.

**Boss zhipin / Shixiseng scraping notes:**
- These platforms serve JD pages publicly without login. Standard HTTP requests with proper headers may suffice for basic pages.
- If they use heavy JS rendering or anti-bot measures, Crawl4AI with stealth mode handles it.
- Rate limiting is critical: add 2-5 second random delays between requests, rotate User-Agent strings, consider residential proxies if IPs get blocked.

**Confidence:** HIGH -- Crawl4AI is the most-starred open-source crawler in 2025-2026 and is specifically designed for AI agent workflows.

---

### Search APIs: Tavily

| Technology | Tier | Purpose | Why |
|------------|------|---------|-----|
| Tavily Search API | Free (1,000 credits/month) | Company research, news, web search | Built specifically for AI agents. Returns clean, extracted content (not just URLs). Single API call does search + scrape + extract. Free tier is generous for a student project. |

**Why Tavily over SerpAPI / Bing Search:**
- SerpAPI returns raw Google SERP data (URLs + snippets). You'd need to separately fetch and parse each URL. Tavily does this in one call.
- SerpAPI's free tier is only 100 searches/month vs Tavily's 1,000.
- Bing Search API requires Azure account setup and is more complex to configure.
- Tavily's Python SDK (`tavily-python`) integrates cleanly and returns structured content ready for Claude analysis.

**Cost control:**
- Free tier: 1,000 credits/month (1 credit = 1 basic search).
- For development and low-volume usage, this is sufficient. One "deep research" per job posting might use 3-5 searches (company info, team info, interview experiences).
- If scaling beyond free tier: $30/month for 10,000 credits.

**Confidence:** HIGH -- Tavily is the de facto search API for AI agents in 2025-2026, recommended by Anthropic's own cookbooks and LangChain documentation.

---

### Database: SQLite (start) -> PostgreSQL (if needed)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| SQLite | 3.x (bundled with Python) | Primary database | Zero setup, single-file, no server process. Perfect for solo dev / student project. Handles Scout's concurrency needs (single user, sequential writes). |
| SQLAlchemy | 2.x | ORM | Industry-standard Python ORM. Supports both SQLite and PostgreSQL with the same models. Makes future migration painless. |
| Alembic | latest | Database migrations | Works with SQLAlchemy. Tracks schema changes over time. |

**Why SQLite over PostgreSQL:**
- Scout is a single-user or low-concurrency application (the developer and a few test users). SQLite handles this perfectly.
- Zero infrastructure: no Docker, no database server, no connection strings. The database is a single file.
- SQLAlchemy abstracts the database engine. If Scout grows beyond SQLite's limits (concurrent writes from multiple users), switch to PostgreSQL by changing one connection string.

**Why NOT MongoDB / Supabase / Firebase:**
- MongoDB: Document databases add complexity for relational data (users -> resumes -> jobs -> generated content). SQL is more natural here.
- Supabase/Firebase: External dependencies for a student project. SQLite keeps everything local and free.

**When to migrate to PostgreSQL:**
- When you have multiple concurrent users writing simultaneously.
- When you deploy to a platform that doesn't support persistent filesystem (some serverless platforms).
- The migration path via SQLAlchemy + Alembic is straightforward.

**Confidence:** HIGH -- SQLite is the correct starting database for solo-dev projects. This is well-established wisdom.

---

### File Handling & Document Parsing

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| PyMuPDF (fitz) | latest | PDF text extraction | Fastest Python PDF parser. Handles both text-based and scanned PDFs (with OCR fallback). |
| python-docx | latest | Word document parsing | Standard library for .docx file reading. |
| httpx | latest | Async HTTP client | For API calls to Tavily, GitHub API, etc. Async-native, pairs well with FastAPI. |

**Confidence:** HIGH -- These are the standard, well-maintained libraries for their respective tasks.

---

### Deployment: Railway or Render

| Technology | Tier | Purpose | Why |
|------------|------|---------|-----|
| Railway | Hobby ($5/month) | Backend + database hosting | One-click deploy from GitHub. Managed PostgreSQL available when needed. Simple container deployment. Good DX. |
| Render | Free / Starter | Alternative to Railway | Free tier for web services (spins down after inactivity). Good for initial prototyping. |
| Vercel | Free | Frontend hosting | Excellent free tier for static sites / SPAs. Vue 3 + Vite deploys in seconds. |

**Recommended deployment architecture:**
- Frontend (Vue 3 SPA) -> Vercel (free)
- Backend (FastAPI) -> Railway ($5/month) or Render (free tier)
- Database: SQLite file on Railway/Render persistent storage, or upgrade to Railway's managed PostgreSQL

**Why NOT Docker / AWS / self-hosting:**
- Docker adds DevOps complexity that a solo dev student doesn't need.
- AWS is powerful but overwhelming for a first project. Railway/Render abstract away infrastructure.
- Self-hosting requires server management. Not worth it for validation.

**Confidence:** MEDIUM -- Deployment landscape changes frequently. Railway and Render are solid choices today but verify current pricing before deploying.

---

## Installation Summary

```bash
# Create project and virtual environment
mkdir scout && cd scout
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Core backend
pip install fastapi uvicorn[standard] python-multipart

# AI
pip install anthropic

# Web scraping
pip install crawl4ai playwright playwright-stealth beautifulsoup4
playwright install chromium

# Search API
pip install tavily-python

# Database
pip install sqlalchemy alembic

# Document parsing
pip install PyMuPDF python-docx

# HTTP client
pip install httpx

# Dev tools
pip install ruff pytest pytest-asyncio

# Frontend (separate directory)
npm create vue@latest scout-frontend -- --template vue-ts
cd scout-frontend
npx shadcn-vue@latest init
npm install pinia
```

---

## What NOT to Use

| Technology | Why Avoid |
|------------|-----------|
| **LangChain** | Massive abstraction overhead. Learning LCEL/Chains/Runnables is a project in itself. Scout's agent is a simple sequential loop -- LangChain adds complexity without proportional value. |
| **LangGraph** | Designed for complex multi-agent state machines. Scout has one agent doing sequential steps. Overkill. |
| **Claude Agent SDK** | Bundles Claude Code CLI. Designed for code-editing agents, not web service backends. Wrong tool for this job. |
| **Streamlit** | Tempting for quick prototyping but impossible to build a real dashboard with routing, custom layouts, and component reuse. You will rewrite it. |
| **Scrapy** | Designed for large-scale distributed crawling (millions of pages). Scout scrapes tens of pages per session. Scrapy's middleware pipeline and project structure add unnecessary complexity. |
| **Django** | Full-featured but heavy. Includes ORM, admin panel, template engine, auth system. FastAPI is lighter, faster, and more modern for API-first applications. |
| **MongoDB** | Scout's data is inherently relational (users -> resumes -> jobs -> generated content). SQL databases model this naturally. MongoDB would require manual denormalization or embedding. |
| **Selenium** | Legacy browser automation. Playwright is faster, more reliable, has better API, and is actively maintained by Microsoft. Selenium is the old way. |
| **Flask** | No async support, no auto-generated docs, no built-in validation. FastAPI does everything Flask does, better. |
| **React / Next.js** | Steeper learning curve than Vue for a solo dev with limited frontend experience. Next.js's SSR/SSG features are unnecessary for a dashboard SPA. |
| **Supabase / Firebase** | External dependency and vendor lock-in for a student project. SQLite keeps everything local, free, and simple. |

---

## Confidence Summary

| Area | Confidence | Rationale |
|------|------------|-----------|
| Backend (Python + FastAPI) | HIGH | Dominant AI backend stack. Verified via multiple sources, official documentation, and ecosystem evidence. |
| Frontend (Vue 3 + shadcn-vue) | HIGH | Vue's lower learning curve is well-documented. shadcn-vue is actively maintained with dashboard templates. |
| AI orchestration (raw anthropic SDK) | HIGH | Anthropic's official docs recommend this pattern. Agent SDK is explicitly for Claude Code agents, not web backends. |
| Web scraping (Crawl4AI) | HIGH | 51k+ stars, actively maintained (v0.8.6 March 2026), specifically designed for AI agent scraping. |
| Search API (Tavily) | HIGH | De facto AI agent search API. 1,000 free credits/month is generous. Verified pricing and SDK availability. |
| Database (SQLite + SQLAlchemy) | HIGH | Standard recommendation for solo dev projects. Migration path to PostgreSQL is well-documented. |
| Document parsing (PyMuPDF) | HIGH | Fastest Python PDF parser. Well-maintained, widely used. |
| Deployment (Railway/Render) | MEDIUM | Solid choices today but deployment platforms evolve quickly. Verify pricing before deploying. |

---

## Sources

- [FastAPI official documentation](https://fastapi.tiangolo.com/)
- [FastAPI PyPI - v0.135.3](https://pypi.org/project/fastapi/)
- [Crawl4AI documentation (v0.8.x)](https://docs.crawl4ai.com/)
- [Crawl4AI PyPI](https://pypi.org/project/Crawl4AI/)
- [Anthropic Python SDK PyPI](https://pypi.org/project/anthropic/)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Claude tool use tutorial](https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent)
- [Tavily pricing](https://www.tavily.com/pricing)
- [Tavily Python SDK](https://github.com/tavily-ai/tavily-python)
- [Playwright Python PyPI - v1.58.0](https://pypi.org/project/playwright/)
- [Vue 3 official site](https://vuejs.org/)
- [shadcn-vue dashboard examples](https://shadcn-vue.com/examples/dashboard)
- [Vue Vben Admin (31k+ stars)](https://allshadcn.com/templates/vue-vben/)
- [SQLite vs PostgreSQL comparison - DataCamp](https://www.datacamp.com/blog/sqlite-vs-postgresql-detailed-comparison)
- [PydanticAI vs LangChain comparison](https://vstorm.co/open-source/pydantic-deep-agents-vs-langchain-deep-agents-which-python-ai-agent-framework-should-you-choose/)
- [SERP API comparison 2025](https://dev.to/ritza/best-serp-api-comparison-2025-serpapi-vs-exa-vs-tavily-vs-scrapingdog-vs-scrapingbee-2jci)
- [Railway deployment guide](https://docs.railway.com/guides/fastapi)
- [Vercel FastAPI support](https://vercel.com/docs/frameworks/backend/fastapi)
