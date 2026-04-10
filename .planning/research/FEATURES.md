# Feature Landscape

**Domain:** AI-Powered Autonomous Job Hunting Agent (Scout)
**Researched:** 2026-04-10
**Target Users:** Chinese job seekers, especially students and fresh graduates (应届生)

---

## Competitive Landscape Summary

The AI resume/job search market in 2025-2026 clusters into four tiers:

1. **Resume Builders** (Rezi, Kickresume, Resume.io, WonderCV/超级简历): Template + AI writing. User pastes JD, gets optimized resume. No search, no research.
2. **JD Matchers** (Jobscan, Teal, Reztune): Analyze keyword alignment between resume and JD. Score-based. Still requires user to find and paste JDs.
3. **Auto-Apply Bots** (LazyApply, LoopCV, Sonara, JobCopilot): Mass-apply to jobs automatically. High quantity, low quality. 1-3% callback rates. Frequently trigger bot detection.
4. **Copilots** (Jobright, Careerflow, Teal): Job tracking + resume tailoring + application management. More holistic but still reactive -- user does the searching.

**Nobody occupies Scout's position:** proactive search + deep company/role research + interview-prep content generation. This is a genuine gap.

---

## Table Stakes

Features users expect. Missing any of these = product feels broken or untrustworthy.

| # | Feature | Why Expected | Complexity | Dependencies | Notes |
|---|---------|--------------|------------|--------------|-------|
| T1 | **Resume upload & parsing** | Every tool does this. Users won't re-type their info. | Medium | None (entry point) | Must handle PDF + Word. Chinese resumes have different section conventions (政治面貌, 籍贯 etc). Use LLM extraction, not regex. |
| T2 | **Resume structure display** | Users need to see what the system "understood" from their resume. Builds trust. | Low | T1 | Editable parsed fields. Show skills, education, experience as structured cards. |
| T3 | **JD keyword extraction & matching** | Jobscan, Teal, Rezi all do this. Users know to expect match scores. | Medium | None | Extract hard skills, soft skills, tools, certifications. Show match % against user's profile. |
| T4 | **ATS-friendly resume output** | 62% of employers reject non-ATS-optimized resumes. Users actively seek ATS compliance. | Medium | T1 | Single-column, standard headers, .docx output, no graphics/tables/icons. Reverse chronological. Fonts: Arial/Calibri 10-12pt. |
| T5 | **Per-job tailored resume generation** | This is the core promise. Every competitor at least claims JD-based tailoring. | High | T1, T3 | Must go beyond keyword stuffing. Rewrite bullet points to reflect JD priorities. Maintain truthfulness -- never fabricate experience. |
| T6 | **Job listing display with filtering** | Users need to browse, filter, and select which jobs to pursue. Standard UX. | Medium | Job search engine | Filter by: city, salary range, company size, industry, job type. Sort by match score. |
| T7 | **User account & data persistence** | Users expect to come back and see their history. | Medium | None | Auth, profile storage, resume versions, job application history. |
| T8 | **Chinese language support (full)** | Target market is Chinese job seekers. UI, resume output, JD parsing all must be native Chinese. | Low-Med | None | Not just i18n -- resume conventions, JD terminology, platform-specific jargon (如 HC, 转正, 三方协议). |
| T9 | **Export as PDF/Word** | Users need to download and submit resumes manually. | Low | T5 | Both formats. PDF for visual fidelity, Word for ATS. |

---

## Differentiators

Features that set Scout apart. These are NOT table stakes -- competitors don't have them. Scout should lean hard into these.

