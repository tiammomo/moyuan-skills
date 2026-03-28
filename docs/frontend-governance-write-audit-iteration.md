# 前端 Governance Write Audit 迭代规划

## 背景

当前页面已经具备 write handoff、approval capture 和 post-write evidence pack，但 approval 还只保存在浏览器本地，无法沉淀成真正可追溯的 audit record。

## 目标

把 governance write 的最后一段“交接确认”推进到“可追踪审计”：

- approval record 持久化
- evidence archive 可回看
- 页面能展示 audit timeline

## 范围

### 1. approval record 持久化

- 把 approval 与 target root、report、write handoff 关联起来
- 支持记录 captured_at、operator note、evidence snapshot
- 明确页面内记录与 CLI write 之间的责任边界

### 2. audit timeline / evidence archive

- 页面展示最近一次 handoff 的审批与验证时间线
- 页面能回看关键 evidence 摘要，而不是只看当前状态
- 明确 drift、重新 stage、重新 verify 后如何生成新的审计记录

### 3. Playwright

- 覆盖 `approval persisted -> audit trail visible`
- 覆盖重新 stage 后旧 approval 失效或转历史记录的路径

## 验收标准

- approval 不再只保存在浏览器 localStorage
- 页面可以看到结构化 audit record，而不仅是一次性的提示文案
- README 与相关中文文档能准确说明 approval、write、audit 三者关系

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-governance-write-audit`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
