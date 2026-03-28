# 前端 Governance Write Audit 迭代规划

## 本轮目标

把 governance write 的“交接确认”推进到“可追踪审计”，让 approval record 不再只是页面瞬时状态，而是能和当前 handoff、evidence snapshot、operator note 一起持久化。

## 已完成内容

### 1. approval record 持久化

- backend 新增 `POST /api/v1/local/state/governance/waiver-apply/approval`
- approval record 会和 target root、report、write handoff 指纹、operator note、evidence snapshot 一起持久化到治理快照目录
- 页面内保留 CLI-only write 边界，approval record 只负责审批留痕和交接，不负责直接写 repo source

### 2. audit timeline / evidence archive

- waiver / apply state 现在会返回 `approval_audit`
- 页面会展示 current approval record、records path、markdown path 和历史 timeline
- 当 handoff 重新 stage / verify / write 导致指纹变化时，旧 approval record 会自动转入历史

### 3. Playwright

- 已覆盖 `approval persisted -> audit trail visible`
- 已覆盖重新 stage 后旧 approval record 变成历史，再继续进入 post-write evidence 刷新路径

## 验收结果

- approval 不再只保存在浏览器 localStorage
- 页面可以看到结构化 audit record，而不仅是一次性的提示文案
- README 与相关中文文档已同步说明 approval、write、audit 三者关系

## 验证结果

- `python -m py_compile backend/app/repository.py backend/app/main.py scripts/check_python_market_backend.py`
- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-governance-write-audit`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`

## 完成说明

本规划已于 `2026-03-28` 完成。按当前协作规则，下一轮规划已切换到 `frontend-docs-action-execution-iteration.md`，本文件在完成记录保留后可以删除。
