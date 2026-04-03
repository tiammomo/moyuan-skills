# 新人第一小时 Onboarding

这篇内容面向第一次进入 `moyuan-skills` 的新人。

目标不是一小时学完整个仓库，而是先建立正确的进入方式。

## 这一小时要完成什么

只完成三件事就够了：

- 看懂仓库的三层结构
- 看懂一个最小 skill 长什么样
- 跑通一条最小检查或示例命令

如果你在过程中卡在术语上，立刻插入阅读：

- [15-newcomer-faq.md](./15-newcomer-faq.md)

## 第 0 到 10 分钟：先知道仓库在干什么

先读：

1. [../../README.md](../../README.md)
2. [../README.md](../README.md)

这一步只回答三个问题：

- 仓库在教什么
- 为什么它不是传统的业务技能仓库
- `docs/`、`skills/`、`scripts/` 分别负责什么

## 第 10 到 25 分钟：先看一个最小 skill

再读：

1. [../skill-quickstart.md](../../authoring/skill-quickstart.md)
2. [03-build-your-first-skill.md](../foundations/03-build-your-first-skill.md)

这一步只回答：

- 一个最小可用 skill 需要哪些 section
- 为什么 `description` 要先写
- 为什么不要一开始就写成长文档

## 第 25 到 40 分钟：第一次看 teaching skill

再看：

1. [../../skills/build-skills/SKILL.md](../../../skills/build-skills/SKILL.md)
2. [02-read-the-repo.md](../foundations/02-read-the-repo.md)

这一步重点不是看懂所有 reference，而是先看懂：

- `SKILL.md` 怎么做路由
- 什么信息留在入口，什么信息延后加载

## 第 40 到 60 分钟：跑一条最小验证

任选一组：

```text
python scripts/check_progressive_skills.py
```

或者：

```text
python skills/release-note-writer/scripts/check_release_note_writer.py
```

跑完以后，再看：

- [../repo-commands.md](../../setup/repo-commands.md)

这样你就知道仓库不只是“能读”，也是真的“能验证”。

## 如果你今天就想做第一次小贡献

最适合新人的第一笔改动通常不是新建一个复杂 skill，而是下面这些小任务：

- 修正文档里的歧义表述
- 给某篇教学文档补一个更清楚的例子
- 给已有 skill 补一个更准确的说明链接
- 帮 README 或 teaching 目录补入口

这样的第一笔改动更容易让你先熟悉仓库结构，再进入更复杂的实现。

## 第一小时不要做什么

- 不要一开始就看所有业务案例
- 不要一开始就试图理解全部 harness 原型
- 不要第一天就给自己定“读完整个 docs/”的目标

## 第一小时结束后的理想状态

如果你已经能回答下面这些问题，就算 onboarding 成功：

- skill 和 harness 的区别是什么
- 一个最小 `SKILL.md` 至少包含哪些 section
- 这个仓库里哪类文件负责教学，哪类文件负责执行，哪类文件负责检查

## 下一步去哪

- 想继续按新人路径学：进入 [10-learner-path.md](../roles/10-learner-path.md)
- 想直接自己写一个 skill：进入 [03-build-your-first-skill.md](../foundations/03-build-your-first-skill.md)
- 想先看完整学习地图：进入 [01-learning-map.md](../foundations/01-learning-map.md)
