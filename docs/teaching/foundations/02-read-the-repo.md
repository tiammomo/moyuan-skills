# 如何阅读整个项目

这篇内容解决的是：

- 第一次进仓库时，应该先看哪里，后看哪里

## 第一次不要做的三件事

- 不要一上来就顺着目录把所有文档读完
- 不要第一天就试图理解所有 harness 细节
- 不要只看 `skills/` 或只看 `docs/`

## 先看三层结构

这个仓库可以先粗分成三层：

### 第一层：项目说明层

文件：

- [../../README.md](../../README.md)
- [../README.md](../README.md)

这层解决“项目是什么、为什么这样组织”。

### 第二层：方法论文档层

文件：

- [../skill-authoring.md](../../authoring/skill-authoring.md)
- [../skill-spec.md](../../authoring/skill-spec.md)
- [../progressive-disclosure.md](../../harness/progressive-disclosure.md)
- [../harness-engineering.md](../../harness/harness-engineering.md)

这层解决“设计原则是什么”。

### 第三层：教学型 skill 层

文件：

- [../../skills/build-skills/SKILL.md](../../../skills/build-skills/SKILL.md)
- [../../skills/progressive-disclosure/SKILL.md](../../../skills/progressive-disclosure/SKILL.md)
- [../../skills/harness-engineering/SKILL.md](../../../skills/harness-engineering/SKILL.md)

这层解决“一个真正可触发的 teaching skill 应该长什么样”。

## 推荐阅读顺序

推荐这样读：

1. 先看项目首页
2. 再看 `docs/README.md`
3. 再看 `skill-spec.md`
4. 再看 `skill-authoring.md`
5. 再看三个 skill 的 `SKILL.md`
6. 最后再看 harness 相关文档

这样读的原因是：

- 先知道项目定位
- 再知道规则
- 再看实例
- 最后理解未来方向

如果你只给自己 1 小时，先缩成这条：

1. [14-first-hour-onboarding.md](../onboarding/14-first-hour-onboarding.md)
2. [../../README.md](../../README.md)
3. [../skill-quickstart.md](../../authoring/skill-quickstart.md)
4. [../../skills/build-skills/SKILL.md](../../../skills/build-skills/SKILL.md)

## 阅读时最容易忽略的点

### 不要只看 `docs/`

如果只看 `docs/`，你会知道“应该怎么做”，但未必能看到“实际 skill 入口长什么样”。

### 不要只看 `skills/`

如果只看 `skills/`，你会看到最终形态，但不一定理解背后的设计原则。

### 不要跳过 `scripts/`

仓库里的检查脚本决定了哪些规范是“真的被执行”的。

对于这个项目来说，教学和工程约束是同时存在的。

## 一个推荐的阅读动作

每读完一层，都回答一个问题：

- 我现在看到的是“解释层”，还是“执行层”？

如果你总能分清这件事，就不容易把仓库看乱。

