# Teaching 目录总览

`docs/teaching/` 是这个仓库的课程化学习区。

如果说根目录 `README.md` 负责回答“这个项目是什么”，`docs/` 负责回答“有哪些方法论文档”，那么 `docs/teaching/` 负责回答：

- 应该按什么顺序学
- 每一阶段要掌握什么
- 怎样从阅读过渡到实践

## 如果你只有 1 小时

给新成员最省力的入口不是直接丢一串文档，而是先走这条短路径：

1. [14-first-hour-onboarding.md](./14-first-hour-onboarding.md)
2. [15-newcomer-faq.md](./15-newcomer-faq.md)
3. [02-read-the-repo.md](./02-read-the-repo.md)
4. [03-build-your-first-skill.md](./03-build-your-first-skill.md)
5. [10-learner-path.md](./10-learner-path.md)

## 推荐学习顺序

1. [01-learning-map.md](./01-learning-map.md)
2. [02-read-the-repo.md](./02-read-the-repo.md)
3. [03-build-your-first-skill.md](./03-build-your-first-skill.md)
4. [04-progressive-disclosure-workshop.md](./04-progressive-disclosure-workshop.md)
5. [05-harness-roadmap.md](./05-harness-roadmap.md)
6. [06-exercises-and-capstone.md](./06-exercises-and-capstone.md)
7. [07-case-gradient.md](./07-case-gradient.md)
8. [08-evals-and-prototypes.md](./08-evals-and-prototypes.md)
9. [09-project-learning-roadmap.md](./09-project-learning-roadmap.md)
10. [10-learner-path.md](./10-learner-path.md)
11. [11-skill-author-path.md](./11-skill-author-path.md)
12. [12-maintainer-path.md](./12-maintainer-path.md)
13. [13-harness-builder-path.md](./13-harness-builder-path.md)
14. [14-first-hour-onboarding.md](./14-first-hour-onboarding.md)
15. [15-newcomer-faq.md](./15-newcomer-faq.md)
16. [16-skills-market-evolution.md](./16-skills-market-evolution.md)
17. [17-market-registry-and-federation.md](./17-market-registry-and-federation.md)

## 这个目录解决什么问题

### 对初学者

帮助你快速理解：

- 什么是 skill
- 为什么这个仓库强调渐进式披露
- skill 和 harness 有什么区别

### 对实践者

帮助你完成：

- 第一个 skill 设计练习
- 一个已有 skill 的拆层重构
- 一个面向未来 harness 的思考练习

### 对维护者

帮助你统一：

- 项目教学口径
- 新成员 onboarding 路径
- 后续课程和案例的扩展结构

### 对项目 owner / curriculum 设计者

帮助你继续判断：

- 这个仓库现在已经补到了哪一层
- 下一阶段最值得补的是课程、案例、lint、eval 还是 harness
- 如何把学习路径和工程演进路线放到同一张图里

## 角色化入口

如果你已经知道自己的目标，比按编号顺序读更快的入口是：

- 初学者：从 [10-learner-path.md](./10-learner-path.md) 开始
- Skill 作者：从 [11-skill-author-path.md](./11-skill-author-path.md) 开始
- 维护者：从 [12-maintainer-path.md](./12-maintainer-path.md) 开始
- Harness 设计者：从 [13-harness-builder-path.md](./13-harness-builder-path.md) 开始
- 带新人 onboarding：从 [14-first-hour-onboarding.md](./14-first-hour-onboarding.md) 开始
- 想先补术语和常见问题：从 [15-newcomer-faq.md](./15-newcomer-faq.md) 开始
- 想理解项目为什么会继续走向 skills market：从 [16-skills-market-evolution.md](./16-skills-market-evolution.md) 开始

## 学习完成后的预期能力

完成这一组内容后，应该至少能做到：

- 看懂这个仓库每一层文件的作用
- 自己设计一个最小可用 skill
- 判断内容该放在 `SKILL.md`、`references/`、`scripts/` 还是 `assets/`
- 理解 skill 为什么会继续走向 harness engineering
- 按练习与 capstone 路径完成一次从 skill 到 harness 的完整设计演练
- 理解真实业务案例怎样形成案例梯度
- 看懂 eval harness、tool contract、safety gate、automation 原型之间的关系
- 能把整个项目按“学习层、案例层、校验层、系统层”四个维度讲清楚
