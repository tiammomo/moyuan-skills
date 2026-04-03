# API Change Risk Review

这是一个更偏 tool-heavy / multi-step 的真实业务 skill。

它和已有案例的主要区别是：

- 先做 deterministic diff
- 再做 review draft
- 最后做 lint 和 rollout review

所以它比单纯“结构化输入 -> 文档输出”的 skill 更接近真实平台治理流程。

## 这个 skill 教什么

- 什么时候应该把“比较逻辑”上移到脚本，而不是让 agent 临场总结
- 怎样把 API diff 翻译成平台或架构评审文档
- 怎样把 rollout checks、migration notes、open questions 写成 review artifact

## 主要命令

```text
python skills/api-change-risk-review/scripts/api_change_risk_review.py diff before.json after.json diff.json
python skills/api-change-risk-review/scripts/api_change_risk_review.py draft diff.json out/api-risk-review.md
python skills/api-change-risk-review/scripts/api_change_risk_review.py lint out/api-risk-review.md
```

## 适合和哪个案例对照看

- 和 `release-note-writer` 对照：
  看“面向外部表达”的文档和“面向内部评审”的文档有什么不同。
- 和 `incident-postmortem-writer` 对照：
  看“风险评审”与“事后复盘”都怎样把安全边界拉高。

## 为什么它重要

这个案例能把仓库的下一阶段方向讲得更清楚：

- skill 不只是写文档
- skill 也可以先做 deterministic tool step，再进入 review flow
- 当 deterministic step 越来越关键时，它就越来越接近 harness 的 tool contract
