# Release Note Writer

`release-note-writer` 是这个仓库当前第一份真实示范型业务 skill。

它的目标不是展示复杂集成，而是展示一个足够真实、又能离线回归的业务场景：

- 从结构化变更输入生成发布说明
- 对生成后的发布说明做结构化检查

## 为什么选这个案例

这个案例适合做仓库里的第一个业务 skill，因为它同时具备：

- 明确的输入输出边界
- 稳定的脚本化需求
- 真实的业务语义
- 很容易配最小 eval harness

它很好地展示了一个“非教学型” skill 在这个仓库里应该怎么长：

- `SKILL.md` 做路由
- `references/` 放输入契约、写作规则、审核清单
- `scripts/` 放 draft 和 lint CLI
- `assets/` 放模板和样例输入

## 当前能力

当前版本支持两类动作：

1. `draft`
   从 JSON 变更输入生成 Markdown 发布说明
2. `lint`
   检查发布说明是否缺标题、缺必需章节或残留模板占位符

## 推荐使用路径

如果你想理解这个 skill：

1. 先看 [../skills/release-note-writer/SKILL.md](../../skills/release-note-writer/SKILL.md)
2. 再看 [../skills/release-note-writer/references/input-contract.md](../../skills/release-note-writer/references/input-contract.md)
3. 然后看 [../skills/release-note-writer/scripts/release_note_writer.py](../../skills/release-note-writer/scripts/release_note_writer.py)
4. 最后跑本地 checker 和 eval harness

## 常用命令

生成样例发布说明：

```text
python skills/release-note-writer/scripts/release_note_writer.py draft skills/release-note-writer/assets/sample-release-input.json out/release-notes.md
```

校验发布说明：

```text
python skills/release-note-writer/scripts/release_note_writer.py lint out/release-notes.md
```

运行 skill-local 检查：

```text
python skills/release-note-writer/scripts/check_release_note_writer.py
```

运行最小 eval harness：

```text
python scripts/run_eval_harness.py --skills release-note-writer
```

## 这个案例在仓库里的意义

`release-note-writer` 不是为了证明“我们会写一个脚本”，而是为了证明：

- 教学型方法论可以落成真实业务 skill
- 渐进式披露可以支撑实际工作流
- eval harness 可以围绕 skill 逐步建立

