# 前端 Remote Policy / Rollback 迭代规划

这一轮迭代承接已经完成的 remote registry install、trust summary、explicit approval、retry、cleanup，以及 installed-state waiver / apply handoff 首版能力。

## 目标

把 remote install 的高风险部分继续产品化，让前端不仅能“跑一次远端安装”，还能更清楚地解释为什么某次远端执行被策略拦住、失败后如何回滚或清理、以及哪些恢复动作已经可以在页面内闭环。

## 范围

### 1. 补充 remote policy gating 上下文

- 在 skill / bundle 的 remote execution 卡片中补充更明确的 policy gate state
- 区分可继续执行、需要显式人工复核、已经被 lifecycle / provenance / org policy 阻断的情况
- 让失败分类不仅停留在 download / trust / installer，还能映射到更具体的 policy follow-up

### 2. 增加第一条 rollback / reconcile 主路径

- 在前端暴露至少一条远端失败后的 rollback、reconcile 或 staged cleanup 之后的恢复链路
- 明确哪些动作仍然只能 copy-first 或 CLI-only
- 保持 rollback 只覆盖低风险或已有限定作用域的 target root

### 3. 扩展后端与代理覆盖

- 如有必要，为 remote rollback 或 policy re-check 增加新的 backend job 入口
- 为新增入口补齐 Next.js proxy route
- 保持 job summary、artifacts、recovery hints 的字段形态与现有 remote execution 卡片一致

### 4. 扩展 Playwright

- 验证至少一条远端 policy gated 路径在前端能给出清楚原因
- 验证至少一条失败后 rollback / reconcile / cleanup 主路径能在页面内完成
- 验证恢复后仍能继续 retry 或回到 copy-first follow-up

## 验收标准

- 前端能展示更细粒度的 remote policy gating 状态
- 前端至少支持一条远端 rollback 或 reconcile 主路径
- README、路线图和集成文档能准确说明当前 remote 风险闭环范围
- Playwright 覆盖至少一条 policy gating + rollback / reconcile 流程

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-remote-policy-rollback`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