| # | Feature | Value Proposition | Complexity | Dependencies | Notes |
|---|---------|-------------------|------------|--------------|-------|
| D1 | **Autonomous job search agent** | User sets preferences once; Scout proactively crawls Boss直聘, 实习僧, 拉勾 etc. and surfaces matching jobs. Zero browsing required. | High | T7 (user profile) | Core differentiator. No competitor does this for Chinese platforms. Must handle anti-scraping (rate limits, rotating headers, delays). Start with 2-3 platforms, not all. |
| D2 | **Deep company research per job** | For each job, Scout auto-researches: company funding history, recent news, product lines, tech blog posts, culture signals. Saves hours of manual research. | High | D1 (job list) | Scrape 天眼查/企查查 for company data. Search tech blogs, press releases. Summarize into digestible brief. |
| D3 | **Interview question aggregation from forums** | Scrape 牛客网, Glassdoor, V2EX for real interview questions specific to that company + role. | High | D1 | Extremely high value for Chinese market. 牛客面经 is the gold standard. Aggregate, deduplicate, categorize (behavioral vs technical vs system design). |
| D4 | **Cross-JD keyword frequency analysis** | Don't just match one JD -- aggregate keywords across 10+ similar JDs from the market to find what the industry truly screens for vs. what's unique to one listing. | Medium | D1, T3 | This is genuinely novel. Shows user "React appears in 90% of similar JDs, but GraphQL only in 15% -- focus on React." |
| D5 | **Interview talking points generation** | Generate personalized self-introduction + answers to common questions, grounded in real interview questions (D3) and company research (D2). Not generic templates. | High | D2, D3, T1 | Key differentiator vs. generic interview prep tools. Answers reference the specific company's products, tech stack, and culture. |
| D6 | **GitHub repo analysis** | Parse user's GitHub repos: extract tech stack, contribution patterns, star counts, code quality signals. Feed into resume tailoring. | Medium | T1 | Unique for developer-focused users. Show "your top contribution is X, relevant to this JD because Y." |
| D7 | **Paper/publication analysis** | Extract key contributions, journal impact, citation count from uploaded papers. Map to JD relevance. | Medium | T1 | Important for graduate students (target demographic). Academic achievements poorly represented in most resume tools. |
| D8 | **Job kanban board with research status** | Visual pipeline: Discovered -> Researched -> Resume Generated -> Applied -> Interview -> Offer. Shows progress per job. | Medium | D1, T7 | Teal has a basic version. Scout's is richer because each card has research + generated content attached. |

---

## Anti-Features

Things to deliberately NOT build. Each one is tempting but harmful.

| # | Anti-Feature | Why Avoid | What to Do Instead |
|---|--------------|-----------|-------------------|
| A1 | **Auto-apply / one-click submit** | Triggers platform bot detection (Boss直聘 actively detects this). Violates ToS. Mass-apply yields 1-3% callback -- worse than manual. 33% of hiring managers detect and reject auto-applied resumes within 20 seconds. Creates adversarial relationship with platforms. | Generate perfect materials; user manually submits. This is Scout's stated strategy and it's correct. |
| A2 | **Keyword stuffing / invisible text tricks** | Modern ATS uses semantic matching and NLP. Keyword stuffing triggers "copycat filters." Recruiters who spot it reject immediately. Short-term hack, long-term poison. | Natural keyword integration through bullet point rewriting. Target 80% keyword coverage, not 100%. |
| A3 | **Predatory pricing / hidden paywalls** | #1 user complaint across all AI resume tools. "Charged $300 for generic content." Users on Reddit actively warn others about tools with unclear pricing. Destroys trust. | Be upfront: free tier with limits, clear paid tier. Or free + user brings own API key (per PROJECT.md). |
| A4 | **Overly creative resume templates** | Multi-column, graphic-heavy, icon-filled templates fail ATS parsing. They look good but get rejected before a human sees them. | Offer 3-5 clean, ATS-proven templates. Function over aesthetics. |
| A5 | **AI fabrication / hallucinated experience** | AI tools are known to "lie" when user experience doesn't match JD. 62% of employers reject resumes with detectable AI fabrication. Career-ending if caught. | Strict guardrail: only reframe and emphasize existing experience. Flag gaps to user with "you may want to add X" prompts, never auto-fill. |
| A6 | **Real-time interview cheating tools** | FinalRound AI and others offer "invisible" live interview assistance. Ethically problematic. If detected, instant disqualification. Platforms are building detection. | Generate preparation materials (talking points, practice questions). Help users PREPARE, not cheat. |
| A7 | **Social login with excessive permissions** | Requesting access to user's LinkedIn/WeChat contacts "to find connections." Privacy violation. Users distrust this. | Simple email/phone auth. Optional manual LinkedIn URL input for profile enrichment, not OAuth scraping. |
| A8 | **Notification spam / engagement hacking** | "10 new jobs matched!" every hour. Drives uninstalls. | Smart batching: daily digest or configurable frequency. Quality signals only (e.g., "high-match job at company you starred"). |

---

