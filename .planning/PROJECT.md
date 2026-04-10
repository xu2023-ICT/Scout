# Scout

## What This Is

Scout 是一个主动猎职 Agent 平台，面向求职者（尤其是学生和应届生）。用户上传简历和相关材料后，Scout 自动搜索匹配岗位、深度研究每个岗位的公司/团队/招聘背景，并生成针对每个岗位高度定制的简历和面试演讲稿。用户只需决定投哪个，Scout 完成其他一切。

## Core Value

**一键触发，AI 替你主动出击找岗位、做研究、改简历——用户不需要搜索、不需要复制 JD、不需要自己改。**

## Requirements

### Validated

(None yet — ship to validate)

### Active

**用户材料输入**
- [ ] 用户上传简历（PDF/Word）
- [ ] 用户上传补充材料：论文 PDF、GitHub 仓库链接
- [ ] AI 自动解析简历结构（工作经历、技能、教育背景）
- [ ] AI 自动分析 GitHub 仓库（技术栈、代码质量、star 数）
- [ ] AI 自动提取论文关键贡献、发表期刊、引用量

**岗位主动搜索**
- [ ] Agent 根据用户画像自动搜索 Boss直聘、实习僧等平台的匹配岗位（爬取公开 JD 页面，无需登录）
- [ ] 支持用户设置搜索偏好（城市、岗位类型、行业）
- [ ] 展示搜索到的岗位列表，供用户确认/过滤

**岗位深度研究（每个岗位）**
- [ ] 爬取并解析完整 JD，提取关键词（含频率权重）
- [ ] 聚合同类岗位 JD 关键词，分析市场真正筛选标准
- [ ] 搜索公司背景：近期融资、产品动态、技术博客、文化价值观
- [ ] 搜索团队信息：技术栈偏好、团队规模
- [ ] 抓取 HR/招聘者 LinkedIn 画像（背景、偏好）
- [ ] 爬取牛客/Glassdoor 该公司面经（面试题、面试流程）

**定制化内容生成（每个岗位）**
- [ ] 生成针对该岗位的定制简历（突出最相关经历、使用 JD 关键词）
- [ ] 生成面试演讲稿（自我介绍 + 常见问题回答框架，基于真实面经）
- [ ] 当信息不足时弹窗提示用户补充

**用户管理**
- [ ] 岗位看板：展示所有已研究岗位及生成状态
- [ ] 用户账号系统（保存简历、材料、历史岗位）

### Out of Scope

- **自动投递** — 平台反自动化机制复杂，且违反 ToS；v1 用户手动投递
- **面试模拟/对话** — 优先做内容生成，交互面试是 v2 功能
- **ToB/HR 侧功能** — 先验证 ToC 需求

## Context

- 当前 AI 简历优化产品主要分两类：纯改写（低质量）和基于 JD 的改写（需手动复制 JD）。两者都缺乏主动搜索和深度研究能力。
- 核心差异化：**Agent 主动搜索岗位 + 深度研究 + 面经驱动的面试稿**，用户零搜索成本。
- Boss直聘、实习僧等平台的 JD 页面**无需登录即可访问**，爬取技术上可行。
- 用户（开发者）是研究生，独立开发，代码能力有限，需要 Claude 辅助编码。

## Constraints

- **开发者**: 单人研究生开发，需选择上手难度合理的技术栈
- **平台限制**: 爬取需注意频率限制，避免 IP 封禁（加延迟、轮换请求头）
- **AI 成本**: 每个岗位深度研究 + 内容生成消耗较多 token，需控制成本或让用户自带 API Key
- **数据合规**: 不存储用户简历敏感信息超过必要时间

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Web 应用（非浏览器插件） | Agent 需要后台主动搜索，插件无法在用户未打开页面时运行 | — Pending |
| 用户手动投递，Scout 只生成内容 | 绕开平台反自动化机制，降低技术风险和 ToS 风险 | — Pending |
| 产品名：Scout | 直接反映"AI 替你主动侦察岗位"的核心价值 | — Pending |
| 面经驱动面试稿 | 基于真实题目生成，比通用模板有显著差异化 | — Pending |
| 先免费，验证需求再变现 | 单人开发，首要目标是验证产品价值 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-10 after initialization*
