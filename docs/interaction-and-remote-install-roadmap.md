# 前端交互与远端安装路线图

这份文档用于记录：当前 repo-backed skills market 已经产品化了哪些交互闭环，还剩哪些能力没有做成页面级体验。

## 当前已完成

### 1. 浏览与教学

- 首页、skills、bundles、docs 都已经走真实仓库产物
- docs 页面已经有搜索、过滤、上下文、相关文档和 action panel
- 中文教学与业务案例文档已经接入

### 2. 本地 lifecycle

- skill / bundle install、update、remove 已接入 backend execution
- installed-state 已接入 doctor / repair / baseline / governance
- 页面会按 target root 在 job 完成后刷新状态

### 3. remote registry install

- remote skill / bundle install 已接入
- 执行前会展示 trust summary、policy gate、approval
- 执行失败后支持 retry、staged cache cleanup、限定目录 rollback

### 4. installed-state governance

installed-state governance 这一层现在已经完成：

- governance summary refresh
- waiver / apply handoff `prepare`
- safe `stage`
- refresh `verify`
- write handoff 页面化

其中：

- `prepare` 用来生成 review pack
- `stage` 用来把治理源文件改动安全写入 staging root
- `verify` 用来重新校验 staged 或 written 结果
- `write handoff` 用来解释 write 资格、展示 CLI write/verify 命令和 checklist
- `write` 本身仍然保持 CLI-only

## 当前剩余缺口

当前最大的剩余缺口已经从“能不能执行”转成了“怎样把高风险动作继续做成可审批、可追踪、可回溯的页面流程”：

1. governance write mode 还没有真正的前端 approval capture 与审计记录
2. docs action panel 仍然是运行指引，不是页面内执行器
3. remote install 仍可继续增强 org policy / provenance 级别的组合规则解释

## 下一轮建议

下一轮优先建议继续推进 governance write-mode，而不是重新扩张新的远端场景。

原因：

- remote install 已经有第一轮风控与恢复闭环
- installed-state governance 现在已经补到 write handoff，离真正的 approval capture 只差最后一步
- 这段能力一旦补齐，前端和 backend 的“读 -> 审 -> stage -> verify -> handoff -> write audit”链路会更完整

建议下一轮聚焦：

- 显式 approval capture 与 operator 责任说明
- post-write audit / refresh / evidence 收口
- write 后的持续 verify 与 drift 回溯说明

下一轮规划文档见 [frontend-governance-write-execution-iteration.md](./frontend-governance-write-execution-iteration.md)。
