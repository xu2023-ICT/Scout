# Domain Pitfalls

**Domain:** AI Job Hunting Agent (Chinese Market)
**Project:** Scout
**Researched:** 2026-04-10

---

## Critical Pitfalls

Mistakes that cause rewrites, user abandonment, or platform bans.

---

### Pitfall 1: Boss Direct Anti-Scraping Arms Race (Scraping)

**What goes wrong:** Boss Direct (Boss直聘) employs a multi-layered anti-scraping system that breaks naive scrapers within minutes. Without login, scraping is capped at ~10 pages before CAPTCHA verification triggers. After 5-6 CAPTCHA encounters, your IP is banned for 24 hours. The site uses short-lived cookies for rendering content, custom font-face (woff) encryption to obfuscate salary/company data in the DOM, and JavaScript-based content rendering that defeats simple HTTP request scrapers.

**Why it happens:** Developers build a working scraper during development with low request volume, then it immediately breaks in production when request volume increases. They also miss the font encryption layer -- the HTML contains encoded characters that only render correctly with the site's custom font files, so scraped text looks like gibberish.

**Consequences:**
- IP bans lock out your server for 24+ hours
- Scraped salary/JD data is garbled due to font encryption
- Users see broken or incomplete job listings
- Constant scraper maintenance as the site updates its defenses

**Warning signs:**
- Scraped text contains Unicode replacement characters or unexpected symbols in salary/number fields
- Request success rate drops below 80%
- CAPTCHAs appear in responses
- Response bodies are empty or contain only skeleton HTML (JS-rendered content missing)

**Prevention:**
1. Use Playwright (not Selenium, not raw HTTP) for browser automation -- it handles JS rendering and is lighter weight
2. Implement font-file interception: download the woff file from each page's `@font-face` declaration, use `fontTools` to build a character mapping table, and decode text post-scraping
3. Enforce strict rate limiting: minimum 3-5 second random delays between requests, never exceed 100 requests/hour from a single IP
4. Build a rotating proxy pool from the start (use Chinese residential proxies, not datacenter IPs)
5. Randomize User-Agent, viewport size, and add mouse movement simulation
6. Cache aggressively -- never re-scrape a JD page that hasn't changed

**Phase:** Must be addressed in the earliest scraping implementation phase. Font decryption and rate limiting are not "nice to have" -- they are prerequisites for any data to flow through the system.

**Confidence:** HIGH (multiple CSDN articles, 52pojie threads, and GitHub projects confirm these specific mechanisms)

---

### Pitfall 2: Shixiseng Custom Font Anti-Scraping (Scraping)

**What goes wrong:** Shixiseng (实习僧) uses custom font-file anti-scraping (similar to Boss直聘 but with its own implementation). The web page renders normally in a browser, but the actual HTML source contains mapped/encrypted characters. Without decoding the font mapping, all extracted text for key fields (salary, company name, location) is corrupted.

**Why it happens:** Developers test by viewing the page visually in a browser and assume the DOM text matches what they see. It does not -- the browser applies the custom font to render the correct glyphs, but the underlying character codes are different.

**Consequences:**
- Extracted job data is partially or fully unreadable
- Developers waste days debugging "encoding issues" when it is actually a font mapping problem

**Warning signs:**
- Extracted text contains characters that look correct in the browser but wrong when printed/logged
- Numbers (salaries, dates) are consistently wrong or contain unexpected characters

**Prevention:**
1. Before writing any scraping code for a new platform, manually inspect the page source (not the rendered DOM) for `@font-face` declarations
2. Download and analyze the font file with `fontTools` (Python) to understand the character mapping
3. Build a per-platform font decoder module that can be updated independently when font files change
4. Monitor for font file URL changes as a signal that the mapping has been rotated

**Phase:** Same phase as Boss直聘 scraping. Build a generic font-decryption utility that works for both platforms.

