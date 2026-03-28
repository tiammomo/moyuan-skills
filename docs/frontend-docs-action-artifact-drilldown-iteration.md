# 前端 Docs Action Artifact Drilldown 迭代规划

## 背景

docs action 现在已经具备 allowlist 执行、recent runs、last-success 和结果回看；但结果仍然主要停留在摘要层，stdout/stderr 与 artifact 还缺少更清晰的 drill-down 入口。

## 目标

把 docs action panel 从“能回看最近运行”推进到“能更细地钻取输出与工件”：

- 让 stdout / stderr / artifact 更容易展开和复看
- 让 recent runs 与当前选中结果形成更清晰的联动
- 让 docs action 更接近真实教学、排错和交接入口

## 范围

### 1. artifact drill-down

- 为 docs action 的 artifact、stdout、stderr 补充更清晰的展开或切换入口
- 区分摘要信息与深度查看信息
- 保持页面结构不被大量日志淹没

### 2. recent runs 联动

- 让切换不同 recent run 时，artifact / stdout / stderr 的展示更直观
- 明确当前正在查看的是 latest run、last-success 还是某次历史运行
- 保持 copy-only 与 backend-job 的边界清晰

### 3. Playwright

- 覆盖 docs action recent run 切换后的 artifact / output 回看
- 覆盖刷新页面后继续 drill-down 的链路

## 验收标准

- docs action 不只显示摘要，还能更细地复看关键输出与工件
- recent runs 切换和结果 drill-down 的关系清楚可见
- README 与相关中文文档能准确说明 docs action artifact revisit 的边界

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-docs-action-artifact-drilldown`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
