# Incident Postmortem Writer

`incident-postmortem-writer` 是当前案例梯度里更偏安全敏感的一份真实业务 skill。

它展示的是：

- 如何从结构化 incident record 生成 postmortem
- 如何在生成流程里显式保留 communication guardrails
- 如何让 skill 与 future safety gate / approval flow 自然衔接

## 这个案例为什么重要

它和 `release-note-writer`、`issue-triage-report` 的区别在于：

- 风险更高
- 审阅要求更严格
- 对 harness 的依赖更明显

这使它非常适合拿来讲：

- 为什么 skill 本身不该承担全部安全职责
- 为什么 postmortem 这类文档需要 safety gate 和 approval

## 当前能力

当前支持：

1. `draft`
   从 incident JSON 生成 postmortem 草稿
2. `lint`
   校验 postmortem 的章节、元数据和占位符残留

## 适合学习什么

通过这个 skill 最值得学习的是：

- 安全敏感业务 skill 怎样写 `Safety First`
- timeline、action items、follow-up risks 这类结构化内容怎样进入模板
- 为什么 postmortem 这类输出天然适合接 safety gate

