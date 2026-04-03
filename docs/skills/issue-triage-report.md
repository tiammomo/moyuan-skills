# Issue Triage Report

`issue-triage-report` 是当前案例梯度里偏轻量的真实业务 skill。

它展示的是一个很典型的团队工作流：

- 从 issue tracker 的 CSV 导出出发
- 自动生成一份 triage 会议前的摘要报告
- 在流转前做结构化 lint

## 这个案例为什么重要

它是一个很好的“第一份业务案例”，因为它同时具备：

- 输入契约清晰
- CSV 解析足够真实
- 输出结构标准
- 很适合做 weekly review 或 standup 准备材料

和 `release-note-writer` 相比，它更强调：

- 轻量工作流
- 数据分组逻辑
- 内部 review 场景

## 当前能力

当前支持：

1. `draft`
   从 CSV issue 导出生成 triage 报告
2. `lint`
   校验 triage 报告的结构完整性和模板残留

## 适合学习什么

通过这个 skill 最值得学习的是：

- 一个轻量业务 skill 怎样设计输入契约
- 什么时候该用 CSV 而不是 JSON
- 怎样把业务分组逻辑稳定地沉到脚本里

