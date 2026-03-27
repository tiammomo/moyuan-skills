# 前端 Installed Waiver / Apply 迭代规划

这一轮迭代承接已经完成的 installed-state governance summary 能力。

## 目标

在前端补上第一版 waiver review 与 apply handoff 入口，让本地用户可以从 governance summary 继续进入具体的 waiver 跟进，而不是每一步都立刻退回到原始 CLI。

## 范围

### 1. 在前端补充 waiver review 上下文

- 从 governance summary 产物中展示最新的 waiver follow-up 动作
- 明确区分只读的 waiver review 与可写的 apply execution
- 保持 skill 详情页和 bundle 详情页都严格绑定当前 target root

### 2. 增加第一条 apply handoff 动作

- 在前端暴露至少一个面向 waiver/apply 的 refresh 或 prepare 动作
- 明确说明哪些流程仍然只能 copy-first 或需要人工复核
- 保留 write-mode apply execution 和高回滚风险流程对应的 CLI follow-up

### 3. 扩展后端代理覆盖

- 为第一条 waiver/apply 刷新链路增加 Next.js proxy route
- 保持整体 lifecycle 路由形态与 state、doctor、repair、baseline、governance 一致

### 4. 扩展 Playwright

- 验证单个 target root 可以在前端读取 waiver/apply 上下文
- 验证第一条受支持的 waiver/apply refresh 路径能在页面内完成更新
- 验证前端仍然清楚区分 governance review 和可写的 apply execution

## 验收标准

- 前端出现第一版 waiver/apply 视图或面板
- 前端可以触发至少一个 waiver/apply 相关的后端流程
- README 和集成文档能准确说明当前 waiver/apply 范围
- Playwright 覆盖至少一条 waiver/apply summary 流程

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-installed-waiver-apply`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
