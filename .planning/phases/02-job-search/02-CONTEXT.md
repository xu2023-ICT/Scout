# Phase 2: Job Search - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

用户在 /search 页填写偏好并选择目标公司，Scout 通过 Tavily API 并行搜索各公司官方招聘页的匹配 JD，实时展示搜索进度，完成后自动跳转到 Dashboard 展示所有找到的岗位。

**v1 范围（本 Phase）：**
- 偏好收集页 (/search)
- 内置大厂官网列表 + 用户可添加自定义公司官网
- Tavily API 搜索 + 内容抓取（每公司并行）
- SSE 实时进度展示（留在 /search 页）
- Dashboard (/dashboard) 展示所有岗位列表
- 搜索失败降级：手动粘贴 JD

**不在 Phase 2 范围内（已移至 v2）：**
- Boss直聘爬取（woff 字体解密、反爬处理）
- 实习僧爬取
- 岗位筛选/排序（Phase 4）
- 匹配分数计算（Phase 4）
- 公司深度研究（Phase 3）

</domain>

<decisions>
## Implementation Decisions

### 范围决策（v1 vs v2）
- **D-01:** v1 只搜索互联网大厂官方招聘页（Tavily API），不做 Boss直聘/实习僧（反爬技术移至 v2）
- **D-02:** 搜索方式：Tavily search query = "公司名 + 岗位关键词 + 招聘/职位"，Tavily 返回 URL + 内容摘要

### 搜索入口设计
- **D-03:** 独立 /search 页面（不是 Dashboard 内嵌表单，不是 Modal）
- **D-04:** /search 页分两个区域：
  - 区域 A：偏好设置（城市多选必填、岗位类型单选、行业方向多选、关键词补充自由输入）
  - 区域 B：公司选择（内置大厂列表，默认全选，用户可取消；可手动输入添加新公司官网 URL）
- **D-05:** 点击「开始搜索」按钮触发搜索，不自动触发

### 内置公司列表
- **D-06:** 内置约 20-30 家主要互联网大厂（字节跳动、阿里巴巴、腾讯、美团、百度、京东、快手、滴滴、网易、小米等），以 checkbox 列表展示，用户可全选/取消选
- **D-07:** 用户可额外添加公司官网 URL（输入框 + 添加按钮），添加后以同样的 checkbox 形式出现在列表中

### 搜索进度展示
- **D-08:** 点击「开始搜索」后留在 /search 页，表单区域替换为进度视图
- **D-09:** 进度视图：每个公司一行，展示实时状态（搜索中... / ✓ 找到 N 个 / ✗ 失败）
- **D-10:** 所有公司搜索完成后，自动跳转到 /dashboard
- **D-11:** 进度通过 SSE（fetch + ReadableStream，沿用 Phase 1 模式）流式推送

### Dashboard 岗位卡片
- **D-12:** 每张岗位卡展示：公司名 + 岗位名（必须）、城市 + 薪资范围（如有）、JD 前两行摘要、来源标签（如「字节官网」）
- **D-13:** 卡片布局：列表视图（非网格），单列或两列由实现决定（Claude's Discretion）
- **D-14:** Phase 2 暂无匹配分（JOBS-03 是 Phase 4 的事），卡片无分数显示

### 降级方案
- **D-15:** 搜索失败的公司，在进度视图该行显示「✗ 失败 — 粘贴 JD」按钮
- **D-16:** 点击按钮在 Dashboard 对应位置（或 Modal）弹出文本框，用户粘贴原始 JD 文本，提交后作为一条岗位记录存入
- **D-17:** Dashboard 始终有「+ 手动添加岗位」按钮（兜底，不只依赖失败触发）

### Claude's Discretion
- Tavily query 的精确措辞和参数（search_depth, max_results）由实现阶段决定
- 公司列表数据结构（JSON 文件还是硬编码）由实现决定
- SSE 事件 payload 格式由实现决定
- Dashboard 卡片具体布局（一列/两列/响应式）由实现决定

</decisions>

<canonical_refs>
## Canonical References

- `.planning/REQUIREMENTS.md` — SCRAPE-01（v2）、SCRAPE-02、SCRAPE-03、SCRAPE-04、JOBS-01
- `.planning/ROADMAP.md` — Phase 2 Goal 和 Success Criteria
- `.planning/phases/01-upload-parse/01-CONTEXT.md` — D-05（单页滚动）、SSE 模式、已有 UI 组件列表
- `scout-frontend/src/services/api.ts` — 现有 SSE fetch+ReadableStream 实现（Phase 2 进度 SSE 参考）
- `scout-frontend/src/stores/resume.ts` — Pinia store 模式（Phase 2 需新建 jobs store）
- `scout-backend/app/routers/upload.py` — 现有 API router 结构（Phase 2 新增 search + jobs router）

</canonical_refs>

<deferred>
## Deferred Ideas

- Boss直聘/实习僧爬取 + woff 字体解密 — v2（反爬技术复杂度过高）
- 岗位筛选/排序（城市、薪资、行业）— Phase 4 (JOBS-02)
- 匹配分数展示 — Phase 4 (JOBS-03)
- 看板状态管理 — Phase 4 (JOBS-04)
- 实时 Agent 工作进度 — Phase 4 (JOBS-05)
- 论文 URL 输入（arXiv/DOI）— Phase 1 补丁，用户决定暂跳过

</deferred>
