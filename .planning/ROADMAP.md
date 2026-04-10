# Roadmap: Scout

**Phases:** 5
**Total v1 Requirements:** 27
**Granularity:** Standard
**Created:** 2026-04-10

## Phases

- [ ] **Phase 1: Core Vertical Slice** - Upload resume, provide Boss直聘 URL, scrape JD with font decryption, generate tailored resume
- [ ] **Phase 2: Autonomous Job Search** - System proactively searches Boss直聘 and 实习僧 based on user profile preferences
- [ ] **Phase 3: Deep Research** - Per-job company research, interview scraping from 牛客网 + 小红书, cross-JD keyword analysis, interview talking points
- [ ] **Phase 4: Generation Quality & Materials** - Diff view, ATS optimization, AI quality controls, supplementary materials, PDF/Word export
- [ ] **Phase 5: Job Management & UX** - Filtering, match scores, kanban board, SSE real-time progress streaming

## Phase Details

### Phase 1: Core Vertical Slice
**Goal**: User uploads a resume, provides a Boss直聘 job URL, and the system scrapes the JD (including font decryption), then generates a tailored resume for that specific position
**Depends on**: Nothing (first phase)
**Requirements**: RESUME-01, RESUME-02, RESUME-03, SCRAPE-01, SCRAPE-04, AI-01, AI-02
**Success Criteria** (what must be TRUE):
  1. User can upload a PDF or Word resume and see the parsed structure (work experience, skills, education) displayed on screen
  2. User can edit the parsed resume structure to correct any errors before processing
  3. User can paste a Boss直聘 job URL and the system extracts the full JD text, including decrypting Boss直聘's custom font encoding
  4. When scraping fails, the system shows the error reason and lets the user paste the JD text manually as a fallback
  5. User receives a generated resume tailored to the specific JD, preserving their original writing style, with zero fabricated skills or experiences
**Plans**: TBD
**UI hint**: yes

### Phase 2: Autonomous Job Search
**Goal**: System proactively searches Boss直聘 and 实习僧 for matching positions based on user-configured search preferences, without the user needing to manually find jobs
**Depends on**: Phase 1
**Requirements**: SCRAPE-02, SCRAPE-03, SCRAPE-05, JOBS-01
**Success Criteria** (what must be TRUE):
  1. User can configure search preferences (city, job type, industry) and the system automatically searches Boss直聘 for matching positions
  2. System automatically searches 实习僧 for matching positions using the same user preferences
  3. User can view all discovered jobs in a dashboard list with key details (title, company, location, salary)
**Plans**: TBD
**UI hint**: yes

### Phase 3: Deep Research
**Goal**: For each job, the system automatically researches the company, scrapes real interview experiences from 牛客网 and 小红书, analyzes keyword frequency across similar JDs, and generates personalized interview talking points
**Depends on**: Phase 2
**Requirements**: RESEARCH-01, RESEARCH-02, RESEARCH-03, RESEARCH-04, RESEARCH-05
**Success Criteria** (what must be TRUE):
  1. User can view a per-job company research report covering funding, product news, tech blog, and culture
  2. User can see real interview questions and process details scraped from 牛客网 for the target company/role
  3. User can see real interview experience posts scraped from 小红书 for the target company/role
  4. User can view a keyword frequency analysis aggregated from 10+ similar JDs (e.g., "React appears in 90% of similar JDs")
  5. User receives a personalized interview script (self-introduction + common question answer frameworks) grounded in real interview data and company research
**Plans**: TBD

### Phase 4: Generation Quality & Materials
**Goal**: Users get diff-based transparency into AI edits, ATS-optimized output, AI quality safeguards, support for supplementary materials (papers/GitHub), and PDF/Word export
**Depends on**: Phase 1
**Requirements**: AI-03, AI-04, AI-05, AI-06, RESUME-04, RESUME-05, RESUME-06
**Success Criteria** (what must be TRUE):
  1. User can view a diff showing exactly what the AI changed and why for each modification
  2. Generated resume achieves 70-80% keyword density via semantic matching without keyword stuffing, and avoids detectable AI-characteristic vocabulary
  3. When the AI lacks sufficient information, it pauses and prompts the user to supply specifics before continuing generation
  4. User can upload supplementary materials (papers, GitHub links), see extracted metadata (key contributions, journal, etc.), and export the final tailored resume as PDF or Word
**Plans**: TBD
**UI hint**: yes

### Phase 5: Job Management & UX
**Goal**: Users can filter, score, and manage jobs through a kanban board with real-time SSE progress streaming for agent operations
**Depends on**: Phase 2, Phase 3
**Requirements**: JOBS-02, JOBS-03, JOBS-04, JOBS-05
**Success Criteria** (what must be TRUE):
  1. User can filter jobs by city, salary, company size, and industry
  2. Each job displays a match score reflecting how well it fits the user's profile
  3. User can drag jobs across a kanban board (Discovered -> Researched -> Generated -> Applied) to manage application status
  4. User can see real-time agent work progress via SSE streaming, with each step's status updating live
**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Vertical Slice | 0/? | Not started | - |
| 2. Autonomous Job Search | 0/? | Not started | - |
| 3. Deep Research | 0/? | Not started | - |
| 4. Generation Quality & Materials | 0/? | Not started | - |
| 5. Job Management & UX | 0/? | Not started | - |

---
*Roadmap created: 2026-04-10*
*Last updated: 2026-04-10*
