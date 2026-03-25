# 第一个 Skill 实战

这篇内容不是讲概念，而是带你完成第一次实战。

## 目标

完成后，你应该能交付：

- 一个 skill 名称
- 一条合格的 `description`
- 一个最小 `SKILL.md` 结构
- 一份资源分层判断

## 步骤 1：先选一个窄任务

不要一开始做“万能助手”。

更适合练手的是：

- 某一类文档处理
- 某一类报告生成
- 某一类结构检查

练习标准：

- 这个任务能用一句话说清
- 至少能想出 3 条真实用户原话

## 步骤 2：先写 `description`

先不要写正文，先写下面这句：

- 这个 skill 做什么
- `Use when ...` 它在什么情况下触发

如果这句写不清，说明 skill 还太宽。

## 步骤 3：画出目录分层

在动手前先决定：

- 什么留在 frontmatter
- 什么留在 `SKILL.md`
- 什么放进 `references/`
- 什么放进 `scripts/`
- 什么放进 `assets/`

推荐直接配合：

- [../skill-design-template.md](../skill-design-template.md)
- [../../skills/build-skills/assets/skill-design-canvas.md](../../skills/build-skills/assets/skill-design-canvas.md)

## 步骤 4：只做最小 `SKILL.md`

先只保证这些部分存在：

- `## Safety First`
- `## Task Router`
- `## Progressive Loading`
- `## Default Workflow`

你的第一个 skill，不需要一开始就很大。

一个适合新人的最小目标是：

- 能触发
- 能路由
- 能说明风险边界
- 能让后续 checker 接得上

## 步骤 5：做一次复盘

问自己三个问题：

1. skill 会不会被正确触发
2. `SKILL.md` 会不会已经太长
3. 有没有一段内容其实更适合做成脚本

## 练习作业

请尝试自己完成一份：

- 名称
- `description`
- `Task Router`
- 分层方案

如果你能完成这四项，就已经真正进入这个仓库的实践阶段了。

## 完成定义

对于第一次练手，不要求你一上来把 skill 做成完整案例。

只要你能交付下面这组最小产物，就已经算完成：

- 一个合理的名字
- 一条合格的 `description`
- 带四个核心 section 的 `SKILL.md`
- 一份“哪些内容放进 `references/` / `scripts/` / `assets/`”的判断说明

