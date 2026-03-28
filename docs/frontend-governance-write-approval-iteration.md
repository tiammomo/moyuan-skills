# 前端 Governance Write Approval 迭代规划

这一轮承接已经完成的 `prepare / stage / verify` 页面闭环，下一步聚焦 write-mode 前的显式审批与 handoff。

## 目标

把当前仍然停留在 CLI-only 的 write-mode 再往前推进半步：不是直接在页面里执行高风险写入，而是把“什么时候能写、写前必须确认什么、写完怎么验证”做成前端可读、可检查、可交接的流程。

## 范围

### 1. write-mode 审批上下文

- 在 governance / waiver / apply 面板里补齐 write-mode eligibility 说明
- 区分 `stage verified`、`blocked`、`drifted` 三种状态下的 write 资格
- 明确哪些条件仍然必须人工确认

### 2. write handoff pack

- 页面生成 copy-friendly 的 write command 和 artifacts checklist
- 展示预计写入目标、diff 来源、verify 命令和 rollback 提示
- 保持真正的 write 动作继续 CLI-only

### 3. Playwright

- 覆盖一条 `stage verified -> write handoff ready` 的页面路径
- 覆盖一条 `blocked / drifted -> write handoff disabled` 的页面路径

## 验收标准

- 页面能清楚解释什么时候可以进入 write-mode
- README 和集成文档能准确说明 write 仍为 CLI-only，但 handoff 已页面化
- Playwright 至少覆盖一条可进入 handoff 的路径和一条被阻止的路径

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-governance-write-approval`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
