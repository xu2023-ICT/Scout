# Requirements: Scout

**Defined:** 2026-04-10
**Core Value:** 用户只需提供简历和搜索偏好，Scout Agent 自动搜索岗位、深度研究公司/团队/面经，生成针对每个岗位高度定制的简历和面试演讲稿。

## v1 Requirements

### Resume Management (RESUME)

- [ ] **RESUME-01**: 用户可上传 PDF 或 Word 格式的简历
- [ ] **RESUME-02**: AI 自动解析简历结构（工作经历、技能、教育背景）并以可读形式展示
- [ ] **RESUME-03**: 用户可查看并编辑 AI 解析的简历结构，确认无误后再处理
- [ ] **RESUME-04**: 用户可上传补充材料：论文 PDF、GitHub 仓库链接（与简历一起在开始时上传）
- [ ] **RESUME-05**: 系统自动从上传论文中提取关键贡献、发表期刊等元数据
- [ ] **RESUME-06**: 用户可将生成的定制简历导出为 PDF 或 Word
- [ ] **RESUME-07**: 生成的简历以 LapisCV 格式输出（Markdown + YAML），基于 LapisCV 模板渲染

### Job Scraping (SCRAPE)

- [ ] **SCRAPE-01**: 系统爬取 Boss直聘 JD 时自动解码 woff 字体加密，确保 JD 文本完整可读
- [ ] **SCRAPE-02**: 系统根据用户画像自动搜索 Boss直聘 匹配岗位（用户无需手动查找或提供链接）
- [ ] **SCRAPE-03**: 系统根据用户画像自动搜索 实习僧 匹配岗位
- [ ] **SCRAPE-04**: 爬取失败时自动降级：展示具体错误原因，保留手动粘贴 JD 作为 fallback
- [ ] **SCRAPE-05**: 用户可设置搜索偏好（城市、岗位类型、行业）

### AI Generation (AI)

- [ ] **AI-01**: 系统针对每个岗位生成定制简历，保留用户原有写作风格和句式
- [ ] **AI-02**: 系统严格基于用户提供的材料生成内容，绝不捏造技能或经历；如有技能缺口，告知用户而非补全
- [ ] **AI-03**: 用户可查看 Diff 视图，逐条看到 AI 改了什么、为什么改
- [ ] **AI-04**: 关键词密度控制在 70-80%（不堆砌），通过 ATS 语义匹配检测
- [ ] **AI-05**: 当信息不足时，系统暂停并弹窗要求用户补充具体信息，补充后自动恢复
- [ ] **AI-06**: 生成内容避免 AI 特征词汇（"pivotal"、"transformative"等），降低 HR 识别率

### Deep Research (RESEARCH)

- [ ] **RESEARCH-01**: 针对每个岗位，系统自动研究公司背景（融资、产品动态、技术博客、企业文化）
- [ ] **RESEARCH-02**: 系统自动爬取牛客网该公司/岗位的真实面经（面试题、面试轮次、笔试情况）
- [ ] **RESEARCH-03**: 系统自动搜索小红书该公司/岗位的真实面试经历帖子
- [ ] **RESEARCH-04**: 系统聚合 10+ 个同类 JD 的关键词并展示出现频率（"React 出现在 90% 的同类 JD 中"）
- [ ] **RESEARCH-05**: 系统基于真实面经 + 公司研究生成个性化面试演讲稿（自我介绍 + 常见问题回答框架）

### Job Management (JOBS)

- [ ] **JOBS-01**: 用户可在 Dashboard 查看所有已发现/已处理的岗位列表
- [ ] **JOBS-02**: 用户可按城市、薪资、公司规模、行业筛选岗位
- [ ] **JOBS-03**: 每个岗位展示与用户画像的匹配分数
- [ ] **JOBS-04**: 用户通过看板管理岗位状态（已发现 → 已研究 → 已生成 → 已投递）
- [ ] **JOBS-05**: 用户可实时看到 Agent 工作进度（通过 SSE 流式展示每一步状态）


## v2 Requirements

### 深度材料分析

- **MAT-01**: GitHub 仓库深度分析（代码质量评分、技术栈识别、项目贡献度）
- **MAT-02**: 自动分析 GitHub star 数、fork 数，在简历中突出量化指标

### 面试准备增强

- **PREP-01**: 模拟面试对话（基于真实面经的问答练习）
- **PREP-02**: 面试录音/录像分析（语速、关键词覆盖）

### 扩展平台

- **PLAT-01**: 智联招聘爬取支持
- **PLAT-02**: 拉钩招聘爬取支持
- **PLAT-03**: 前程无忧爬取支持
- **PLAT-04**: 牛客招聘爬取支持

### 社交功能

- **SOCIAL-01**: 内推信息关联（该岗位是否有内推渠道）
- **SOCIAL-02**: OAuth 登录（GitHub、微信）

## Out of Scope

| Feature | Reason |
|---------|--------|
| 自动投递 | 触发平台反自动化封禁，违反平台 ToS，实际投递质量低（1-3% 回调率） |
| LinkedIn 爬取 | LinkedIn 主动对爬虫提起法律诉讼，法律风险不成比例 |
| 求职信生成 | 中国招聘市场普遍不需要求职信 |
| 移动 App | Web 优先，验证需求后再说 |
| ToB/HR 端功能 | 先验证 ToC 需求 |
| 关键词堆砌优化 | 现代 ATS 会降权关键词堆砌，适得其反 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| RESUME-01 | Phase 1 | Pending |
| RESUME-02 | Phase 1 | Pending |
| RESUME-03 | Phase 1 | Pending |
| RESUME-04 | Phase 1 | Pending |
| RESUME-05 | Phase 1 | Pending |
| RESUME-06 | Phase 3 | Pending |
| RESUME-07 | Phase 3 | Pending |
| SCRAPE-01 | Phase 1 | Pending |
| SCRAPE-02 | Phase 1 | Pending |
| SCRAPE-03 | Phase 1 | Pending |
| SCRAPE-04 | Phase 1 | Pending |
| SCRAPE-05 | Phase 1 | Pending |
| AI-01 | Phase 1 | Pending |
| AI-02 | Phase 1 | Pending |
| AI-03 | Phase 3 | Pending |
| AI-04 | Phase 3 | Pending |
| AI-05 | Phase 3 | Pending |
| AI-06 | Phase 3 | Pending |
| RESEARCH-01 | Phase 2 | Pending |
| RESEARCH-02 | Phase 2 | Pending |
| RESEARCH-03 | Phase 2 | Pending |
| RESEARCH-04 | Phase 2 | Pending |
| RESEARCH-05 | Phase 2 | Pending |
| JOBS-01 | Phase 1 | Pending |
| JOBS-02 | Phase 4 | Pending |
| JOBS-03 | Phase 4 | Pending |
| JOBS-04 | Phase 4 | Pending |
| JOBS-05 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 28
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-10*
*Last updated: 2026-04-10 after roadmap phase mapping*
