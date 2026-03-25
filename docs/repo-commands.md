# 仓库常用命令

这份文档汇总这个仓库最常用的开发与验证命令。

## 仓库级结构检查

检查所有 skill 的渐进式结构、reference 可达性，以及 `agents/openai.yaml` 一致性：

```text
python scripts/check_progressive_skills.py
```

检查 README、docs、teaching、templates 的相对链接是否仍然有效：

```text
python scripts/check_docs_links.py
```

检查 harness prototype 的 schema、example 和模板包：

```text
python scripts/check_harness_prototypes.py
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
python skills/issue-triage-report/scripts/check_issue_triage_report.py
python skills/incident-postmortem-writer/scripts/check_incident_postmortem_writer.py
python skills/api-change-risk-review/scripts/check_api_change_risk_review.py
```

## 生成发布说明

```text
python skills/release-note-writer/scripts/release_note_writer.py draft skills/release-note-writer/assets/sample-release-input.json out/release-notes.md
```

## 校验发布说明

```text
python skills/release-note-writer/scripts/release_note_writer.py lint out/release-notes.md
```

## 运行 Eval Harness

```text
python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json
```

如果你改动了 case 或输出逻辑，重写 baseline：

```text
python scripts/run_eval_harness.py --write-baseline examples/eval-harness/baseline.json
```

## 运行 Harness Prototype Stub

```text
python scripts/run_harness_stub.py tool-contract examples/harness-prototypes/tool-contracts/release-note-writer.yaml
python scripts/run_harness_stub.py gate examples/harness-prototypes/safety-gates/publication-review.yaml --check "script lint passes" --artifact "generated draft" --artifact "review note" --artifact "approval record"
python scripts/run_harness_stub.py automation examples/harness-prototypes/automation/weekly-triage-digest.toml
```

## 运行 Harness Runtime

```text
python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml
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
python scripts/check_docs_links.py
python scripts/check_harness_prototypes.py
python skills/release-note-writer/scripts/check_release_note_writer.py
python skills/issue-triage-report/scripts/check_issue_triage_report.py
python skills/incident-postmortem-writer/scripts/check_incident_postmortem_writer.py
python skills/api-change-risk-review/scripts/check_api_change_risk_review.py
python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json
python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml
```

