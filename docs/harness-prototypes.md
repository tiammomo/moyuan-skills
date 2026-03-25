# Harness 原型示例

这份文档用来说明仓库里新增的三类 harness 原型：

- tool contract
- safety gate
- automation

这些原型不是完整系统，而是第一批“可见、可讨论、可复用”的系统层资产。

现在它们已经不只是静态示例，还配了：

- schema
- checker
- executable stub

在这三类原型之上，仓库还新增了一层组合资产：

- runtime blueprint
- executable runtime

## 1. Tool Contract

位置：

- [../examples/harness-prototypes/tool-contracts/release-note-writer.yaml](../examples/harness-prototypes/tool-contracts/release-note-writer.yaml)
- [../examples/harness-prototypes/tool-contracts/incident-postmortem-writer.yaml](../examples/harness-prototypes/tool-contracts/incident-postmortem-writer.yaml)
- [../examples/harness-prototypes/schemas/tool-contract.schema.json](../examples/harness-prototypes/schemas/tool-contract.schema.json)

它们展示：

- 一个 skill 脚本怎样被描述成 harness 可理解的工具
- 输入、输出、失败模式和安全说明应该怎样被显式写出

## 2. Safety Gate

位置：

- [../examples/harness-prototypes/safety-gates/publication-review.yaml](../examples/harness-prototypes/safety-gates/publication-review.yaml)
- [../examples/harness-prototypes/schemas/safety-gate.schema.json](../examples/harness-prototypes/schemas/safety-gate.schema.json)

它展示：

- 哪些发布动作不应该变成默认自动行为
- 哪些检查、审批和 artifact 应该在系统层被要求

## 3. Automation

位置：

- [../examples/harness-prototypes/automation/weekly-triage-digest.toml](../examples/harness-prototypes/automation/weekly-triage-digest.toml)
- [../examples/harness-prototypes/schemas/automation.schema.json](../examples/harness-prototypes/schemas/automation.schema.json)

它展示：

- 一个 skill 驱动的 recurring workflow 应该怎样被描述
- precheck、postcheck、review requirement 应该怎样进 spec

## 4. Runtime Blueprint

位置：

- [../examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml](../examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml)
- [../examples/harness-prototypes/schemas/runtime-blueprint.schema.json](../examples/harness-prototypes/schemas/runtime-blueprint.schema.json)
- [harness-runtime.md](./harness-runtime.md)

它展示：

- 怎样把 automation、tool contract、gate 组合成一次具体 run
- 一次 run 结束后应该留下什么 report 和 artifact
- harness 怎样从 stub 走向最小可执行运行层

## 这些原型在仓库里的作用

它们的意义不是“已经有完整 harness 了”，而是：

- 让 skill 和 future harness 之间出现清晰接口
- 让团队能围绕真实格式讨论系统设计
- 让后续 eval、automation、safety 的演进不再停留在口头上

## 现在怎么验证它们

```text
python scripts/check_harness_prototypes.py
python scripts/run_harness_stub.py tool-contract examples/harness-prototypes/tool-contracts/release-note-writer.yaml
python scripts/run_harness_stub.py automation examples/harness-prototypes/automation/weekly-triage-digest.toml
python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml
```
