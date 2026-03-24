# 渐进式披露 Workshop

这篇内容面向已经会写最小 skill 的读者。

目标是学会：

- 如何把一个臃肿 skill 重构成渐进式结构

## Workshop 任务

假设你拿到一个已经很长的 skill，它有这些问题：

- `SKILL.md` 超长
- 同时混着路由、背景、接口细节和命令示例
- 需要的信息太多，agent 不知道先看哪段

你的任务是把它拆回：

- frontmatter
- `SKILL.md`
- `references/`
- `scripts/`
- `assets/`

## 推荐流程

### 第一步：标记内容类型

先把现有内容按类型标出来：

- trigger
- safety
- router
- topic detail
- repeated execution
- templates/examples

### 第二步：收缩 `SKILL.md`

让 `SKILL.md` 只保留：

- 安全边界
- 路由
- 默认工作流

### 第三步：拆 reference

把 topic detail 拆成几个主题文件。

建议每个 reference 只讲一类问题。

### 第四步：抽 script

只要出现“相同逻辑已经重复写了很多次”，就考虑脚本化。

### 第五步：做导航和校验

拆完以后检查：

- agent 能否更快定位入口
- reference 是否两跳内可达
- router 是否更清楚

## 推荐搭配阅读

- [../progressive-disclosure.md](../progressive-disclosure.md)
- [../../skills/progressive-disclosure/SKILL.md](../../skills/progressive-disclosure/SKILL.md)
- [../../skills/progressive-disclosure/assets/loading-plan-template.md](../../skills/progressive-disclosure/assets/loading-plan-template.md)

## Workshop 产出

完成后，你应该至少产出：

- 一份拆层方案
- 一份新的 router 草稿
- 一份“哪些内容迁移到了哪里”的清单

