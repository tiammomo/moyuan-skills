# 从 Skill 到 Harness 的学习路线

这篇内容是教学目录的最后一站。

目标不是让你马上实现一个完整 harness，而是让你知道：

- skill 继续演进时，系统层会出现什么问题

## 为什么要学这一层

如果只学会写 skill，很容易遇到这些瓶颈：

- skill 越来越多，触发开始冲突
- 脚本越来越多，调用边界越来越乱
- 每次修改后，不知道有没有回归
- 高风险动作只能靠“提醒注意”

这时，问题已经不只是 skill 本身，而是外围系统。

## 你需要开始理解的 5 个概念

### 1. Trigger

系统怎样决定调用哪个 skill。

### 2. Tool Contract

工具怎样定义输入、输出、失败模式和安全边界。

### 3. State / Memory

哪些信息该跨轮保存，哪些不该保存。

### 4. Eval / Feedback

系统怎样知道自己有没有变好。

### 5. Safety / Automation

哪些动作该确认，哪些动作该编排，哪些动作必须有人 review。

## 一个最重要的学习转折

到这里，学习重点要从：

- “怎么把文档写清楚”

逐步转向：

- “怎么把整个运行系统设计清楚”

这就是 skill 和 harness 的分水岭。

## 推荐搭配阅读

- [../harness-engineering.md](../harness-engineering.md)
- [../skill-future-roadmap.md](../skill-future-roadmap.md)
- [../project-improvement-plan.md](../project-improvement-plan.md)
- [../../skills/harness-engineering/SKILL.md](../../skills/harness-engineering/SKILL.md)

## 这篇读完之后，下一步该做什么

推荐下一步不是继续看文档，而是做一份自己的小蓝图：

- 一个 skill
- 一条高风险路径
- 一个最小 eval
- 一个最小 safety gate

如果你能把这四件事连起来，你就已经开始真正进入 harness engineering 视角了。
