# Contributing

这个仓库优先追求三件事：

- 新读者能快速学会
- skill 结构能长期维持整洁
- 方法论能继续演进到 harness 层

如果你准备贡献内容，建议按下面的顺序做。

## 先判断你改的是哪一层

1. 教学层
   修改 `docs/` 或 `docs/teaching/`，目标是把仓库讲清楚。
2. 案例层
   修改 `skills/`，目标是新增或升级一个可触发的 skill。
3. 校验层
   修改 `scripts/`、checker、workflow，目标是把约定变成可回归检查。
4. 系统层
   修改 `examples/eval-harness/`、`examples/harness-prototypes/`、`templates/`，目标是把 skill 推向 harness engineering。

## 推荐工作流

1. 先改文档或 skill 本体。
2. 再补对应的 checker、lint 或 eval。
3. 再补 README / docs 索引。
4. 最后跑回归检查。

## 本地最小回归

```text
python scripts/check_progressive_skills.py
python scripts/check_docs_links.py
python scripts/check_harness_prototypes.py
python skills/build-skills/scripts/check_build_skills.py
python skills/progressive-disclosure/scripts/check_progressive_disclosure.py
python skills/harness-engineering/scripts/check_harness_engineering.py
python skills/release-note-writer/scripts/check_release_note_writer.py
python skills/issue-triage-report/scripts/check_issue_triage_report.py
python skills/incident-postmortem-writer/scripts/check_incident_postmortem_writer.py
python skills/api-change-risk-review/scripts/check_api_change_risk_review.py
python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json
```

## 修改 skill 时的约定

- frontmatter 只保留 `name` 和 `description`
- `description` 负责触发语义，不要把 “When to Use” 写回正文
- `SKILL.md` 必须保留 `Safety First`、`Task Router`、`Progressive Loading`、`Default Workflow`
- 只在真正需要时新增 `references/`、`scripts/`、`assets/`
- 顶层不要放额外的 `README.md`、`CHANGELOG.md` 之类文件

## 修改教学文档时的约定

- `docs/teaching/` 是课程区，不只是索引区
- 新增教学文档时，要在 `docs/teaching/README.md` 和 `docs/README.md` 里挂入口
- 优先补“学习顺序、练习方法、为什么这样设计”，而不是只补抽象定义

## 修改 harness 原型时的约定

- 原型要同时满足 “看得懂、能检查、能继续扩展”
- 尽量同时补 schema、example、checker、stub，而不是只给静态示例
- 如果原型影响 eval 或 automation，顺手补对应的报告或样例

## 提交建议

- 尽量把变更按主题拆分，而不是把 skill、docs、workflow 全混在一笔里
- 如果变更引入了新案例或新模板，提交信息尽量直接说明用途
- 推送前确认工作区干净，并确认新增索引都能从 README 进入