**Confidence:** MEDIUM (confirmed that 实习僧 uses font-based anti-scraping; specific implementation details less documented than Boss直聘)

---

### Pitfall 3: AI-Generated Resumes That Get Candidates Rejected (AI Quality)

**What goes wrong:** The AI produces resumes that are detectably AI-generated, causing recruiters to reject them. 33.5% of hiring managers can spot an AI-generated resume in under 20 seconds. One in five recruiters (19.6%) will outright reject a candidate whose resume appears AI-generated. The telltale signs: repetitive phrasing across bullet points, overuse of buzzwords like "synergize," "transformative," "pivotal," "realm," "intricate," "showcasing" (Stanford research flagged these specific words), vague accomplishments without metrics, and uniform sentence structure.

**Why it happens:** LLMs default to a "resume voice" learned from training data -- polished, generic, buzzword-heavy. Without explicit constraints, every generated resume sounds identical. The system prompt says "optimize this resume" and the LLM interprets that as "make it sound more impressive" rather than "make it sound like THIS specific person wrote it."

**Consequences:**
- Users submit AI-generated resumes and get rejected, blame the product
- Word spreads that "Scout resumes get you rejected" -- fatal for a job-hunting tool
- Users lose trust and stop using the platform entirely

**Warning signs:**
- Multiple generated resumes for different users share identical phrasing patterns
- Generated bullet points lack specific numbers, percentages, or project names
- Resume language doesn't match the user's apparent experience level (entry-level candidate described as having "expert proficiency")

**Prevention:**
1. **Preserve the user's voice:** Extract writing style markers from the original resume (sentence length, vocabulary level, tone) and instruct the LLM to match them
2. **Ban specific words:** Maintain a blocklist of AI-detectable buzzwords (synergize, transformative, pivotal, realm, intricate, showcasing, leverage, spearheaded) and post-process to flag/replace them
3. **Require specificity:** Prompt engineering must demand concrete metrics, project names, and technologies from the user's actual experience -- never let the LLM invent details
4. **Diff-based output:** Show users exactly what changed from their original resume and why, so they can verify every modification
5. **A/B test with AI detectors:** Run generated resumes through GPTZero or similar tools during QA to ensure they don't trigger detection
6. **Human-in-the-loop review:** Make it easy for users to edit, approve, or reject each change individually

**Phase:** Must be deeply considered when designing the resume generation prompt engineering. This is not a post-launch fix -- the prompt architecture determines output quality.

**Confidence:** HIGH (Gartner survey data, Stanford research, multiple recruiter surveys from 2025)

---

### Pitfall 4: Resume Content Hallucination (AI Quality)

**What goes wrong:** The LLM fabricates skills, experiences, or achievements that the user never had. For example: adding "TensorFlow" to skills when the user only used PyTorch, inventing a "team lead" role when the user was an individual contributor, or generating fake metrics ("improved performance by 40%") with no basis.

**Why it happens:** LLMs are completion machines. When asked to "enhance" a resume for a JD that requires skills the candidate lacks, the model fills the gap by inventing relevant experience rather than acknowledging the gap. This is the fundamental tension: the system is incentivized to maximize JD keyword match, and the easiest way to do that is to fabricate.

**Consequences:**
- User submits resume with fabricated claims, gets caught in interview -- devastating to their career
- Legal liability if the platform knowingly facilitates resume fraud (70% of workers already lie on resumes; an AI tool that automates this is an amplifier)
- Trust destruction -- one viral story of "Scout made up my experience" kills the product

**Warning signs:**
- Generated resume contains skills/technologies not present in original resume or GitHub repos
- Experience bullet points use verbs/claims that don't correspond to any user-provided context
- Generated content passes JD keyword match at >90% (suspiciously high match usually means fabrication)

