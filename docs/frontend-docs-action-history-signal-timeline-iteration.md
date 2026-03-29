# 前端 Docs Action History Signal Timeline 迭代规划

## 背景

docs action 现在已经具备：

- allowlist backend 执行
- recent runs compare / filter
- run diff summary
- inline diff excerpts
- section diff 状态与 quick-open handoff
- last-success 回看与 artifact / stdout / stderr drilldown

下一步的主要问题不再是“怎么解释当前选中运行和 pinned success 的差异”，而是“在 recent runs 列表里，能不能先看出哪次运行变了、变在哪一类信号上，再决定点开哪一条”。

## 目标

把 docs action panel 从“切到某次运行后才能读懂差异”推进到“在 history 列表里就能看懂主要变化信号”：

- 为 recent runs 提供变化信号 badge / timeline 提示
- 把 selected run 与 pinned success 的差异信号前移到列表层
- 减少用户逐条点开 recent runs 才能定位异常的成本

## 范围

### 1. history signal

- 为 recent runs 列表补充变化信号标签
- 区分 status、output、artifact 等差异类别
- 保持列表仍然易扫读，不堆叠过多说明

### 2. signal 与 summary 联动

- 让列表 signal 与 run diff summary、inline diff excerpts 保持一致
- 让用户可以从 history 列表直接跳到最值得查看的运行和区块
- 避免出现列表信号和详情摘要不一致的情况

### 3. Playwright

- 覆盖 recent runs signal 的显示与切换
- 覆盖 selected run、pinned success、excerpt、drilldown 之间的真实联动链路

## 验收标准

- recent runs 列表能直接表达主要变化信号
- 用户能在不逐条展开的情况下判断优先查看哪次运行
- README 与相关中文文档能准确说明 history signal timeline 的定位和边界

## 验证计划

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-docs-action-history-signal-timeline`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
