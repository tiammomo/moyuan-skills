# Evals 与 Harness 原型

这篇内容用来把仓库里的两条“系统层”资产串起来：

- eval harness
- harness prototypes

## 先看 Eval Harness

入口：

- [../../scripts/run_eval_harness.py](../../../scripts/run_eval_harness.py)
- [../../examples/eval-harness/cases.json](../../../examples/eval-harness/cases.json)
- [../../examples/eval-harness/baseline.json](../../../examples/eval-harness/baseline.json)

这里最值得学的是：

- case 如何描述
- grader 如何描述
- report 如何生成
- baseline 和 regression diff 怎样帮助你判断系统有没有退化

## 再看 Harness Prototypes

入口：

- [../harness-prototypes.md](../../harness/harness-prototypes.md)
- [../harness-runtime.md](../../harness/harness-runtime.md)
- [../../examples/harness-prototypes/tool-contracts/release-note-writer.yaml](../../../examples/harness-prototypes/tool-contracts/release-note-writer.yaml)
- [../../examples/harness-prototypes/safety-gates/publication-review.yaml](../../../examples/harness-prototypes/safety-gates/publication-review.yaml)
- [../../examples/harness-prototypes/automation/weekly-triage-digest.toml](../../../examples/harness-prototypes/automation/weekly-triage-digest.toml)
- [../../examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml](../../../examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml)
- [../../scripts/check_harness_prototypes.py](../../../scripts/check_harness_prototypes.py)
- [../../scripts/run_harness_stub.py](../../../scripts/run_harness_stub.py)
- [../../scripts/run_harness_runtime.py](../../../scripts/run_harness_runtime.py)

这里最值得学的是：

- 为什么 skill 之外还需要系统层描述
- 为什么 tool contract、safety gate、automation 应该用显式结构表示
- 为什么 schema、checker、stub 会让原型从“概念图”变成“可执行资产”
- 为什么 runtime blueprint 是从“静态原型”走到“真实运行”的关键一步

## 两者怎么一起看

最好的看法不是“eval 和 harness 是两套东西”，而是：

- eval 告诉你系统有没有变好
- harness prototype 告诉你系统以后应该怎样长

前者负责反馈，后者负责结构。