**Prevention:**
1. **Strict grounding constraint:** The LLM must ONLY use information present in the user's uploaded materials (resume, GitHub, papers). Implement a verification step that cross-references every claim in the generated resume against source materials
2. **Explicit "gap reporting":** When the JD requires skills the user doesn't have, the system should report the gap to the user rather than filling it. "This JD requires Kubernetes experience, which isn't in your materials. Would you like to add relevant experience?"
3. **Separate "rephrase" from "add":** Two distinct operations -- rephrasing existing experience (safe) vs. adding new content (dangerous, requires user confirmation)
4. **Source attribution in output:** Each modified bullet point should cite which source document it drew from
5. **Confidence scoring:** Flag generated content with low source-grounding confidence for user review

**Phase:** Core prompt engineering and output validation pipeline. Must be built into the generation architecture from day one, not bolted on later.

**Confidence:** HIGH (resume fraud is a $600B+ problem per Crosschq research; AI amplification is widely documented)

---

### Pitfall 5: Long-Running Agent Workflows Failing Silently (Agent Reliability)

**What goes wrong:** Scout's core workflow is multi-step and long-running: scrape jobs -> research companies -> analyze JDs -> generate resumes. Research shows that if each step has 85% reliability, a 10-step workflow succeeds only ~20% of the time. Failure rate quadruples when task duration doubles. Steps fail due to: scraping timeouts, API rate limits, LLM context window overflow, network errors, or unexpected data formats. Without checkpointing, a failure at step 8 loses all work from steps 1-7.

**Why it happens:** Developers build each step independently and test in isolation. In isolation, each step works fine. The combinatorial failure probability of the full pipeline is invisible until production. Additionally, long-running LLM calls (30+ seconds each) make the total workflow take 5-15 minutes per job, during which many things can go wrong.

**Consequences:**
- Users click "research job" and get no result 30 minutes later -- no explanation, no partial output
- Wasted API costs on partially-completed workflows that produce nothing
- Users lose trust in the system's reliability

**Warning signs:**
- Background job completion rate drops below 70%
- Users report "stuck" or "processing" states that never resolve
- API cost per completed job is much higher than expected (due to retried/wasted partial runs)

**Prevention:**
1. **Checkpoint after every step:** Persist intermediate results (scraped JD, company research, keyword analysis) to database after each step completes. If a later step fails, resume from the last checkpoint, not from scratch
2. **Design for partial results:** Even if company research fails, the JD analysis and keyword-matched resume should still be deliverable. Degrade gracefully instead of all-or-nothing
3. **Per-step timeouts with circuit breakers:** Each step gets a timeout (e.g., 30s for scraping, 60s for LLM call). If a step fails 3 times, circuit-break and skip it with a user notification
4. **Idempotent step design:** Each step should be safely re-runnable. Use deterministic IDs tied to the job+user, not random UUIDs
5. **Progress reporting:** Show users real-time progress ("Analyzing JD... Researching company... Generating resume...") so they know the system is working
6. **Dead letter queue:** Failed jobs go to a retry queue with exponential backoff, not into a void

**Phase:** Architecture phase. The state management and checkpointing pattern must be the foundation of the agent workflow, not an afterthought.

