# Roadmap: Scout

**Phases:** 4 (+ Phase 5 if traction)
**Total v1 Requirements:** 27
**Granularity:** Standard
**Created:** 2026-04-10
**Last updated:** 2026-04-10 after requirement revisions

## Phases

- [ ] **Phase 1: Upload & Parse** - 上传简历+材料 → AI解析结构化数据 → 表单确认
- [ ] **Phase 2: Job Search** - 询问偏好+分析简历 → 并行搜索所有平台（Boss+实习僧+官网）→ 展示Dashboard
- [ ] **Phase 3: Research → Generate** - 先研究（公司+牛客+小红书+跨JD） → 再生成定制简历+面试稿+质量控制
- [ ] **Phase 4: Job Management** - 筛选、匹配分、看板、SSE实时进度

## Phase Details

### Phase 1: Upload & Parse
**Goal**: 用户上传简历和补充材料，AI 解析出结构化数据，用户在网页表单上确认/修正，系统存储数据准备就绪
**Depends on**: Nothing (first phase)
**Requirements**: RESUME-01, RESUME-02, RESUME-03, RESUME-04, RESUME-05
**Success Criteria** (what must be TRUE):
  1. 用户上传 PDF/Word 简历，看到解析后的结构化内容（工作经历、技能、教育），可编辑修正
  2. 用户上传论文 PDF，系统自动提取关键贡献、发表期刊、元数据
  3. 用户提交 GitHub 链接，系统记录（不做分析）
  4. 解析完成后展示结构化表单，用户确认内容正确后系统准备就绪
**Plans:** 5 plans
Plans:
- [x] 01-01-PLAN.md — Project scaffold: FastAPI backend + SQLAlchemy models/schemas + Vue 3 frontend + test infrastructure
- [ ] 01-02-PLAN.md — Backend: file upload endpoint + PDF/Word text extraction + integration tests
- [ ] 01-03-PLAN.md — Backend: Claude Haiku 4.5 structured parsing (RESUME_SCHEMA + PAPER_SCHEMA) wired into pipeline
- [ ] 01-04-PLAN.md — Frontend: upload page with drag-drop zone + SSE progress display + auto-redirect
- [ ] 01-05-PLAN.md — Frontend: /review/{id} editable structured form (all sections) + save/confirm + human verify
**UI hint**: yes

### Phase 2: Job Search
**Goal**: 系统先询问用户偏好并结合简历自动推断搜索策略，然后并行搜索 Boss直聘、实习僧、公司官网，含 woff 字体解密，展示岗位 Dashboard
**Depends on**: Phase 1
**Requirements**: SCRAPE-01, SCRAPE-02, SCRAPE-03, SCRAPE-04, JOBS-01
**Success Criteria** (what must be TRUE):
  1. 系统询问用户偏好（城市/类型/行业），同时分析简历关键词，综合生成搜索策略
  2. Boss直聘、实习僧、公司官网三平台并行搜索，woff 字体正确解码，JD 文本完整可读
  3. 爬取失败时展示具体错误，提供手动粘贴 JD 的降级方案
  4. 用户在 Dashboard 看到所有已发现岗位列表
**Plans**: TBD
**UI hint**: yes

### Phase 3: Research → Generate
**Goal**: 针对每个岗位，先完成公司研究+面经抓取+跨JD分析，再基于研究结果生成定制简历和面试演讲稿，含质量控制和导出
**Depends on**: Phase 2
**Requirements**: RESEARCH-01, RESEARCH-02, RESEARCH-03, RESEARCH-04, RESEARCH-05, AI-01, AI-02, AI-03, AI-04, AI-05, AI-06, RESUME-06, RESUME-07
**Success Criteria** (what must be TRUE):
  1. 每个岗位有公司研究报告（融资、产品、技术博客、企业文化）
  2. 牛客网真实面经（面试题、轮次、笔试）和小红书面试经历帖子均可见
  3. 聚合 10+ 同类 JD 关键词频率分析可见
  4. 基于研究生成定制简历：保留用户写作风格、零捏造、关键词密度 70-80%、无 AI 特征词
  5. Diff 视图展示每处修改原因；信息不足时暂停弹窗要求补充
  6. 生成个性化面试演讲稿（自我介绍+常见问题），可导出为 PDF/Word
**Plans**: TBD
**UI hint**: yes

### Phase 4: Job Management
**Goal**: 用户可按条件筛选岗位、查看匹配分、用看板管理投递状态、实时看到 Agent 每步工作进度
**Depends on**: Phase 1, Phase 2
**Requirements**: JOBS-02, JOBS-03, JOBS-04, JOBS-05
**Success Criteria** (what must be TRUE):
  1. 用户可按城市、薪资、公司规模、行业筛选岗位列表
  2. 每个岗位展示与用户画像的匹配分数
  3. 用户可拖拽岗位在看板各列间移动（已发现 → 已研究 → 已生成 → 已投递）
  4. Agent 工作时每步状态通过 SSE 实时推送到前端展示
**Plans**: TBD
**UI hint**: yes

### Phase 5: Scale (if traction)
**Goal**: 有真实用户后的扩展——PostgreSQL 迁移、Celery 并发、更多平台爬虫
**Depends on**: Phase 1~4 完成且产品有用户
**Requirements**: (no v1 requirements — triggered by traction)
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Upload & Parse | 1/5 | In Progress | - |
| 2. Job Search | 0/? | Not started | - |
| 3. Research → Generate | 0/? | Not started | - |
| 4. Job Management | 0/? | Not started | - |
| 5. Scale (if traction) | — | On hold | - |

---
*Roadmap created: 2026-04-10*
*Last updated: 2026-04-10 after requirement revisions (merged Phase 1+2, added LapisCV, moved materials to Phase 1)*
*Phase 1 planned: 2026-04-10 — 5 plans in 4 waves*
