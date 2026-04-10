# Roadmap: Scout

**Phases:** 4 (+ Phase 5 if traction)
**Total v1 Requirements:** 27
**Granularity:** Standard
**Created:** 2026-04-10
**Last updated:** 2026-04-10 after requirement revisions

## Phases

- [ ] **Phase 1: Upload & Parse** - 上传简历+材料 → AI解析结构化数据 → 表单确认
- [ ] **Phase 2: Job Search** - 询问偏好 → 并行搜索互联网大厂官网（Tavily API，v1）→ 展示Dashboard（Boss直聘/实习僧 → v2）
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
**Goal**: 系统询问用户偏好，通过 Tavily API 并行搜索互联网大厂官方招聘页（v1；Boss直聘/实习僧 → v2），实时展示搜索进度，结果展示在 Dashboard
**Depends on**: Phase 1
**Requirements**: SCRAPE-02, SCRAPE-03, SCRAPE-04, JOBS-01（SCRAPE-01 已移至 v2）
**Success Criteria** (what must be TRUE):
  1. 用户在 /search 页填写偏好（城市/岗位类型/行业/关键词）并选择目标公司（内置大厂列表，可添加）
  2. 点击「开始搜索」后，页面实时展示各公司搜索状态（搜索中/找到N个/失败），全部完成后自动跳转 Dashboard
  3. Tavily 搜索某公司失败时，在该位置显示「粘贴 JD」降级入口
  4. 用户在 /dashboard 看到所有已发现岗位（公司名+职位+城市+薪资+JD摘要+来源标签）
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
| 1. Upload & Parse | 5/5 | ✅ Complete | 2026-04-10 |
| 2. Job Search | 0/? | Planning | - |
| 3. Research → Generate | 0/? | Not started | - |
| 4. Job Management | 0/? | Not started | - |
| 5. Scale (if traction) | — | On hold | - |

---
*Roadmap created: 2026-04-10*
*Last updated: 2026-04-10 — Phase 2 scope revised: v1 only searches company official career pages via Tavily (Boss直聘/实习僧 → v2)*
*Phase 1 complete: 2026-04-10 — 5 plans, E2E verified*