**Confidence:** HIGH (Amazon's agent evaluation research, Zylos Research on agent checkpointing, and industry consensus all confirm these patterns)

---

### Pitfall 6: Claude API Costs Spiraling Out of Control (Cost)

**What goes wrong:** Each job requires multiple LLM calls: JD analysis, company research synthesis, resume tailoring, interview prep generation. At scale (e.g., 50 jobs x 5 LLM calls x 4K tokens each), costs multiply fast. Without optimization, a single user session researching 20 jobs could cost $5-15 in API calls. With prompt caching disabled or misconfigured, identical system prompts and tool definitions are re-billed on every call.

**Why it happens:** During development, you test with 1-2 jobs and costs seem trivial. The per-job cost is hidden by small-scale testing. Developers also default to the most capable (most expensive) model for every call, even simple classification tasks that a cheaper model handles fine.

**Consequences:**
- Product becomes financially unsustainable before finding product-market fit
- Forced to add paywalls too early, killing growth
- Or forced to degrade quality (shorter prompts, fewer research steps) to cut costs

**Warning signs:**
- Monthly API bill exceeds $100 with fewer than 50 active users
- Average cost per job exceeds $0.50
- Same system prompt text appears in >80% of API calls (caching opportunity missed)

**Prevention:**
1. **Model routing:** Use Claude Haiku for simple tasks (JD keyword extraction, text classification), Sonnet for medium tasks (company research synthesis), and Opus only for complex reasoning (resume tailoring with nuance). This alone can cut costs 60-80%
2. **Prompt caching:** Use Anthropic's `cache_control` parameter to cache system prompts, tool definitions, and shared context. Cached tokens cost 10% of normal input tokens -- a 90% reduction
3. **Batch API for non-real-time work:** Use batch mode for processing multiple jobs simultaneously. Batch API offers 50% cost reduction
4. **Token budgets:** Set `max_tokens` conservatively on each call. A JD analysis needs ~500 tokens output, not 4096
5. **Aggressive result caching:** Cache company research results, JD analyses, and keyword extractions. If two users apply to the same company, don't re-research it
6. **User-provided API key option:** As stated in PROJECT.md constraints, allowing users to bring their own API key offloads cost risk
7. **Cost tracking per operation:** Log token usage per step per job. Monitor and alert on cost anomalies

**Phase:** Must be designed into the architecture from the start. Retrofitting caching and model routing into an existing pipeline is painful.

**Confidence:** HIGH (Anthropic's official documentation confirms caching/batch pricing; multiple production case studies confirm 60-90% cost reduction)

---

## Moderate Pitfalls

---

### Pitfall 7: Chinese PDF Resume Parsing Failures (Resume Parsing)

**What goes wrong:** Chinese-language PDFs have unique parsing challenges that English-focused libraries don't handle well. Common failures include:
- **Embedded custom fonts:** Chinese resumes often use fonts like SimSun, SimHei, or FangSong. If the PDF embeds a subset of the font, extraction libraries may produce garbled output for characters outside the subset
- **Image-based PDFs:** Many Chinese users create resumes from templates that render as images inside the PDF (especially from WPS Office or online template generators). Standard text extraction returns nothing
- **Layout complexity:** Chinese resumes frequently use two-column layouts, tables, and mixed horizontal/vertical text that confuse layout-analysis algorithms
- **Encoding issues:** CJK character encodings (GB2312, GBK, GB18030, UTF-8) may be misdetected, producing mojibake (乱码)

**Why it happens:** Most popular PDF parsing libraries (pdfminer, PyMuPDF) were designed primarily for English/Latin text. Chinese text extraction is a second-class feature with known edge cases. Developers test with their own resume (which works) and miss the variety of formats real users will upload.

**Consequences:**
- AI receives garbled or incomplete resume data, producing poor quality output
- Users with image-based PDFs see "parsing failed" errors and abandon the product
- Subtle parsing errors (wrong characters in skill names) propagate through the entire pipeline

**Warning signs:**
- Parsed text contains `?` or `\ufffd` replacement characters
- Parsed resume has fewer than 100 characters (image-based PDF)
- Skill names don't match known technology terms after parsing

**Prevention:**
1. **Use `pymupdf4llm` as primary parser** -- it has the best balance of speed and quality for CJK text
2. **Add OCR fallback:** When text extraction yields fewer than 100 characters, automatically run OCR using PaddleOCR (superior to Tesseract for Chinese text)
3. **LLM-based structure extraction:** After getting raw text, use Claude to structure it into sections (education, experience, skills) rather than relying on regex patterns. LLMs handle messy formatting far better than rule-based parsers
4. **Support Word (.docx) as primary format:** .docx parsing is dramatically more reliable than PDF. Encourage users to upload Word files when possible
5. **Parsing validation step:** After parsing, show the user the extracted structured data and ask them to confirm/correct before proceeding
6. **Test with 50+ real Chinese resumes** covering different templates, fonts, and creation tools (WPS, Word, LaTeX, online builders)

**Phase:** Early implementation phase. Parsing quality is the foundation -- garbage in, garbage out for the entire downstream pipeline.

**Confidence:** MEDIUM (Chinese PDF parsing issues are well-documented in Chinese tech blogs; specific library recommendations based on 2025 benchmarks)

---

### Pitfall 8: ATS Keyword Optimization That Backfires (AI Quality)

**What goes wrong:** The system over-optimizes for ATS keyword matching, producing resumes that pass automated screening but get rejected by human reviewers. Modern ATS systems (2025+) use semantic NLP analysis, not just keyword counting. They detect and penalize keyword stuffing. A resume matching >85% of JD keywords with forced insertions actually scores LOWER than a natural 70% match.

**Why it happens:** The obvious metric for "resume-JD fit" is keyword overlap percentage. Developers optimize for this metric, and the LLM helpfully stuffs keywords everywhere -- in skills sections, experience descriptions, even the summary. This was effective in 2020 but modern ATS systems have evolved.

**Consequences:**
- Resumes that pass ATS but read poorly to humans -- the candidate gets screened in but immediately screened out
- Resumes that trigger ATS "keyword stuffing" penalties and get auto-rejected
- Users see high "match scores" from your tool but still don't get interviews, eroding trust

**Warning signs:**
- Generated resumes have keyword density >15%
- Skills section contains >20 items (many of which the candidate barely knows)
- Same keyword appears 4+ times across different sections

**Prevention:**
1. **Target 70-80% keyword match**, not 100%. Explicitly cap the optimization
2. **Semantic matching, not string matching:** Use embeddings to match experience descriptions to JD requirements by meaning, not exact keywords
3. **Natural integration only:** Keywords should appear in the context of actual accomplishments ("Built a real-time data pipeline using Apache Kafka") not as standalone insertions
4. **Keyword density monitoring:** Post-process to flag resumes where any keyword appears more than 3 times
5. **Separate "skills I have" from "skills they want":** Show users the gap analysis rather than auto-filling their skills section

**Phase:** Resume generation prompt engineering phase. The optimization target and constraints must be carefully calibrated.

**Confidence:** HIGH (2025 ATS technology reports confirm semantic analysis is standard; keyword stuffing penalties documented)

---

### Pitfall 9: User Trust Erosion Through Opacity (User Trust)

**What goes wrong:** Users don't trust AI-modified resumes because they can't understand what changed and why. They feel loss of control over their own career narrative. Only 26% of job seekers trust AI in the hiring process (Gartner 2025). When the system outputs a "final" resume without explaining its reasoning, users either: (a) submit it blindly and get burned by hallucinated content, or (b) refuse to use it at all.

**Why it happens:** Developers focus on output quality and forget that resumes are deeply personal documents. Unlike AI writing a blog post or email, a resume represents someone's professional identity. Changing it without explanation feels like identity theft, not assistance.

**Consequences:**
- Low adoption even among users who sign up
- Users manually revert all AI changes, making the tool useless
- Negative word-of-mouth: "it changed my resume and I don't even know what it did"

**Warning signs:**
- Users download generated resumes but don't submit them (trackable via follow-up surveys)
- High rate of users reverting to original resume
- Support tickets asking "why did it change X?"

**Prevention:**
1. **Track-changes view:** Show a diff between original and modified resume, with each change annotated with reasoning ("Added 'distributed systems' because it appears 3x in the JD and matches your Kafka project experience")
2. **Per-change approval:** Let users accept/reject individual modifications, not just the whole resume
3. **Confidence indicators:** Mark each change with confidence level (high: direct skill match; medium: inferred from related experience; low: gap -- user should verify)
4. **"Why this change" explanations:** For each modification, provide a one-sentence rationale linking it to the JD analysis
5. **Preview before submit:** Never auto-finalize. Always show the result for review

**Phase:** UI/UX design phase and resume generation output format design. Must be baked into the product flow, not added as a feature later.

**Confidence:** HIGH (Gartner survey data; TopResume hiring survey; universal UX principle)

---

### Pitfall 10: PIPL Compliance Violations with Resume Data (Data Sensitivity)

**What goes wrong:** China's Personal Information Protection Law (PIPL, effective Nov 2021) is the Chinese equivalent of GDPR with even stricter consent requirements. Resume data contains sensitive personal information: name, phone, email, address, education history, employment history, salary expectations. PIPL has no "legitimate interest" exception -- explicit consent is required for ALL processing. Violations carry fines up to RMB 50 million or 5% of annual revenue.

**Why it happens:** Solo developers building MVPs skip compliance because "it's just a side project." But PIPL applies to any entity processing Chinese citizens' personal information, regardless of scale. Sending resume content to Anthropic's API (servers outside China) constitutes cross-border data transfer, which has additional requirements under PIPL.

**Consequences:**
- Legal liability even for a small product
- Users' personal data exposed if there's a breach with no incident response plan
- Cross-border data transfer (to Claude API) without proper safeguards violates PIPL Articles 38-43

**Warning signs:**
- No privacy policy or user consent mechanism in the product
- Resume data stored in plaintext without encryption
- No data retention policy (resumes stored indefinitely)
- API calls to Claude include full resume text without user being informed that data leaves China

**Prevention:**
1. **Explicit consent flow:** Before processing any resume, get clear user consent explaining: what data is collected, how it's processed, that it will be sent to overseas AI APIs, and retention period
2. **Data minimization:** Don't send the entire resume to Claude for every API call. Extract only the relevant sections needed for each specific task
3. **Retention policy:** Auto-delete resume data after a defined period (e.g., 30 days after last activity). Let users delete their data immediately on request
4. **Encryption at rest and in transit:** Encrypt stored resumes. Use HTTPS for all API calls (this is standard but must be verified)
5. **Privacy policy page:** Even for MVP, have a clear privacy policy explaining data handling in Chinese
6. **Inform users about cross-border transfer:** Be transparent that resume data is sent to AI services hosted outside China. This is a PIPL requirement, not optional

**Phase:** Must be addressed before any user-facing launch, even for beta/MVP. Legal compliance is not a "v2 feature."

**Confidence:** HIGH (PIPL is well-documented law; cross-border transfer requirements are explicit in the statute)

---

## Minor Pitfalls

---

### Pitfall 11: Scraper Structure Breakage After Platform Updates (Scraping)

**What goes wrong:** Job platforms update their HTML structure, CSS class names, and API endpoints regularly. A scraper that works today breaks next week when Boss直聘 renames a CSS class or restructures their job listing page.

**Prevention:**
1. Use semantic selectors (ARIA labels, data attributes) over brittle CSS class selectors
2. Build a scraper health monitor that runs daily test scrapes against known pages and alerts on failures
3. Isolate scraping logic into a thin adapter layer so fixes don't require touching business logic
4. Consider using the platforms' mobile web versions or API endpoints (often more stable than desktop HTML)

**Phase:** Scraping implementation phase. Design the adapter pattern from the start.

---

### Pitfall 12: GitHub Repo Analysis Overengineering (Feature Scope)

**What goes wrong:** Developers spend weeks building sophisticated GitHub analysis (code quality metrics, commit frequency analysis, language statistics) when a simpler approach would suffice. The GitHub API has rate limits (60 requests/hour unauthenticated, 5000/hour authenticated) that constrain what's practical anyway.

**Prevention:**
1. Start with README + repo description + language breakdown + star count. This covers 80% of the value
2. Use GitHub's REST API, not scraping, to avoid anti-bot issues
3. Authenticate with a GitHub token to get the higher rate limit
4. Cache results -- a user's GitHub profile doesn't change hourly

**Phase:** Feature implementation phase. Keep it simple initially and iterate based on user feedback.

---

### Pitfall 13: Interview Prep Content Based on Outdated Miangjing (Feature Quality)

**What goes wrong:** The system scrapes interview experiences (面经) from Nowcoder (牛客) that may be months or years old. Interview questions, processes, and team structures change. Users prepare based on outdated information and feel misled.

**Prevention:**
1. Always display the date of each interview experience source
2. Prioritize recent (last 6 months) experiences and flag older ones
3. Use interview experiences as a starting framework, not the definitive guide
4. Clearly label generated interview prep as "based on historical data, may not reflect current process"

**Phase:** Interview prep feature phase. A metadata/freshness indicator is essential.

---

### Pitfall 14: LLM Context Window Overflow on Long JDs and Resumes (Agent Reliability)

**What goes wrong:** Combining a full resume + full JD + company research + system prompts + interview data exceeds the context window, causing truncation of important information or API errors. Even with large context models, stuffing everything in degrades output quality.

**Prevention:**
1. Summarize/chunk inputs: extract key sections from long JDs and company research before feeding to the LLM
2. Use a pipeline approach: separate calls for analysis vs. generation, passing only relevant findings forward
3. Track token counts before API calls and truncate intelligently (not just cutting off the end)
4. For very long inputs, use a map-reduce pattern: analyze sections independently, then synthesize

**Phase:** Agent pipeline architecture phase.

---

### Pitfall 15: LinkedIn/HR Profile Scraping Legal and Technical Risk (Scraping)

**What goes wrong:** The PROJECT.md mentions scraping HR/recruiter LinkedIn profiles. LinkedIn aggressively litigates against scrapers (hiQ Labs v. LinkedIn went to the Supreme Court). LinkedIn's anti-bot detection is among the most sophisticated, and scraping it from China adds network reliability issues on top of legal risk.

**Prevention:**
1. **Drop LinkedIn scraping from MVP entirely.** The legal risk is disproportionate to the value for a solo-developer project
2. Instead, use publicly available information from company career pages, tech blogs, and Chinese platforms (脉脉, if accessible)
3. If company/team research is needed, use search APIs (Google/Bing/Baidu) to find public articles, not profile scraping

**Phase:** Scope decision before implementation begins. This should be moved to "Out of Scope" for v1.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation | Severity |
|-------------|---------------|------------|----------|
| Scraping infrastructure | IP bans, font encryption, structure changes | Proxy pool, font decoder, adapter pattern, rate limits | Critical |
| Resume parsing | Chinese PDF failures, image PDFs, encoding | pymupdf4llm + PaddleOCR fallback, validation step | Critical |
| Agent workflow architecture | Silent failures, no checkpointing, context overflow | Step-based state machine with DB persistence | Critical |
| Resume generation prompts | Hallucination, keyword stuffing, detectable AI voice | Grounding constraints, blocklists, diff-based output | Critical |
| Cost management | API costs spiraling | Model routing, prompt caching, token budgets | Moderate |
| User trust / UX | Opacity, loss of control | Track-changes view, per-change approval | Moderate |
| Data compliance | PIPL violations, cross-border transfer | Consent flow, encryption, retention policy | Moderate |
| GitHub/company research | Overengineering, rate limits | Start simple, cache aggressively, use APIs | Low |
| Interview prep | Outdated information | Date labeling, freshness filtering | Low |
| LinkedIn scraping | Legal risk, technical difficulty | Remove from v1 scope | Low (if removed) |

---

## Sources

**Scraping (Boss直聘/实习僧):**
- [Boss直聘反爬解决办法 - CSDN](https://blog.csdn.net/m0_62074330/article/details/145246276)
- [Boss直聘反反爬机制详解 - CSDN](https://blog.csdn.net/jmfang/article/details/105760928)
- [BOSS直聘的反爬机制 - 52pojie](https://www.52pojie.cn/thread-1641725-1-1.html)
- [字体反爬详解 - 静觅](https://cuiqingcai.com/6431.html)
- [State of Web Scraping 2026 - Browserless](https://www.browserless.io/blog/state-of-web-scraping-2026)

**AI Quality / Resume Fraud:**
- [Common Mistakes AI Job Apply Tools Make - Scale.jobs](https://scale.jobs/blog/common-mistakes-ai-job-apply-tools)
- [7 Signs Recruiters Know Your Resume Was AI-Written - Scale.jobs](https://scale.jobs/blog/signs-recruiters-know-resume-ai-written)
- [AI and the Rise of Resume Fraud - NPAworldwide](https://npaworldwide.com/blog/2025/05/16/ai-and-the-rise-of-resume-fraud/)
- [Resume Fraud: The $600 Billion Crisis - Crosschq](https://www.crosschq.com/blog/resume-fraud-the-600-billion-crisis-transforming-how-organizations-verify-talent-in-2025)

**ATS / Keyword Stuffing:**
- [ATS Resume Optimization 2025 - Interview Guys](https://blog.theinterviewguys.com/ats-resume-optimization/)
- [How to Pass ATS in 2026 - ResumeAdapter](https://www.resumeadapter.com/blog/ats-compatibility-what-it-means-and-how-to-pass-in-2025)
- [Mastering Resume Keywords Without Stuffing - Scion Staffing](https://scionstaffing.com/mastering-resume-without-keyword-stuffing/)

**User Trust:**
- [Gartner: 26% of Job Applicants Trust AI](https://www.gartner.com/en/newsroom/press-releases/2025-07-31-gartner-survey-shows-just-26-percent-of-job-applicants-trust-ai-will-fairly-evaluate-them)
- [AI in Hiring: The Growing Trust Gap - UNLEASH](https://www.unleash.ai/talent-acquisition/ai-in-hiring-the-growing-trust-gap-between-employers-and-job-candidates/)

**Agent Reliability:**
- [Long-Running AI Agents - Zylos Research](https://zylos.ai/research/2026-01-16-long-running-ai-agents)
- [AI Agent Workflow Checkpointing - Zylos Research](https://zylos.ai/research/2026-03-04-ai-agent-workflow-checkpointing-resumability)
- [Error Recovery in AI Agent Development - GoCodeo](https://www.gocodeo.com/post/error-recovery-and-fallback-strategies-in-ai-agent-development)
- [Evaluating AI Agents at Amazon - AWS](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/)

**Cost Optimization:**
- [Claude API Cost Optimization - DEV Community](https://dev.to/whoffagents/claude-api-cost-optimization-caching-batching-and-60-token-reduction-in-production-3n49)
- [Reduced LLM Token Costs by 90% - Medium](https://medium.com/@ravityuval/how-i-reduced-llm-token-costs-by-90-using-prompt-rag-and-ai-agent-optimization-f64bd1b56d9f)
- [Anthropic API Pricing Guide - Finout](https://www.finout.io/blog/anthropic-api-pricing)

**Data Privacy (PIPL):**
- [China PIPL Compliance Guide - China Briefing](https://www.china-briefing.com/doing-business-guide/china/company-establishment/pipl-personal-information-protection-law)
- [China's PIPL - Bloomberg Law](https://pro.bloomberglaw.com/insights/privacy/china-personal-information-protection-law-pipl-faqs/)
- [China Data Privacy Laws 2026 - Recording Law](https://www.recordinglaw.com/world-laws/world-data-privacy-laws/china-data-privacy-laws/)

**Resume Parsing:**
- [7 Python PDF Extractors Tested 2025 - DEV Community](https://dev.to/onlyoneaman/i-tested-7-python-pdf-extractors-so-you-dont-have-to-2025-edition-akm)
- [简历信息提取 PDFPlumber和PP-Structure - 知乎](https://zhuanlan.zhihu.com/p/430964415)
