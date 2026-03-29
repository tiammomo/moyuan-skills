# 前端交互与远端安装路线图

这份文档用于记录：当前 repo-backed skills market 已经产品化了哪些交互闭环，还剩哪些能力没有做成页面级体验。

## 当前已完成

### 1. 浏览与教学

- 首页、skills、bundles、docs 都已经走真实仓库产物
- docs 页面已经有搜索、过滤、上下文、相关文章、action panel、allowlist backend action execution，以及 recent runs compare / filter、run diff summary、section diff 状态、quick-open handoff、last-success 回看与 artifact / stdout / stderr drilldown
- 中文教学与业务案例文档已经接入

### 2. 本地 lifecycle

- skill / bundle install、update、remove 已接入 backend execution
- installed-state 已接入 doctor / repair / baseline / governance
- 页面会按 target root 在 job 完成后刷新状态

### 3. remote registry install

- remote skill / bundle install 已接入
- 执行前会展示 trust summary、policy gate、approval
- 执行失败后支持 retry、staged cache cleanup、限定目标 rollback

### 4. installed-state governance

installed-state governance 这一层现在已经完成：

- governance summary refresh
- waiver / apply handoff `prepare`
- safe `stage`
- refresh `verify`
- write handoff 页面化
- persisted approval record
- audit timeline / evidence archive
- post-write evidence pack 展示

其中：

- `prepare` 用来生成 review pack
- `stage` 用来把治理源文件改动安全写入 staging root
- `verify` 用来重新校验 staged 或 written 结果
- `write handoff` 用来解释 write 资格、展示 CLI write/verify 命令、approval checklist 与 evidence pack
- `write` 本身仍然保持 CLI-only

## 当前剩余缺口

当前最大的缺口已经从“怎样把差异提示带到 drilldown 入口”进一步转成了“怎样在不展开完整输出的情况下，先把最关键的差异摘录直接摆到 summary 层”：

1. docs action 现在已经能把 diff summary 接到 drilldown，但 artifact / stdout / stderr 还缺少更直接的 inline excerpt / before-vs-baseline 摘录
2. governance approval audit 目前还没有更细的 archive 检索、筛选与批量回看能力
3. remote install 还可以继续增强 org policy / provenance 级别的组合解释

## 下一轮建议

下一轮优先建议继续顺着 docs action 往下做 inline diff excerpts，而不是立刻回到更重的治理 UI。

原因：

- docs action execution、recent runs compare / filter、run diff summary、section diff 状态和 quick-open handoff 已经有了，现在最值得补的是“怎样先给出足够短的差异摘录，再决定要不要展开完整输出”
- remote install 已经具备第一轮风控与恢复闭环
- installed-state governance 已经补到 approval record、audit timeline 和 post-write evidence，主要闭环已经成型

建议下一轮聚焦：

- docs action artifact / stdout / stderr 的 inline diff excerpt
- selected run 与 pinned success 之间的摘要级 before / after 对照
- Playwright 覆盖 docs action excerpt / drilldown 的真实切换链路

下一轮规划文档见 [frontend-docs-action-inline-diff-excerpts-iteration.md](./frontend-docs-action-inline-diff-excerpts-iteration.md)。
