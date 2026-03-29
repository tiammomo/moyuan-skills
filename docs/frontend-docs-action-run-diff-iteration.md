# 前端 Docs Action Run Diff 迭代规划

## 背景

docs action 现在已经具备：

- allowlist backend 执行
- recent runs compare / filter
- last-success 回看
- artifact / stdout / stderr drilldown

下一步的主要问题不再是“能不能切换和筛选历史运行”，而是“当我已经选中一条运行时，页面能不能直接告诉我它和基线相比变了什么”。

## 目标

把 docs action panel 从“能筛选和切换历史运行”推进到“能更结构化地解释运行差异”：

- 让 selected run 与 last-success 之间有清晰的 diff summary
- 让 artifact / output 的变化提示更容易扫读
- 让 docs action 更接近真实交接、复盘和排错入口

## 范围

### 1. run diff summary

- 为 selected run 与 last-success 生成轻量级差异摘要
- 明确哪些字段没有变化、哪些字段值得重点关注
- 保持 UI 在信息增加后仍然可扫读

### 2. drilldown 联动

- 让 diff summary 与 artifact / stdout / stderr drilldown 联动
- 当没有 last-success 或无法形成 diff 时，给出清晰的降级说明
- 避免把完整日志差异直接堆进主面板

### 3. Playwright

- 覆盖 docs action diff summary 的显示与切换
- 覆盖失败运行与最近成功运行之间的差异提示链路

## 验收标准

- docs action 在选中历史运行后，能更直观地说明它与 last-success 的差异
- 用户不需要逐段翻日志，也能快速定位应该先看哪块输出
- README 与相关中文文档能准确说明 diff summary 的定位和边界

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-docs-action-run-diff`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
