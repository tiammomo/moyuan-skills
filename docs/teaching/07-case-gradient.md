# 案例梯度学习

这篇内容专门讲仓库里的真实业务 skill 应该怎么按梯度学习。

## 当前案例梯度

建议按下面顺序看：

1. [../../skills/issue-triage-report/SKILL.md](../../skills/issue-triage-report/SKILL.md)
2. [../../skills/release-note-writer/SKILL.md](../../skills/release-note-writer/SKILL.md)
3. [../../skills/incident-postmortem-writer/SKILL.md](../../skills/incident-postmortem-writer/SKILL.md)

## 为什么是这个顺序

### `issue-triage-report`

最适合先学，因为它更轻：

- CSV 输入简单
- 分组逻辑清楚
- 输出是典型内部报告

### `release-note-writer`

适合第二个看，因为它更强调：

- 结构化变更如何进入面向读者的文案
- highlights、breaking changes、known issues 这类发布语义

### `incident-postmortem-writer`

适合最后看，因为它最接近 harness 问题：

- 风险更高
- 审批需求更强
- 安全边界更重要

## 学习时最值得比较的维度

比较这三个 skill 时，重点看：

- 输入契约差异
- `Safety First` 的强弱差异
- 模板结构差异
- 为什么有的更适合直接进入 safety gate

