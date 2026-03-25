# 整个项目的学习路线与演进图

这篇内容专门用来回答两个问题：

- 如果把 `moyuan-skills` 当成一个完整项目，而不是几篇零散文档，我应该怎么学
- 如果把它当成一个长期演进的实验仓库，下一阶段最值得继续补什么

## 先用四层视角看整个仓库

理解这个项目，最稳的方式不是一篇篇文档顺着读，而是先把它看成四层：

1. 学习层
   入口在 `docs/` 和 `docs/teaching/`，负责解释方法论、课程顺序和练习路径。
2. 案例层
   入口在 `skills/`，负责把抽象方法论落到可触发、可检查的 skill 实例。
3. 校验层
   入口在 `scripts/` 和各 skill 自带的 checker，负责把仓库约定变成可回归检查。
4. 系统层
   入口在 `examples/eval-harness/` 与 `examples/harness-prototypes/`，负责把 skill 往 harness engineering 的方向推进。

如果你能先建立这四层心智模型，后面看任何文档都不容易迷路。

## 按角色进入这个项目

### 如果你是第一次接触这个仓库

建议顺序：

1. [14-first-hour-onboarding.md](./14-first-hour-onboarding.md)
2. [README.md](../../README.md)
3. [01-learning-map.md](./01-learning-map.md)
4. [02-read-the-repo.md](./02-read-the-repo.md)
5. [03-build-your-first-skill.md](./03-build-your-first-skill.md)

你的目标不是一口气看全，而是先理解：

- 仓库在教什么
- skill 为什么要做渐进式披露
- 一份最小可用 skill 应该长什么样

### 如果你准备自己写 skill

建议顺序：

1. [03-build-your-first-skill.md](./03-build-your-first-skill.md)
2. [../skill-authoring.md](../skill-authoring.md)
3. [04-progressive-disclosure-workshop.md](./04-progressive-disclosure-workshop.md)
4. [07-case-gradient.md](./07-case-gradient.md)

你的重点是学会：

- 如何收窄触发边界
- 如何决定内容放在 `SKILL.md`、`references/`、`scripts/` 还是 `assets/`
- 如何通过真实案例判断“好结构”和“坏结构”的差别

### 如果你是仓库维护者

建议顺序：

1. [12-maintainer-path.md](./12-maintainer-path.md)
2. [08-evals-and-prototypes.md](./08-evals-and-prototypes.md)
3. [../repo-commands.md](../repo-commands.md)
4. [../dev-setup.md](../dev-setup.md)

你的重点是学会：

- 哪些约定已经被 lint 化
- 哪些规则还只是文档建议
- 哪些内容下一步应该上移到 harness 层

### 如果你关心 harness engineering

建议顺序：

1. [05-harness-roadmap.md](./05-harness-roadmap.md)
2. [08-evals-and-prototypes.md](./08-evals-and-prototypes.md)
3. [../harness-engineering.md](../harness-engineering.md)
4. [../harness-prototypes.md](../harness-prototypes.md)

你的重点不是“再写一个 skill”，而是判断：

- 哪些 skill 已经暴露出 tool contract 的需求
- 哪些路径需要 safety gate
- 哪些周期性任务应该走 automation

## 当前已经补到哪一层

截至当前版本，这个仓库已经具备：

- 一套可串讲整个项目的 `docs/teaching/` 教学目录
- 三个教学型 skill，分别覆盖 authoring、progressive disclosure、harness thinking
- 四个业务案例 skill，形成轻量、发布型、tool-heavy、到安全敏感的案例梯度
- 一套带 grader、baseline、diff 和 report 的 eval harness
- 三类带 schema、checker、stub 的 harness 原型：tool contract、safety gate、automation
- 一条真正能运行的 runtime blueprint，用来把 automation、tool contract、gate 串成一次可报告的 run
- 一套仓库级 lint，用来检查结构、router、teaching 完整性、fixture 与 `openai.yaml` 一致性

这说明项目已经从“方法论文档集合”走到了“可学习、可验证的实验仓库”。

## 还需要继续补什么

下一阶段最值得继续补的，不是再堆更多文档，而是把下面几类能力继续做深：

1. 角色化教学
   把初学者、作者、维护者、harness 设计者的学习入口分得更清楚。
2. 更难的真实案例
   新增 1 到 2 个 tool-heavy、multi-step、带 review gate 的业务 skill。
3. 更强的 lint
   把 trigger 质量、description 质量、示例链接、反模式 fixture 继续纳入检查。
4. 更强的 eval
   增加 baseline、回归 diff、按 skill 聚合评分和失败样例归档。
5. 更可执行的 harness
   让当前原型从静态规范继续前进到 schema、checker 和 runtime stub。
6. 更好的协作体验
   补贡献指南、开发依赖、文档 lint 和版本迭代机制。

## 怎么把“学习”和“演进”放到一起看

这也是这个教学模块最重要的一点：学习路线和项目路线其实是同一张图的两面。

- 学习路线回答的是“读者应该先学什么，再练什么”
- 项目路线回答的是“仓库应该先补什么，再系统化什么”

如果一个项目只能学习、不能继续演进，它最终会变成静态教材。
如果一个项目只能演进、不能被新人快速学会，它最终会变成只有作者自己能维护的私有结构。

`moyuan-skills` 真正想做的是把这两件事绑在一起：

- 用 teaching 目录保证它可学
- 用案例和 checker 保证它可验证
- 用 eval 和 harness prototype 保证它可继续演进

## 推荐的下一跳

如果你刚看完这篇，接下来最推荐走的分支是：

- 想系统学完整个仓库：回到 [../../README.md](../../README.md)
- 想先完成新人 onboarding：进入 [14-first-hour-onboarding.md](./14-first-hour-onboarding.md)
- 想开始实操写 skill：进入 [03-build-your-first-skill.md](./03-build-your-first-skill.md)
- 想理解案例梯度：进入 [07-case-gradient.md](./07-case-gradient.md)
- 想理解系统层：进入 [08-evals-and-prototypes.md](./08-evals-and-prototypes.md)
- 想直接按角色进入：进入 [10-learner-path.md](./10-learner-path.md)、[11-skill-author-path.md](./11-skill-author-path.md)、[12-maintainer-path.md](./12-maintainer-path.md) 或 [13-harness-builder-path.md](./13-harness-builder-path.md)
