# Harness Runtime 最小执行面

这份文档讲的是仓库这一次真正进入“运行层”的部分。

前一版仓库已经有：

- tool contract
- safety gate
- automation
- schema / checker / stub

这一轮在它们之上又补了一层：runtime blueprint + executable runtime。

## 这层解决什么问题

前面的原型已经能回答“格式应该长什么样”，但还不能回答：

- 一条 harness 路径怎样真正串起来跑
- precheck、主命令、postcheck、gate 怎样落到一次 run
- 这次 run 结束后，应该留下什么 report 和 audit artifact

`run_harness_runtime.py` 就是在回答这组问题。

## 当前入口

- [../scripts/run_harness_runtime.py](../scripts/run_harness_runtime.py)
- [../examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml](../examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml)
- [../examples/harness-prototypes/automation/release-note-publication.toml](../examples/harness-prototypes/automation/release-note-publication.toml)
- [../examples/harness-prototypes/tool-contracts/release-note-writer.yaml](../examples/harness-prototypes/tool-contracts/release-note-writer.yaml)
- [../examples/harness-prototypes/safety-gates/publication-review.yaml](../examples/harness-prototypes/safety-gates/publication-review.yaml)

## 当前运行链长什么样

这条 demo runtime 走的是：

1. 读取 runtime blueprint
2. 装配 automation、tool contract、gate
3. 运行 precheck
4. 运行主命令生成 draft
5. 运行 postcheck
6. 校验 gate 所需 checks 和 artifacts
7. 输出 JSON / Markdown runtime report

## 为什么要有 runtime blueprint

因为三类原型本身还是分散的：

- automation 关注什么时候跑、跑什么命令
- tool contract 关注工具边界
- gate 关注发布前约束

runtime blueprint 的作用是把它们组合成“一次具体 run 的执行蓝图”。

## 当前仓库里的最小判断

这一层还不是完整 orchestration engine，但已经足够说明：

- harness 不只是静态规范
- harness 可以先从 repo 内可执行 demo 开始长
- 真正的运行层至少要留下 report、artifact 和 gate 结果

## 如何运行

```text
python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml
```

运行后会生成：

- 一份 JSON runtime report
- 一份 Markdown runtime report
- 一份 generated draft

其中 review note 和 approval record 作为 demo audit artifact 由仓库静态提供，用来模拟人工审批已完成的状态。
