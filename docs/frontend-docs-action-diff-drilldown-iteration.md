# 前端 Docs Action Diff Drilldown 迭代规划

## 背景

docs action 现在已经具备：

- allowlist backend 执行
- recent runs compare / filter
- run diff summary
- last-success 回看
- artifact / stdout / stderr drilldown

下一步的主要问题不再是“能不能看懂当前运行和基线成功之间的差异”，而是“当页面已经告诉我哪里变了，能不能顺着提示直接钻到最值得看的输出片段”。

## 目标

把 docs action panel 从“能总结差异”推进到“能更直接地钻取差异细节”：

- 让 run diff summary 与 artifact / stdout / stderr drilldown 建立更清晰的联动
- 让值得优先查看的差异区域在页面上更容易定位
- 让 docs action 更接近真实排错、交接和复盘入口

## 范围

### 1. diff drilldown 提示

- 为 artifact / stdout / stderr 提供更明确的差异提示
- 明确哪些区域只是可查看，哪些区域确实与基线不同
- 保持 UI 在增加高亮后仍然可扫读

### 2. summary / drilldown 联动

- 让 run diff summary 能引导用户快速跳到需要重点查看的 drilldown
- 当某个 drilldown 没有差异时，给出清晰的稳定说明
- 避免把完整日志差异直接堆到主面板

### 3. Playwright

- 覆盖 docs action diff drilldown 的显示与切换
- 覆盖失败运行与最近成功运行之间的差异高亮链路

## 验收标准

- docs action 在显示 diff summary 后，用户能更快定位应该先点开的 drilldown
- 页面能清晰区分“有差异的输出”和“只是可回看的输出”
- README 与相关中文文档能准确说明 diff drilldown 的定位和边界

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-docs-action-diff-drilldown`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
