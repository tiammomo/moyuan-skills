# Harness 设计者学习路径

这条路径面向已经不满足于“只有 skill”，而是想设计系统层的人。

## 目标

- 把 skill 和 harness 的边界想清楚
- 理解 tool contract、eval、safety gate、automation 的协同关系
- 能从一个案例 skill 推导出系统层原型

## 建议顺序

1. [05-harness-roadmap.md](./05-harness-roadmap.md)
2. [08-evals-and-prototypes.md](./08-evals-and-prototypes.md)
3. [09-project-learning-roadmap.md](./09-project-learning-roadmap.md)
4. [harness-engineering.md](../harness-engineering.md)
5. [harness-prototypes.md](../harness-prototypes.md)

## 学习重点

- 哪些约束应该写进 skill，哪些应该上移到 harness
- 哪些路径需要 baseline eval 和 regression diff
- 哪些动作必须加 safety gate
- 哪些稳定任务适合变成 automation
