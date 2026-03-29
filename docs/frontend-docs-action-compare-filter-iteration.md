# 前端 Docs Action Compare / Filter 迭代规划

## 背景

docs action 现在已经具备：

- allowlist backend 执行
- recent runs 与 last-success 回看
- artifact / stdout / stderr drilldown

下一步的主要问题不再是“能不能回看”，而是“当一次动作跑过很多轮之后，怎样更快比较不同运行结果”。

## 目标

把 docs action panel 从“能逐次回看结果”推进到“能更高效地筛选和比较历史运行”：

- 让 recent runs 支持更清晰的状态过滤
- 让 latest / last-success / failed run 的差异更容易识别
- 让 result summary 与 drilldown 形成更明确的 compare 入口

## 范围

### 1. recent runs compare / filter

- 为 docs action recent runs 增加基础筛选能力
- 明确区分成功、失败、当前选中和 last-success
- 优先突出最近失败且值得复盘的运行

### 2. summary / drilldown 联动

- 让 result summary、artifact drilldown 和历史选择之间的联动更直观
- 补充更清晰的“当前查看来源”与状态聚合提示
- 避免面板因为历史记录增加而失去可扫读性

### 3. Playwright

- 覆盖 docs action compare / filter 的页内交互
- 覆盖 latest / failed / last-success 之间的切换与复盘

## 验收标准

- docs action 在多次 recent runs 下仍然容易筛选与比较
- 用户能快速分辨当前在看哪一次运行，以及它和 last-success 的关系
- README 与相关中文文档能准确说明 compare / filter 的定位

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-docs-action-compare-filter`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
