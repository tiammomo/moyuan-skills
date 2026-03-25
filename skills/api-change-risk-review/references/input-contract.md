# Input Contract

## Contents

- [Schema Snapshot Format](#schema-snapshot-format)
- [Diff Output Format](#diff-output-format)
- [Comparison Rules](#comparison-rules)

## Schema Snapshot Format

`diff` 命令接收两份 JSON schema snapshot，结构如下：

- `api_name`
- `version`
- `endpoints`

每个 endpoint 需要包含：

- `path`
- `method`
- `summary`
- `auth`
- `request.fields`
- `response.fields`

每个 field 至少包含：

- `name`
- `type`
- `required`

## Diff Output Format

`draft` 命令接收一份 diff JSON，关键字段包括：

- `api_name`
- `from_version`
- `to_version`
- `risk_level`
- `summary`
- `breaking_changes`
- `additive_changes`
- `deprecations`
- `migration_notes`
- `rollout_checks`
- `open_questions`

## Comparison Rules

- 删除 endpoint 视为 breaking change
- 新增 required request field 视为 breaking change
- 删除 response field 视为 breaking change
- field type 变化视为 breaking change
- 新增 endpoint 或新增 optional field 视为 additive change
- `auth` 变化视为高风险变化，需要进入 rollout checks
