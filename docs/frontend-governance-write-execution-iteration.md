# 前端 Governance Write Execution 迭代规划

这一轮承接已经完成的 `write handoff` 页面化能力，下一步聚焦真正的显式 approval capture 与 write 后审计收口。

## 目标

把当前已经能解释清楚的 write handoff 再往前推进半步：不是直接让页面偷偷执行高风险写入，而是把“谁批准、批准后怎么执行、执行后如何留痕与复核”做成前端可读、可追踪、可审计的流程。

## 范围

### 1. approval capture

- 在 governance / waiver / apply 面板里补上显式 approval capture
- 明确 operator 责任说明与高风险提示
- 把 approval 结果和 handoff 关联，避免页面只给命令、不说明责任边界

### 2. write 后审计

- 页面展示 write 后的 evidence / summary / verify 收口
- 明确 post-write refresh、持续 verify 和 drift 回溯入口
- 补充 write 后 review record 需要保留的工件

### 3. Playwright

- 覆盖一条 `approval captured -> CLI handoff acknowledged` 的页面路径
- 覆盖一条 `post-write evidence refreshed` 的页面路径

## 验收标准

- 页面能清楚解释 approval capture 只是交接与留痕，不会绕过 CLI-only write 边界
- README 和集成文档能准确说明 approval capture、post-write audit 与 handoff 的关系
- Playwright 至少覆盖一条 approval capture 路径和一条 post-write evidence 路径

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-governance-write-execution`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
