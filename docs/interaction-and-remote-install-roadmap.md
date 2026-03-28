# 前端交互与远端安装路线图

这份路线图用于说明：当前 repo-backed `skills market` 已经完成了哪些闭环，还剩哪些按钮、执行链路和治理动作没有产品化。

## 当前总览

当前已经完成：

- 前端与后端的 repo-backed 浏览链路
- skill / bundle 详情页上的本地 install、update、remove
- installed-state doctor、repair、baseline、governance、waiver/apply prepare
- remote registry install
- remote trust summary、policy gate、approval
- 远端失败后的 retry、staged cache cleanup、remote target rollback
- Playwright 端到端联调覆盖

当前最大的剩余缺口变成了：

1. waiver / apply 的 write-mode governance execution 仍然是 CLI-only
2. docs action panel 仍然是运行指引，不是可执行动作

## 分阶段状态

### 阶段 1：浏览与教学

状态：`已完成`

已经具备：

- 首页、skills、bundles、docs 的真实数据展示
- 文档搜索、筛选、关联导航
- docs 上下文面板、推荐顺序、前置条件、预期结果与产物提示

### 阶段 2：本地 lifecycle 执行

状态：`已完成`

已经具备：

- skill / bundle install、update、remove 的后端执行
- job polling 与 summary 展示
- detail page 上的 honest copy-first 提示

### 阶段 3：远端 registry install

状态：`已完成`

已经具备：

- CLI 远端 install / install-bundle
- backend 远端 install API
- 前端 skill / bundle 详情页上的 registry-backed execution

### 阶段 4：远端风险控制与恢复

状态：`已完成首版产品化`

这一轮已经补上：

- remote trust summary
- explicit approval
- remote policy gate 状态
- policy-blocked 路径上的前端禁用与原因说明
- failed run 后的 retry
- staged cache cleanup
- 限定在 `dist/frontend-remote-execution/` 作用域内的 remote target rollback

当前结论：

- 前端已经能解释“为什么不能跑”
- 前端已经能解释“失败后先怎么清理或回滚”
- 更深一层的 org policy / provenance 组合规则仍可继续增强，但首轮产品闭环已经成立

### 阶段 5：installed-state 产品面

状态：`持续推进中，主要读写闭环已到位`

已经完成：

- installed-state 读取
- doctor / low-risk repair
- baseline capture 与 retained history
- governance summary refresh
- waiver / apply handoff prepare

仍未完成：

- write-mode governance-source execution
- 页面内的 staged / write / verify 一体化执行

## 当前推荐优先级

建议下一轮优先做：

1. governance write-mode execution 的安全前端化
2. 已有 waiver / apply / verify 产物的页面内串联

原因：

- remote install 这一侧已经有了第一轮风险提示与恢复闭环
- 现阶段更高价值的缺口已经转移到 installed-state 治理动作的 write-mode 落地

## 简短结论

如果只需要一句话概括当前项目状态：

- `frontend/backend interaction` 已经足够支撑真实浏览、教学和第一轮执行闭环
- `remote install` 已经具备 trust、policy gate、approval、retry、cleanup、rollback
- `installed-state governance` 仍然差最后一段 write-mode 执行产品化

当前下一轮规划见 [frontend-governance-write-mode-iteration.md](./frontend-governance-write-mode-iteration.md)。
