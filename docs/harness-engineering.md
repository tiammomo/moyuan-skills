# Harness Engineering 设计笔记

这篇文档讨论的是：当 skill 从“可复用知识包”继续往前长时，外围系统应该怎么设计。

## 什么是 Harness Engineering

你可以把 harness engineering 理解成“围绕 agent 工作流搭系统”的能力。

它关注的不只是 prompt，也不只是 tool，而是整条运行链：

- 任务怎样进入系统
- skill 怎样被触发
- tool 怎样被约束
- state 和 memory 怎样被维护
- eval 怎样持续反馈
- safety gate 怎样拦住危险动作
- automation 怎样让系统可以长期运行

## Skill 和 Harness 的边界

一个很实用的判断方法是：

- skill 更像一个按需加载的能力包
- harness 更像让这些能力包稳定运行的操作系统外层

通常来说：

- skill 负责领域知识、任务路由、局部工作流
- harness 负责 tool contract、状态管理、评测闭环、审计、安全和自动化

## Harness 的六个基础原语

### 1. Trigger

系统如何判断什么时候调用哪个 skill、哪个工具、哪条路径。

### 2. Tool Contract

工具的输入、输出、错误语义、幂等性、权限边界是什么。

### 3. State / Memory

哪些信息只在当前 run 生效，哪些需要跨 run 记住，哪些根本不该记。

### 4. Eval / Feedback

系统如何知道自己这次做得好不好，以及下一次应该修哪里。

### 5. Safety Gate

哪些动作需要确认、审批、dry-run、diff、审计或者人工 review。

### 6. Automation / Scheduling

哪些任务是一次性的，哪些应该被编排成持续运行的流程。

## 为什么 skill 仓库也要讨论 harness

因为很多团队在做 skill 时，会慢慢遇到这些问题：

- skill 越来越多，触发开始互相重叠
- 工具越来越多，调用边界开始混乱
- 成功与失败没有稳定的评测标准
- 每次问题都靠人工复盘，没有持续反馈

当这些问题出现时，继续往 `SKILL.md` 里加说明通常是无效的。
真正需要补的是 harness。

## 一个好 harness 对 skill 的要求

如果未来准备上 harness，那么今天的 skill 最好就满足：

- frontmatter 边界明确
- `SKILL.md` 路由清晰
- `references/` 主题分明
- `scripts/` 有稳定 CLI 或检查入口
- 危险路径有默认关闭的 guardrail

这样未来把部分职责上移到 harness 时，迁移成本会低很多。

## 从单个 skill 走向 harness 的常见路径

很多团队会经历下面这条路线：

1. 先写 prompt 和少量脚本
2. 再沉淀成可复用 skill
3. 再补渐进式披露，控制上下文
4. 再补统一检查和 eval
5. 再补 orchestration、memory、safety gate
6. 最后形成一个更像 agent operating system 的东西

## 三个典型误区

### 1. 以为 skill 可以代替 harness

结果：

- 过多系统职责被塞到文本里
- 规则越来越长，行为却仍然不稳定

### 2. 以为 harness 可以代替 skill

结果：

- 系统有了 orchestration，但没有清晰的领域知识入口
- 每次都在运行时重新猜流程

### 3. 只做 tool，不做 eval

结果：

- 能运行，但不知道质量有没有提升
- 回归只能靠体感

## 一个实用的设计问题单

设计一个 skill 周边 harness 时，建议至少回答这些问题：

1. 系统如何知道该调用这个 skill？
2. skill 内部哪些路径未来应该变成外部 orchestration？
3. 哪些动作必须有 dry-run、diff 或人工确认？
4. 失败后要留下哪些 trace 或 artifact？
5. 如何验证 skill 版本升级后没有回归？
6. 哪些信息应该进入 memory，哪些不应该？

## 结论

这个仓库把 harness engineering 放进主线，不是因为 skill 不重要了，而是因为：

- 越成熟的 agent system，越需要把 skill 放进一个更可观测、可评估、可编排的运行框架里

因此，做 skill 时就开始思考 harness，不是过度设计，而是提前建立正确边界。

## 当前仓库里的原型落点

当前仓库已经补了三类最小原型：

- tool contract
- safety gate
- automation

对应说明见：

- [harness-prototypes.md](./harness-prototypes.md)

