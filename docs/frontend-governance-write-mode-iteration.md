# 前端 Governance Write-Mode 迭代规划

## 状态

已完成（2026-03-28）

## 本轮完成

- waiver / apply 面板补齐了 `prepare / stage / verify` 三个前端可执行入口
- 页面内已经能展示 latest report、stage artifact、verification 状态和 CLI follow-up
- `write` 仍然明确保持为 CLI-only，不从页面直接写 repo governance source
- Windows 下的 staged artifact 文件名改成了短名 + hash，避免超长路径导致 stage 失败
- Playwright 补上了 `prepare -> stage -> verify` 主路径验证
- README、backend/README、前后端集成文档、路线图和 docs 索引都已同步为中文说明

## 验证结果

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-governance-write-mode`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`

## 结论

这一轮已经把 governance write-mode 前的安全边界说明、safe stage、refresh verify 和页面反馈链路补齐，可以切换到下一轮关于显式审批与 write-mode handoff 的规划。
