# 前端 Governance Write Approval 迭代规划（已完成）

这一轮承接已经完成的 `prepare / stage / verify` 页面闭环，目标是把 write-mode 前的显式审批与 handoff 页面化，而不是直接把高风险写入塞进 UI。

## 原始目标

1. 在 governance / waiver / apply 面板里补齐 write-mode eligibility 说明
2. 生成 copy-friendly 的 write command、verify command 和 artifacts checklist
3. 用 Playwright 覆盖 `stage verified -> write handoff ready` 与 `blocked / drifted -> write handoff disabled`

## 完成情况

- 已在 waiver / apply state 中新增结构化 `write_handoff`，统一返回 write 资格、阻断原因、命令包、review artifacts、approval checklist 与 rollback hint
- 已在 skill / bundle 详情页的 waiver / apply 面板里展示 `pending / ready / blocked / drifted / completed` 五种 write 状态
- 已把 CLI `write` / `verify` 命令、planned governance source、review artifacts 与 checklist 页面化
- 已保持 repo governance source 的真实 `write` 继续 CLI-only，不从页面直接执行
- 已补充 Playwright：覆盖 `stage verified -> write handoff ready` 与篡改 staged artifact 后进入 `drifted / handoff disabled`
- 已同步 README、backend README、前后端集成文档、docs 索引与路线图，全部改成中文说明

## 验证结果

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-governance-write-approval`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