## V2 Ideas

Good features that should NOT be in v1. Build after core loop is validated.

| # | Feature | Why Defer | Unlock Condition | Complexity |
|---|---------|-----------|------------------|------------|
| V1 | **AI mock interview (voice/video)** | Requires speech processing, real-time AI interaction. Complex UX. Core value is content generation, not simulation. | After v1 validates that users want interview prep content | Very High |
| V2 | **Cover letter generation** | Nice to have but not critical for Chinese market (cover letters less common in Chinese job applications vs. Western). | After v1, if users request it | Low-Med |
| V3 | **LinkedIn profile optimization** | Valuable for international job seekers. Not critical for domestic Chinese market focus. | If expanding to international market | Medium |
| V4 | **Salary negotiation assistant** | Useful but far downstream in job search funnel. v1 needs to nail the search-to-apply loop. | After users start getting offers through Scout | Medium |
| V5 | **Team/hiring manager profiling** | Scrape hiring manager's LinkedIn, tech talks, blog posts to understand preferences. Powerful but complex and raises privacy concerns. | After validating company research value | High |
| V6 | **Referral network matching** | "3 people in your school alumni network work at this company." Requires building a user graph. | After significant user base | Very High |
| V7 | **Application outcome tracking & analytics** | Track which resume versions led to interviews. Learn what works. | After enough users complete full apply cycle | Medium |
| V8 | **Multi-language resume generation** | Generate English + Chinese versions of the same resume. Important for foreign companies in China. | After core Chinese flow works | Medium |
| V9 | **Browser extension for manual JD capture** | Let user click a button on any job page to import JD into Scout. Complement to autonomous search. | If users find platforms Scout can't scrape | Low-Med |
| V10 | **WeChat mini-program** | Mobile-first access via WeChat ecosystem. Huge reach in China. | After web app validates product-market fit | High |

---

## Feature Dependencies

```
User Materials (T1, T2)
    |
    v
Job Search Agent (D1) -----> Job Listings (T6)
    |                              |
    v                              v
Company Research (D2)       JD Keyword Extraction (T3)
    |                              |
    v                              v
Interview Q Aggregation (D3)  Cross-JD Analysis (D4)
    |                              |
    +--------+--------+           |
             |                     |
             v                     v
    Interview Talking Points (D5)  Tailored Resume (T5)
                                       |
                                       v
                                  Export PDF/Word (T9)
                                       |
                                       v
                                  Job Kanban Board (D8)

GitHub Analysis (D6) --+
                       +--> Feed into T5 (Tailored Resume)
Paper Analysis (D7) ---+

User Account (T7) --- underlies everything
Chinese Language (T8) --- underlies everything
ATS Formatting (T4) --- applies to T5 output
```

---

## MVP Recommendation

**Phase 1 -- Core Loop (must ship first):**
1. T1: Resume upload & parsing
2. T2: Resume structure display
3. T7: User account (minimal -- even just local storage initially)
4. T8: Full Chinese language support
5. D1: Autonomous job search (start with Boss直聘 only)
6. T6: Job listing display with basic filtering
7. T3: JD keyword extraction & matching

