# 前端 Docs Action History 迭代规划

## 背景

docs 详情页现在已经能对 allowlist action 发起 backend job，也能在页面内看到 prerequisite state、运行状态和结果摘要；但这些信息仍然停留在“当前这一次执行”，缺少可回看、可复盘的 run history 视角。

## 目标

把 docs action panel 从“能执行一次”推进到“能回看最近执行与关键产物”：

- 保留 recent runs / last-success 视图
- 让结果摘要、stdout/stderr、artifact 更容易复看
- 让 docs action execution 更接近真实的教学与运维交接入口

## 范围

### 1. recent runs

- 为 docs action 引入最近运行记录或 last-success 状态
- 区分页内瞬时状态与已完成历史
- 明确哪些结果来自当前页面执行，哪些来自最近一次成功执行

### 2. 结果复看

- 让 result summary、stdout/stderr、artifact 有更清晰的 revisit 入口
- 统一 teaching / project / skill docs 的结果展示文案
- 保持 copy-only 与 backend-job 两类 action 的边界清晰

### 3. Playwright

- 覆盖 docs action 执行后刷新或返回页面时仍可回看结果
- 覆盖 last-success 与 failed run 的页面表现差异

## 验收标准

- docs action 不只展示当前瞬时状态，还能解释最近一次执行结果
- 页面能更清楚地复看 summary、输出片段与关键 artifact
- README 与相关中文文档能准确说明 docs action history / revisit 的边界

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-docs-action-history`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
