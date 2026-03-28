# 前端 Docs Action Execution 迭代规划

## 背景

当前 docs 详情页已经能展示 action panel、命令顺序、前置条件和预期产物，但它仍然更像“执行说明书”，还不是可交互的执行入口。

## 目标

把 docs action panel 从“只会解释”推进到“可以协助执行和跟踪”：

- action run / copy / prereq check 更结构化
- 页面内能看到 action 的运行状态和结果摘要
- docs 页面和 backend execution 能形成统一的交互语言

## 范围

### 1. docs action 状态化

- 为 docs action 引入结构化状态，而不是只展示静态命令
- 区分 ready、blocked、running、succeeded、failed 等状态
- 明确 action 是否只是 copy 指令，还是可以触发 backend 执行

### 2. prereq 与结果摘要

- 页面展示 prerequisite check 结果
- 页面在 action 完成后展示结果摘要和关键产物
- 统一文案风格，避免 docs action panel 和 skills / bundles 详情页交互割裂

### 3. Playwright

- 覆盖 docs action panel 的真实执行或模拟执行路径
- 覆盖 prerequisite blocked 与 retry 的交互路径

## 验收标准

- docs action panel 不再只是静态说明
- 页面能解释 action 当前状态、前置条件和执行结果
- README 与相关中文文档能准确说明 docs action execution 的交互边界

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-docs-action-execution`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
