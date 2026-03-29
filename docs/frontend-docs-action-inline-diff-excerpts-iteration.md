# 前端 Docs Action Inline Diff Excerpts 迭代规划

## 背景

docs action 现在已经具备：

- allowlist backend 执行
- recent runs compare / filter
- run diff summary
- last-success 回看
- artifact / stdout / stderr drilldown
- section diff 状态与 quick-open handoff

下一步的主要问题不再是“能不能把用户带到正确的 drilldown”，而是“在用户还没点开完整输出之前，能不能先给出足够短、足够有用的差异摘录”。

## 目标

把 docs action panel 从“能把用户带到 drilldown”推进到“能先在 summary 层给出可扫描的差异摘录”：

- 为 stdout / stderr / artifact 提供更短的 inline diff excerpt
- 让 selected run 与 pinned success 的差异先以摘要形式出现在主面板
- 让用户更快判断是继续展开完整输出，还是已经拿到足够的排障线索

## 范围

### 1. 摘录生成

- 为 stdout / stderr 提供可控长度的差异摘录
- 为 artifact 提供关键字段级的 before / after 摘要
- 避免把整段日志直接塞回 summary 区域

### 2. 面板联动

- 让 excerpt 与 run diff summary、section diff 状态保持一致
- 当 excerpt 已经足够说明问题时，减少用户进入完整 drilldown 的次数
- 当 excerpt 不足时，仍然保持 drilldown 入口清晰可达

### 3. Playwright

- 覆盖 excerpt 展示、run 切换、filter 切换和 drilldown 衔接
- 覆盖失败运行与 pinned success 之间的摘要级 before / after 对照

## 验收标准

- docs action 在 result summary 区域能直接展示可扫描的差异摘录
- 用户能区分“已经足够定位问题的摘录”和“需要继续展开完整输出的情况”
- README 与相关中文文档能准确说明 excerpt 的定位与边界

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-docs-action-inline-diff-excerpts`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
