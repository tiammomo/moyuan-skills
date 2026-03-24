# Skills 文档总览

`docs/` 面向人的学习与维护，而 `skills/` 面向 agent 的实际触发与执行。

如果你希望快速知道这个仓库该怎么读，按下面顺序就够了：

1. [teaching/README.md](./teaching/README.md)
2. [skill-learning-guide.md](./skill-learning-guide.md)
3. [skill-quickstart.md](./skill-quickstart.md)
4. [skill-spec.md](./skill-spec.md)
5. [skill-authoring.md](./skill-authoring.md)
6. [progressive-disclosure.md](./progressive-disclosure.md)
7. [harness-engineering.md](./harness-engineering.md)
8. [skill-future-roadmap.md](./skill-future-roadmap.md)

## 当前文档

- [teaching/README.md](./teaching/README.md)
  课程化教学入口，串起整个仓库的学习顺序、模块目标和实践路径
- [project-improvement-plan.md](./project-improvement-plan.md)
  规划这个项目下一步该如何继续完善
- [dev-setup.md](./dev-setup.md)
  本地开发环境与依赖准备说明
- [repo-commands.md](./repo-commands.md)
  仓库常用命令索引
- [skill-learning-guide.md](./skill-learning-guide.md)
  讲清楚这个仓库的学习顺序，以及三个教学型 skill 应该怎么配合看
- [skill-quickstart.md](./skill-quickstart.md)
  面向“先做一个最小 skill 再逐步完善”的路径
- [skill-spec.md](./skill-spec.md)
  仓库级结构规范和校验要求
- [skill-authoring.md](./skill-authoring.md)
  如何从 0 到 1 设计、搭建和维护一个 skill
- [skill-design-template.md](./skill-design-template.md)
  可以直接复制使用的设计表模板
- [progressive-disclosure.md](./progressive-disclosure.md)
  如何切分上下文层级、控制知识加载成本
- [harness-engineering.md](./harness-engineering.md)
  如何把 skill 放进更大的 agent harness 里设计
- [skill-future-roadmap.md](./skill-future-roadmap.md)
  对未来 skills 演进路径的阶段性判断
- [release-note-writer.md](./release-note-writer.md)
  第一份真实示范型业务 skill 的仓库级说明
- [issue-triage-report.md](./issue-triage-report.md)
  轻量业务案例，展示 CSV 输入到 triage 报告的完整链路
- [incident-postmortem-writer.md](./incident-postmortem-writer.md)
  更偏安全敏感的业务案例，展示 postmortem 生成与审阅边界
- [harness-prototypes.md](./harness-prototypes.md)
  tool contract、safety gate、automation 三类原型说明

## Teaching 目录

`docs/teaching/` 专门用于讲解整个项目的学习内容，当前包含：

- [teaching/01-learning-map.md](./teaching/01-learning-map.md)
  整体学习地图，帮助读者建立阶段化认知
- [teaching/02-read-the-repo.md](./teaching/02-read-the-repo.md)
  讲解这个仓库应该怎么阅读
- [teaching/03-build-your-first-skill.md](./teaching/03-build-your-first-skill.md)
  带读者完成第一次 skill 实战
- [teaching/04-progressive-disclosure-workshop.md](./teaching/04-progressive-disclosure-workshop.md)
  带读者做一次渐进式披露重构练习
- [teaching/05-harness-roadmap.md](./teaching/05-harness-roadmap.md)
  从 skill 过渡到 harness engineering 的学习路线
- [teaching/06-exercises-and-capstone.md](./teaching/06-exercises-and-capstone.md)
  把教学目录进一步落到练习题和 capstone 项目
- [teaching/07-case-gradient.md](./teaching/07-case-gradient.md)
  讲解三个真实业务案例应该如何按梯度学习
- [teaching/08-evals-and-prototypes.md](./teaching/08-evals-and-prototypes.md)
  讲解 eval harness 与 harness prototypes 的学习路径

如果你的目标是 onboarding 新成员或把仓库变成课程内容，建议优先从 `teaching/` 开始。
