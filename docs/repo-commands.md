# 仓库常用命令

这份文档汇总这个仓库最常用的开发与验证命令。

## 仓库级结构检查

检查所有 skill 的渐进式结构、reference 可达性，以及 `agents/openai.yaml` 一致性：

```text
python scripts/check_progressive_skills.py
```

## 教学型 Skill 检查

```text
python skills/build-skills/scripts/check_build_skills.py
python skills/progressive-disclosure/scripts/check_progressive_disclosure.py
python skills/harness-engineering/scripts/check_harness_engineering.py
```

## 业务 Skill 检查

```text
python skills/release-note-writer/scripts/check_release_note_writer.py
```

## 生成发布说明

```text
python skills/release-note-writer/scripts/release_note_writer.py draft skills/release-note-writer/assets/sample-release-input.json out/release-notes.md
```

## 校验发布说明

```text
python skills/release-note-writer/scripts/release_note_writer.py lint out/release-notes.md
```

## 运行最小 Eval Harness 示例

```text
python scripts/run_minimal_eval_harness.py
```

## 常见维护动作

### 看某个文档是否还有占位符

```text
Get-ChildItem -Recurse -File | Select-String -Pattern "TODO|\[TODO"
```

### 查看 `docs/teaching/` 当前结构

```text
Get-ChildItem -Recurse docs\teaching
```

### 查看 skill 目录结构

```text
Get-ChildItem -Recurse skills
```

## 推荐的提交前最小命令集

如果你只想做一轮最小回归，推荐跑：

```text
python scripts/check_progressive_skills.py
python skills/release-note-writer/scripts/check_release_note_writer.py
python scripts/run_minimal_eval_harness.py
```

