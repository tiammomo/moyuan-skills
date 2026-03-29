# 前端交互与远端安装路线图

这份文档用于记录：当前 repo-backed skills market 已经产品化了哪些交互闭环，还剩哪些能力没有做成页面级体验。

## 当前已完成

### 1. 浏览与教学

- 首页、skills、bundles、docs 都已经走真实仓库产物
- docs 页面已经有搜索、过滤、上下文、相关文章、action panel、allowlist backend action execution，以及 recent runs compare / filter、last-success 回看与 artifact / stdout / stderr drilldown
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

当前最大的缺口已经从“怎样把多次运行结果做成更高效的比较与筛选”进一步转成了“怎样把选中运行和基线运行的差异说明得更结构化”：

1. docs action 现在已经能 compare / filter recent runs，但 selected run 与 last-success 之间还缺少结构化 diff summary
2. governance approval audit 目前还没有更细的 archive 检索、筛选与批量回看能力
3. remote install 还可以继续增强 org policy / provenance 级别的组合解释

## 下一轮建议

下一轮优先建议继续顺着 docs action 往下做 selected run diff summary，而不是立刻回到更重的治理 UI。

原因：

- docs action execution、recent runs compare / filter 和 artifact drilldown 已经有了，现在最值得补的是“怎样把选中运行与基线运行的变化总结出来”
- remote install 已经具备第一轮风控与恢复闭环
- installed-state governance 已经补到 approval record、audit timeline 和 post-write evidence，主要闭环已经成型

建议下一轮聚焦：

- docs action selected run 与 last-success 的 diff summary
- result summary、artifact drilldown 与历史选择之间的差异提示
- Playwright 覆盖 docs action diff summary / compare handoff 的真实链路

下一轮规划文档见 [frontend-docs-action-run-diff-iteration.md](./frontend-docs-action-run-diff-iteration.md)。
