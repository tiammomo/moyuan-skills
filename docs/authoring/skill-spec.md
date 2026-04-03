# Skills 规范说明

这篇文档定义的是“本仓库里的 skill 应该长成什么样”。

它不是业务说明，而是结构、写法和维护约束。

## 1. 目录结构

一个 skill 目录建议按下面组织：

```text
skills/<skill-name>/
|- SKILL.md
|- agents/
|  `- openai.yaml
|- scripts/
|- references/
`- assets/
```

约束如下：

- `SKILL.md` 必须存在
- `agents/openai.yaml` 推荐存在
- `scripts/`、`references/`、`assets/` 按需创建

## 2. 命名规范

- 目录名只用小写字母、数字和连字符
- 目录名与 frontmatter 里的 `name` 保持一致
- 名称尽量短、清晰、可触发

推荐：

- `build-skills`
- `progressive-disclosure`
- `harness-engineering`

## 3. Frontmatter 规范

`SKILL.md` 顶部必须是 YAML frontmatter，并且只保留两个字段：

```yaml
---
name: my-skill
description: Describe what the skill does and when Codex should use it. Use when ...
---
```

要求：

- `name` 必须等于目录名
- `description` 必须同时写清“做什么”和“什么时候用”
- `description` 里要显式出现 `Use when ...`
- 不要继续堆自定义字段

## 4. 渐进式结构约束

本仓库把 skill 统一设计成渐进式加载能力包。

加载顺序应当是：

1. frontmatter 决定是否触发
2. `SKILL.md` 提供最小执行导航
3. `references/`、`scripts/`、`assets/` 只在当前任务需要时进入

因此，本仓库默认要求：

- `SKILL.md` 控制在 500 行以内
- `SKILL.md` 至少包含 `## Task Router`、`## Progressive Loading`、`## Default Workflow`
- 如果有 `references/`，就必须提供 `## Reference Files`
- 如果有 `scripts/`、`references/` 或 `assets/`，就必须提供 `## Bundled Resources`
- `## Progressive Loading` 必须明确写出“Read only / Load only / Do not preload”这类按需规则

## 5. Reference 规范

适合放进 `references/` 的内容：

- 规则说明
- 接口说明
- 主题型工作流
- 排查指南
- 领域知识

约束如下：

- 参考文件要按主题拆，而不是按历史过程堆
- 每份 reference 都应当能从 `SKILL.md` 直接到达，或在两跳内到达
- 不要做深层 reference 套娃
- 单个 `references/*.md` 超过 100 行时，顶部必须有 `## Contents`

## 6. Scripts 规范

适合放进 `scripts/` 的内容：

- 会反复执行的逻辑
- 容易出错、需要稳定参数和输出的逻辑
- 希望通过本地或 CI 回归的逻辑

脚本要求：

- 输入输出清晰
- 错误信息可定位
- 至少有一条代表性检查路径

## 7. Assets 规范

`assets/` 放输出资源，不放上下文说明。

适合放：

- 模板
- 样例
- 复用资源

## 8. `SKILL.md` 正文规范

推荐保留这些部分：

- 一句目标说明
- `## Safety First`
- `## Task Router`
- `## Progressive Loading`
- `## Default Workflow`
- `## Reference Files`
- `## Bundled Resources`

注意：

- 核心路由和默认动作留在 `SKILL.md`
- 细节规则放进 `references/`
- 可执行逻辑放进 `scripts/`

## 9. Harness 预留原则

本仓库鼓励在设计 skill 时提前判断：

- 哪些内容其实属于 system-level routing
- 哪些内容其实属于 tool contract
- 哪些内容未来需要 memory 或 state
- 哪些内容未来需要 eval 和 safety gate

这一步不是要求你马上实现 harness，而是要求你不要把 skill 做成“系统杂物间”。

## 10. 验证规范

新增或修改 skill 后，至少建议做两层检查：

1. 仓库结构 lint
2. skill-local smoke/check

当前仓库推荐：

- `python scripts/check_progressive_skills.py`
- `python skills/<skill-name>/scripts/check_<skill_name>.py`

## 11. 提交前检查清单

- 名称是否符合小写连字符规则？
- frontmatter 是否只包含 `name` 和 `description`？
- `description` 是否清楚包含 `Use when ...`？
- `SKILL.md` 是否还是入口而不是总文档？
- reference 是否都能从 `SKILL.md` 两跳内到达？
- 长 reference 是否已经补了 `## Contents`？
- 是否已经留下 skill-local 检查？
- 是否已经判断哪些东西未来应该进入 harness？

