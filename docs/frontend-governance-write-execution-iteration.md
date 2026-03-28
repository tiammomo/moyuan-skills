# 前端 Governance Write Execution 迭代规划

## 本轮目标

把已经页面化的 `write handoff` 再往前推进半步，不让页面直接执行高风险 write，而是把“谁确认、确认后怎么执行、执行后如何留痕”做成可读、可追踪的前端交接流程。

## 已完成内容

### 1. approval capture

- waiver / apply 面板新增显式 approval capture
- 明确说明这个勾选只记录浏览器内的交接确认，不会绕过 CLI-only write 边界
- approval 状态与 handoff readiness 绑定，只有 `ready / completed` 时才开放确认

### 2. write 后证据收口

- write handoff 新增 evidence pack
- evidence pack 会聚合 apply / execute / verify / target root / stage directory 等关键证据
- 页面能区分 `pre_write_ready`、`post_write_verified`、`post_write_pending`、`post_write_drifted` 等状态

### 3. Playwright

- 已覆盖 `approval captured -> CLI write to mirror target -> post-write evidence refreshed`
- 用镜像 governance target root 验证 write/verify/report 链路，避免测试直接写仓库治理源文件

## 验收结果

- 页面能清楚解释 approval capture 只是交接与留痕，不会绕过 CLI-only write 边界
- README、前后端集成文档、后端说明与路线图都已同步为中文说明
- Playwright 已覆盖 approval capture 路径与 post-write evidence 路径

## 验证结果

- `python -m py_compile backend/app/repository.py scripts/check_python_market_backend.py`
- `python scripts/check_python_market_backend.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`

## 完成说明

本规划已于 `2026-03-28` 完成。按当前协作规则，下一轮规划已切换到 `frontend-governance-write-audit-iteration.md`，本文件在完成记录保留后可以删除。
