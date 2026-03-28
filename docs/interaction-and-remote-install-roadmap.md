# 前端交互与远端安装路线图

这份文档用于记录：当前 repo-backed skills market 已经产品化了哪些交互闭环，还剩哪些能力没有做成页面级体验。

## 当前已完成

### 1. 浏览与教学

- 首页、skills、bundles、docs 都已经走真实仓库产物
- docs 页面已经有搜索、过滤、上下文、相关文章和 action panel
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
- browser-side approval capture
- post-write evidence pack 展示

其中：

- `prepare` 用来生成 review pack
- `stage` 用来把治理源文件改动安全写入 staging root
- `verify` 用来重新校验 staged 或 written 结果
- `write handoff` 用来解释 write 资格、展示 CLI write/verify 命令、approval checklist 与 evidence pack
- `write` 本身仍然保持 CLI-only

## 当前剩余缺口

当前最大的缺口已经从“能不能执行”转成了“怎样把高风险动作继续做成可审计、可追踪、可交接的页面流程”：

1. approval capture 目前只保存在浏览器本地，还没有进入 backend 可追溯审计记录
2. write handoff 还没有结构化的 approval history / audit timeline / evidence archive
3. docs action panel 仍然是运行指引，不是页面内执行器
4. remote install 还可以继续增强 org policy / provenance 级别的组合解释

## 下一轮建议

下一轮优先建议继续推进 governance write audit，而不是重新扩张新的远端场景。

原因：

- remote install 已经具备第一轮风控与恢复闭环
- installed-state governance 已经补到 approval capture 和 post-write evidence，最自然的下一步就是把这些信息沉淀成可追溯审计记录
- 这段能力一旦补齐，前端和 backend 的“读 -> 审 -> stage -> verify -> handoff -> write audit”链路会更完整

建议下一轮聚焦：

- 持久化 approval record，与 target root / report / operator note 绑定
- 页面化 audit timeline 与 evidence archive
- Playwright 覆盖 `approval persisted -> audit trail visible` 的真实路径

下一轮规划文档见 [frontend-governance-write-audit-iteration.md](./frontend-governance-write-audit-iteration.md)。
