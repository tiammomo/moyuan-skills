# 新人常见问题

这篇内容专门回答新人第一次进入仓库时最容易卡住的问题。

如果你在 `README.md`、`docs/authoring/skill-quickstart.md` 或 `docs/teaching/` 里看到一些词不太确定含义，先看这里。

## 1. `skill` 到底是什么

在这个仓库里，skill 不是一篇长 prompt，也不是一份随手记下来的说明文档。

它更像一个可触发、可维护、可验证的能力包，通常至少包含：

- 触发描述
- 路由方式
- 安全边界
- 默认工作流

## 2. `SKILL.md` 和 `docs/**/*.md` 有什么区别

- `SKILL.md`
  面向 agent 触发与执行，是能力入口
- `docs/**/*.md`
  面向人学习和维护，是解释层

一个简单判断是：

- 解释“为什么这样设计”的，多半在 `docs/authoring`、`docs/market`、`docs/skills` 这些目录
- 决定“实际怎么触发和走哪条路”的，多半在 `SKILL.md`

## 3. `frontmatter` 是什么

`SKILL.md` 顶部那段最短的元信息就是 frontmatter。

在这个仓库里，它最重要的作用是：

- 给 skill 命名
- 说明它做什么
- 用 `Use when ...` 写清触发场景

## 4. `Task Router` 是什么

它是 `SKILL.md` 里的路由区。

作用不是把所有知识堆进去，而是把不同问题分流到：

- 哪个 reference
- 哪个 script
- 哪个默认 workflow

如果一个 router 越写越宽，通常说明 skill 边界还没收窄。

## 5. `checker` 是什么

checker 是一条可以重复运行的检查命令。

它的目标不是替代设计判断，而是保证最基本的结构和主链路没有坏。

对新人来说，最值得理解的一点是：

- 这个仓库不是“只有文档”，它是真的有回归入口

## 6. `eval` 和 `checker` 有什么区别

- checker 更像结构和主链路检查
- eval 更像质量回归检查

可以粗略理解成：

- checker 看“能不能稳定跑”
- eval 看“输出有没有退化”

## 7. `harness` 是什么

harness 是 skill 外面的系统层。

它通常负责：

- tool contract
- state
- eval
- safety gate
- automation

如果你第一次接触这个仓库，还不需要一开始就把 harness 吃透。

先知道一件事就够了：

- skill 负责能力入口
- harness 负责让这些能力更稳定地运行

## 8. 第一天必须懂 harness 吗

不需要。

第一天更重要的是先搞清楚：

- skill 怎么触发
- `SKILL.md` 怎么分层
- checker 为什么要存在

等这些稳定了，再进入 harness 反而更轻松。

## 9. 为什么仓库里既有 `docs/`，又有 `skills/`，还有 `scripts/`

因为这三个目录在回答不同问题：

- `docs/` 回答“人怎么学”
- `skills/` 回答“agent 怎么用”
- `scripts/` 回答“仓库怎么检查和运行”

把这三层分清之后，整个仓库会一下清楚很多。

## 10. 新人第一天最容易做错什么

- 以为要先把所有文档读完才能动手
- 以为要先理解全部 harness 才能写 skill
- 以为 skill 就是写一篇很长的总说明
- 以为 checker 只是附属物，可以最后再补

## 11. 第一天下来做到什么就算合格

如果你已经能做到下面几件事，就说明 onboarding 已经成功了：

- 能说清 `docs/`、`skills/`、`scripts/` 三层分别做什么
- 能说清一个最小 skill 至少包含哪些 section
- 能跑通一条 checker 或 eval 命令

## 下一步去哪

- 想走最短 onboarding 路径：进入 [14-first-hour-onboarding.md](./14-first-hour-onboarding.md)
- 想继续按新人路径学：进入 [10-learner-path.md](../roles/10-learner-path.md)
- 想开始做第一个 skill：进入 [03-build-your-first-skill.md](../foundations/03-build-your-first-skill.md)
