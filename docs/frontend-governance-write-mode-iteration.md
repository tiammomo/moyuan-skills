# 前端 Governance Write-Mode 迭代规划

这一轮迭代承接已经完成的 installed-state governance summary、waiver / apply handoff prepare，以及 remote policy / rollback 首版闭环。

## 目标

把治理链路里仍然停留在 CLI-only 的 write-mode execution 再往前推一步，让前端不只停在“生成 handoff 包”，而是能够更清楚地展示 staged / write / verify 三段动作的边界、风险与执行状态。

## 范围

### 1. 补齐 write-mode 前的安全上下文

- 在现有 governance / waiver / apply 面板中补齐 staged、write、verify 的状态说明
- 明确哪些动作仍然要求显式人工确认
- 保持高风险写入动作默认只作用在明确 target root 或 governance 输出目录

### 2. 增加第一条 write-mode frontend handoff

- 为 staged execution、write execution 或 verify execution 中至少一条主路径补齐 backend job 入口
- 在前端页面里展示 job summary、artifacts、blocked reason 与 follow-up
- 保持 write-mode 仍然是可解释、可撤回、可验证的渐进式动作，而不是“黑盒一键执行”

### 3. 扩展 Playwright

- 验证至少一条 governance staged / write / verify 流程
- 验证至少一条 blocked 或 manual-review 路径
- 验证执行后页面能够刷新并给出下一步 follow-up

## 验收标准

- 前端能展示至少一条治理 write-mode 相关执行链路
- README、路线图和集成文档能准确说明 staged / write / verify 当前覆盖范围
- Playwright 覆盖至少一条 governance write-mode 主路径

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-governance-write-mode`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
