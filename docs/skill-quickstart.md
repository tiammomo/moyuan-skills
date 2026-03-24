# Skills 快速上手

这篇文档面向“先做出一个最小可用 skill，再逐步增强”的场景。

如果你想先理解设计思路，再读 [skill-authoring.md](./skill-authoring.md)。
如果你想先核对结构规则，再读 [skill-spec.md](./skill-spec.md)。

## 10 分钟目标

完成后，你会得到一个最小但符合本仓库规范的 skill：

```text
skills/my-skill/
|- SKILL.md
`- agents/
   `- openai.yaml
```

## 步骤 1：给 skill 起一个窄而清晰的名字

建议：

- 只用小写字母、数字和连字符
- 优先用动作或能力命名
- 名称不要过宽

例如：

- `build-skills`
- `release-note-writer`
- `api-schema-audit`

不推荐：

- `my-helper`
- `all-in-one-tool`
- `misc-skill`

## 步骤 2：先写触发句，而不是先写正文

先把 `description` 草稿写出来，再决定 skill 要不要存在。

好 description 至少回答两件事：

1. 这个 skill 做什么
2. `Use when ...` 什么时候应该触发

示例：

```yaml
description: Teach how to design, scaffold, validate, and evolve reusable Codex skills. Use when Codex needs to create a new skill, refactor an existing skill, or decide how to split content across SKILL.md, references, scripts, and assets.
```

## 步骤 3：只写最小 `SKILL.md`

一个最小可用版本通常只需要：

- 一句目标说明
- `## Task Router`
- `## Progressive Loading`
- `## Default Workflow`

不要一开始就把背景、示例、接口细节全塞进去。

## 步骤 4：按需再加 `references/`、`scripts/`、`assets/`

默认判断原则：

- 短而常用：留在 `SKILL.md`
- 长而按需：放进 `references/`
- 稳定执行：放进 `scripts/`
- 模板和样例：放进 `assets/`

只有真的需要时再创建这些目录，不要为了“看起来完整”而补空目录。

## 步骤 5：补一个最小检查入口

在本仓库里，至少跑：

```text
python scripts/check_progressive_skills.py
```

如果你的 skill 自己带了脚本或模板，再补一个 skill-local 检查，例如：

```text
python skills/my-skill/scripts/check_my_skill.py
```

## 做完后再补仓库文档

如果这个 skill 会被长期维护，再同步更新：

1. [../README.md](../README.md)
2. [README.md](./README.md)
3. 对应专题文档

## 最小自查清单

- 名称是否清楚且可触发？
- `description` 是否同时写清“做什么”和“什么时候用”？
- `SKILL.md` 是否还是入口，而不是长说明书？
- 是否只有在真正需要时才引入 `references/`、`scripts/`、`assets/`？
- 是否已经有至少一条可重复执行的检查命令？

