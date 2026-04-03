# 学习地图

这份学习地图用来回答一个问题：

- 如果我要系统学完这个仓库，最合理的路径是什么？

## 如果时间很少，先走哪条路

### 30 分钟路径

- [14-first-hour-onboarding.md](../onboarding/14-first-hour-onboarding.md)
- [02-read-the-repo.md](./02-read-the-repo.md)
- [03-build-your-first-skill.md](./03-build-your-first-skill.md)

目标：

- 先知道仓库在教什么
- 先知道一个最小 skill 长什么样

### 半天路径

- [14-first-hour-onboarding.md](../onboarding/14-first-hour-onboarding.md)
- [../skill-learning-guide.md](../../authoring/skill-learning-guide.md)
- [../skill-quickstart.md](../../authoring/skill-quickstart.md)
- [04-progressive-disclosure-workshop.md](./04-progressive-disclosure-workshop.md)

目标：

- 能自己起一个 skill 名称和 `description`
- 能判断内容该放在哪一层

### 完整路径

继续按下面五阶段走完整个仓库。

## 第一阶段：先理解项目为什么存在

先读：

- [../../README.md](../../README.md)
- [../README.md](../README.md)

这一阶段要回答：

- 这个仓库为什么从业务型 skills 转成教学型实验室
- 三条主线分别是什么
- `docs/`、`skills/`、`scripts/` 分别承担什么角色

完成标志：

- 你能用自己的话解释这个仓库的定位

## 第二阶段：先学 skill，不急着学 harness

先读：

- [../skill-learning-guide.md](../../authoring/skill-learning-guide.md)
- [../skill-quickstart.md](../../authoring/skill-quickstart.md)
- [../skill-spec.md](../../authoring/skill-spec.md)
- [../skill-authoring.md](../../authoring/skill-authoring.md)

这一阶段要回答：

- 一个 skill 为什么不是长文档
- frontmatter、`SKILL.md`、`references/`、`scripts/`、`assets/` 各放什么
- 什么叫一个可触发、可维护、可检查的 skill

完成标志：

- 你能独立画出一个 skill 的目录结构

## 第三阶段：学会渐进式披露

先读：

- [../progressive-disclosure.md](../../harness/progressive-disclosure.md)
- [../../skills/progressive-disclosure/SKILL.md](../../../skills/progressive-disclosure/SKILL.md)

这一阶段要回答：

- 为什么 skill 会膨胀
- 怎样判断一段内容应该放在哪一层
- 好的 router 应该怎么写

完成标志：

- 你能把一个臃肿 skill 拆成更清晰的层级

## 第四阶段：开始理解 harness

先读：

- [../harness-engineering.md](../../harness/harness-engineering.md)
- [../skill-future-roadmap.md](../../authoring/skill-future-roadmap.md)
- [../../skills/harness-engineering/SKILL.md](../../../skills/harness-engineering/SKILL.md)

这一阶段要回答：

- 什么属于 skill，什么属于 harness
- 为什么越成熟的 agent system 越需要 eval、state、safety、automation
- skills 的未来发展方向是什么

完成标志：

- 你能判断一个问题是该继续写 skill，还是该上移到 harness

## 第五阶段：做项目化练习

最后结合：

- [03-build-your-first-skill.md](./03-build-your-first-skill.md)
- [04-progressive-disclosure-workshop.md](./04-progressive-disclosure-workshop.md)
- [05-harness-roadmap.md](./05-harness-roadmap.md)

这一阶段要输出：

- 一个最小 skill 设计稿
- 一次渐进式重构方案
- 一份 harness 演进草图

