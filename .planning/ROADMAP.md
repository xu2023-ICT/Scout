# Roadmap: Scout

**Phases:** 4 (+ Phase 5 if traction)
**Total v1 Requirements:** 28
**Granularity:** Standard
**Created:** 2026-04-10
**Last updated:** 2026-04-10 after requirement revisions

## Phases

- [ ] **Phase 1: Core Pipeline** - 上传全部材料 → 自动搜索 Boss直聘 + 实习僧（含字体解密）→ 生成定制简历
- [ ] **Phase 2: Deep Research** - 公司研究 + 牛客/小红书面经 + 跨JD关键词分析 + 面试演讲稿
- [ ] **Phase 3: Generation Quality** - Diff视图、ATS优化、防幻觉、LapisCV格式导出
- [ ] **Phase 4: Job Management** - 筛选、匹配分、看板、SSE实时进度

## Phase Details

### Phase 1: Core Pipeline
**Goal**: 用户上传简历和全部补充材料，系统自动搜索 Boss直聘 + 实习僧 匹配岗位（含 woff 字体解密），并针对每个岗位生成定制简历。用户无需手动查找职位或复制 JD。
**Depends on**: Nothing (first phase)
**Requirements**: RESUME-01, RESUME-02, RESUME-03, RESUME-04, RESUME-05, SCRAPE-01, SCRAPE-02, SCRAPE-03, SCRAPE-04, SCRAPE-05, AI-01, AI-02, JOBS-01
**Success Criteria** (what must be TRUE):
  1. 用户上传 PDF/Word 简历后能看到解析后的结构（工作经历、技能、教育），可编辑修正
  2. 用户上传论文 PDF 和 GitHub 链接后，系统自动提取论文贡献和期刊元数据
  3. 系统根据用户偏好自动搜索 Boss直聘 和 实习僧，无需用户提供链接，爬取时正确解码 woff 字体加密
  4. 爬取失败时，系统展示具体错误原因并提供手动粘贴 JD 的降级方案
  5. 用户在 Dashboard 可看到所有已发现岗位列表
  6. 每个岗位生成一份定制简历，保留用户写作风格，零捏造内容
**Plans**: TBD
**UI hint**: yes

### Phase 2: Deep Research
**Goal**: 针对每个岗位，系统自动研究公司背景、从牛客网和小红书抓取真实面经、聚合同类 JD 关键词频率，并生成基于真实数据的个性化面试演讲稿
**Depends on**: Phase 1
**Requirements**: RESEARCH-01, RESEARCH-02, RESEARCH-03, RESEARCH-04, RESEARCH-05
**Success Criteria** (what must be TRUE):
  1. 每个岗位有一份公司研究报告（融资动态、产品、技术博客、企业文化）
  2. 牛客网该公司/岗位的真实面试题和面试流程可见
  3. 小红书该公司/岗位的真实面试经历帖子可见
  4. 聚合 10+ 同类 JD 的关键词出现频率（如"React 出现在 90% 的同类 JD 中"）
  5. 生成基于真实面经 + 公司研究的个性化面试演讲稿（自我介绍 + 常见问题回答框架）
**Plans**: TBD

### Phase 3: Generation Quality
**Goal**: 用户可查看 AI 逐条修改原因，生成内容通过 ATS 语义匹配，避免 AI 特征词，支持 LapisCV 格式输出和 PDF/Word 导出
**Depends on**: Phase 1
**Requirements**: AI-03, AI-04, AI-05, AI-06, RESUME-06, RESUME-07
**Success Criteria** (what must be TRUE):
  1. Diff 视图清晰展示 AI 改了哪里、为什么改
  2. 关键词密度维持在 70-80%，生成内容无 AI 特征词汇（"pivotal"、"transformative" 等）
  3. 信息不足时系统暂停并弹窗让用户补充，补充后自动继续
  4. 生成的简历以 LapisCV 格式（Markdown + YAML）输出，可编译为 PDF；同时支持直接导出 Word
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
| 1. Core Pipeline | 0/? | Not started | - |
| 2. Deep Research | 0/? | Not started | - |
| 3. Generation Quality | 0/? | Not started | - |
| 4. Job Management | 0/? | Not started | - |
| 5. Scale (if traction) | — | On hold | - |

---
*Roadmap created: 2026-04-10*
*Last updated: 2026-04-10 after requirement revisions (merged Phase 1+2, added LapisCV, moved materials to Phase 1)*
