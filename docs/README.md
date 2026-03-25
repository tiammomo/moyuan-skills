# Skills 文档总览

`docs/` 面向人的学习与维护，而 `skills/` 面向 agent 的实际触发与执行。

## 新人先看这几篇

如果你是第一次进这个仓库，不要先从最长的文档开始。

建议先按这个顺序看：

1. [teaching/14-first-hour-onboarding.md](./teaching/14-first-hour-onboarding.md)
2. [teaching/README.md](./teaching/README.md)
3. [teaching/15-newcomer-faq.md](./teaching/15-newcomer-faq.md)
4. [skill-quickstart.md](./skill-quickstart.md)
5. [skill-learning-guide.md](./skill-learning-guide.md)
6. [repo-commands.md](./repo-commands.md)

如果你希望快速知道这个仓库该怎么读，按下面顺序就够了：

1. [teaching/README.md](./teaching/README.md)
2. [teaching/09-project-learning-roadmap.md](./teaching/09-project-learning-roadmap.md)
3. [skill-learning-guide.md](./skill-learning-guide.md)
4. [skill-quickstart.md](./skill-quickstart.md)
5. [skill-spec.md](./skill-spec.md)
6. [skill-authoring.md](./skill-authoring.md)
7. [progressive-disclosure.md](./progressive-disclosure.md)
8. [harness-engineering.md](./harness-engineering.md)
9. [skill-future-roadmap.md](./skill-future-roadmap.md)

## 当前文档

- [teaching/README.md](./teaching/README.md)
  课程化教学入口，串起整个仓库的学习顺序、模块目标和实践路径
- [dev-setup.md](./dev-setup.md)
  本地开发环境与依赖准备说明
- [repo-commands.md](./repo-commands.md)
  仓库常用命令索引
- [template-library.md](./template-library.md)
  说明 `templates/` 里三套模板包分别适合什么阶段
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
- [api-change-risk-review.md](./api-change-risk-review.md)
  更偏 tool-heavy 的业务案例，展示 schema diff 到风险评审文档的多步流程
- [incident-postmortem-writer.md](./incident-postmortem-writer.md)
  更偏安全敏感的业务案例，展示 postmortem 生成与审阅边界
- [harness-prototypes.md](./harness-prototypes.md)
  tool contract、safety gate、automation 三类原型说明
- [harness-runtime.md](./harness-runtime.md)
  讲解 runtime blueprint 和最小可执行 harness runtime 的设计与运行方式

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
  讲解四个真实业务案例应该如何按梯度学习
- [teaching/08-evals-and-prototypes.md](./teaching/08-evals-and-prototypes.md)
  讲解 eval harness 与 harness prototypes 的学习路径
- [teaching/09-project-learning-roadmap.md](./teaching/09-project-learning-roadmap.md)
  专门把整个项目的学习路径、当前完成度和下一阶段演进路线串起来
- [teaching/10-learner-path.md](./teaching/10-learner-path.md)
  面向初学者的最短学习路径
- [teaching/11-skill-author-path.md](./teaching/11-skill-author-path.md)
  面向 skill 作者的结构化学习路径
- [teaching/12-maintainer-path.md](./teaching/12-maintainer-path.md)
  面向维护者的仓库演进与校验路径
- [teaching/13-harness-builder-path.md](./teaching/13-harness-builder-path.md)
  面向 harness 设计者的系统层学习路径
- [teaching/14-first-hour-onboarding.md](./teaching/14-first-hour-onboarding.md)
  面向新成员的第一小时 onboarding 路径，帮助先建立正确心智模型再深入阅读
- [teaching/15-newcomer-faq.md](./teaching/15-newcomer-faq.md)
  面向新成员的术语解释与常见问题，帮助先跨过第一轮理解门槛

如果你的目标是 onboarding 新成员、把仓库变成课程内容，或者快速理解整个项目现在该怎么继续学，建议优先从 `teaching/` 开始。带新人时，建议先给 [teaching/14-first-hour-onboarding.md](./teaching/14-first-hour-onboarding.md)，再继续到 [teaching/09-project-learning-roadmap.md](./teaching/09-project-learning-roadmap.md)。