**Phase 2 -- The Magic (Scout's differentiators):**
1. D2: Deep company research
2. D3: Interview question aggregation (牛客网)
3. T5: Per-job tailored resume generation
4. T4: ATS-friendly output
5. T9: Export PDF/Word

**Phase 3 -- Full Experience:**
1. D4: Cross-JD keyword frequency analysis
2. D5: Interview talking points generation
3. D6: GitHub repo analysis
4. D7: Paper/publication analysis
5. D8: Job kanban board

**Rationale:** Phase 1 proves the agent can find relevant jobs (the hardest technical risk). Phase 2 delivers the core "wow" -- personalized content per job. Phase 3 rounds out the experience. Each phase is independently useful: Phase 1 alone is a job aggregator, Phase 2 makes it a full AI career assistant.

**Defer:** All V2 features. Especially mock interviews (V1) and WeChat mini-program (V10) -- both are massive scope that distract from validating the core autonomous search + research loop.

---

## Chinese Market Specifics

Features and considerations unique to the Chinese job seeker market:

| Aspect | What's Different | Implication for Scout |
|--------|-----------------|----------------------|
| **Resume format conventions** | Chinese resumes include 政治面貌 (political affiliation), 籍贯 (hometown), 证件照 (ID photo), 民族 (ethnicity). Standard sections differ from Western resumes. | Resume parser and templates must handle these fields natively. |
| **Platform ecosystem** | Boss直聘, 实习僧, 拉勾, 前程无忧, 智联招聘, 牛客 -- each has unique UI and anti-scraping measures. | Start with Boss直聘 (largest for tech). Add 实习僧 (internship focus for target demo). |
| **秋招/春招 cycle** | 70-80% of campus hiring happens in 秋招 (Sep-Oct). 春招 is supplementary and more competitive. Timing is critical. | Scout should understand recruitment cycles and prioritize accordingly. Surface "秋招提前批" opportunities. |
| **面经 culture** | 牛客网面经 is THE source for real interview questions in China. Interview prep is heavily community-driven. | D3 (interview Q aggregation from 牛客) is a massive differentiator in China. No existing tool auto-aggregates this. |
| **内推 (internal referral)** | Internal referrals are the highest-converting channel for Chinese tech companies. Users actively seek 内推码. | v2 opportunity: surface referral opportunities. v1: at minimum note in company research when 内推 channels are available. |
| **三方协议 / 户口** | Fresh graduates deal with 三方协议 (tripartite agreement) and 户口 (hukou/residency) concerns that affect job decisions. | Not a Scout feature per se, but company research (D2) should surface whether company solves 户口 (a major perk). |
| **Cover letters** | Less common in Chinese job applications. Most platforms (Boss直聘) don't even have a cover letter field. | Confirms A2 anti-feature: don't prioritize cover letter generation. Move to V2. |

---

## Sources

- [8 Best AI Resume Builders in 2026 - Rezi](https://www.rezi.ai/posts/best-ai-resume-builders)
- [9 Best AI Resume Builders of 2026 - Teal](https://www.tealhq.com/post/best-ai-resume-builders)
- [Resume Now Survey: 62% of Employers Reject AI-Generated Resumes](https://www.resume-now.com/job-resources/careers/ai-applicant-report)
- [Why AI Resume Builders Hurt Tech Job Seekers - Built In](https://builtin.com/articles/risks-ai-resume-builders)
- [Why AI Job Application Tools Don't Get Interviews - Scale.jobs](https://scale.jobs/blog/ai-job-application-tools-dont-get-interviews)
- [57% Quit Applications Due to Job Search Frustration - LiveCareer](https://www.livecareer.com/resources/job-search-frustration)
- [The State of the Job Search in 2025 - Jobscan](https://www.jobscan.co/state-of-the-job-search)
- [Best AI Resume Builder Reddit - PitchMeAI](https://pitchmeai.com/blog/best-ai-resume-builder-reddit)
- [AI Auto Apply for Jobs: Complete Guide 2026 - Careery](https://careery.pro/blog/ai-job-search/ai-auto-apply-for-jobs-guide)
- [Why Applying to More Jobs with AI Doesn't Work - Scale.jobs](https://scale.jobs/blog/applying-more-jobs-with-ai-doesnt-work)
- [ChatGPT Jobs Feature - Careerflow](https://www.careerflow.ai/blog/chatgpt-jobs-feature)
- [超级简历 WonderCV - AI简历制作与优化工具](https://china-ai-like.com/tools/wondercv/)
- [AIHawk - GitHub open source job agent](https://github.com/feder-cr/Jobs_Applier_AI_Agent_AIHawk)
- [ATS-Optimized Resume Guide 2025 - Jobscan](https://www.jobscan.co/blog/20-ats-friendly-resume-templates/)
- [CNBC: Don't make these AI mistakes on your resume](https://www.cnbc.com/2025/09/15/dont-make-these-ai-mistakes-on-your-resume-career-experts-say-it-could-ruin-your-chances.html)
- [前程无忧 2026届毕业生秋招指南](https://xz.chsi.com.cn/xz/zyts/202509/20250910/2293415299.html)
- [牛客网 面试经验中心](https://www.nowcoder.com/interview/center)

**Confidence:** MEDIUM-HIGH. Feature landscape well-documented through multiple credible sources. Chinese market specifics based on domain knowledge + limited search results (some searches returned 503 errors). Anti-feature recommendations strongly supported by employer surveys and user complaint data.
