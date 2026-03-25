# Moyuan Skills

这个仓库被重构成一个“教学型 skills 实验室”。

它的目标不是先堆业务集成，而是先把三件更底层的事情讲明白：

- 如何构建一个可触发、可维护、可验证的 skill
- 如何设计渐进式披露策略，让上下文按需加载而不是一次性塞满
- 如何把 skill 放进更大的 harness engineering 体系里，思考它未来会怎样演进

## 如果你是第一次来

不用一上来把整个仓库读完。

对新人最友好的进入方式是：

1. 先看 [docs/teaching/14-first-hour-onboarding.md](./docs/teaching/14-first-hour-onboarding.md)
2. 再看 [docs/skill-quickstart.md](./docs/skill-quickstart.md)
3. 然后只跑 1 到 2 条最小验证命令

第一次建议先跑：

- `python scripts/check_progressive_skills.py`
- `python skills/release-note-writer/scripts/check_release_note_writer.py`
- `python scripts/run_eval_harness.py --skills release-note-writer`

这样做的目标不是马上学完整个仓库，而是先确认三件事：

- 你知道这个仓库在教什么
- 你知道一个最小 skill 长什么样
- 你知道仓库里的检查是真能跑起来的

## 仓库定位

在这个版本里，`moyuan-skills` 不再把重点放在某个具体 SaaS 平台接入，而是把重点放在“方法论 + 示例 + 校验”三层：

- `docs/`
  面向人的学习路径、规范说明、模板与方法论
- `skills/`
  面向 agent 的可触发教学型 skill
- `scripts/`
  面向仓库维护者的结构校验脚本

这三层对应三类问题：

1. 人怎么学
2. agent 怎么用
3. 仓库怎么持续保持整洁

## 什么是渐进式 skill

这个仓库延续参考项目的核心思想：skill 应该是“渐进式加载”的能力包，而不是一篇越来越长的总说明书。

一个成熟 skill 通常拆成五层：

1. frontmatter
   只负责触发，说明“做什么”和“什么时候用”
2. `SKILL.md`
   只负责路由、安全边界、默认工作流
3. `references/`
   放按需加载的规则、专题说明、接口知识
4. `scripts/`
   放稳定执行或重复复用的实现
5. `assets/`
   放模板、样例和输出资源

在 `moyuan-skills` 里，我们再往前走一步：把 skill 看成 future harness 的一个可组合模块，而不是系统的全部。

## 当前 Skills

截至 2026-03-25，这个仓库包含三份教学型 skill 和四份示范型业务 skill：

| Skill | 类型 | 主题 | 当前状态 | 入口 |
| --- | --- | --- | --- | --- |
| `build-skills` | 教学型 | 如何设计、搭建、校验一个 skill | 已完成首版 | [docs/skill-authoring.md](./docs/skill-authoring.md) |
| `progressive-disclosure` | 教学型 | 如何把知识切到 frontmatter / `SKILL.md` / `references/` / `scripts/` / `assets/` | 已完成首版 | [docs/progressive-disclosure.md](./docs/progressive-disclosure.md) |
| `harness-engineering` | 教学型 | 如何从 skill 继续演进到工具编排、评测闭环和 agent operating system | 已完成首版 | [docs/harness-engineering.md](./docs/harness-engineering.md) |
| `issue-triage-report` | 示范型业务 | 如何从 CSV issue 导出生成 triage 摘要 | 已完成首版 | [docs/issue-triage-report.md](./docs/issue-triage-report.md) |
| `release-note-writer` | 示范型业务 | 如何从结构化变更输入生成并校验发布说明 | 已完成首版 | [docs/release-note-writer.md](./docs/release-note-writer.md) |
| `api-change-risk-review` | 示范型业务 | 如何从 before / after schema snapshot 生成 API 风险评审 | 已完成首版 | [docs/api-change-risk-review.md](./docs/api-change-risk-review.md) |
| `incident-postmortem-writer` | 示范型业务 | 如何从 incident record 生成并校验 postmortem | 已完成首版 | [docs/incident-postmortem-writer.md](./docs/incident-postmortem-writer.md) |

## 推荐学习路径

如果你想完整学一遍，推荐按下面顺序阅读：

1. [docs/teaching/README.md](./docs/teaching/README.md)
2. [docs/teaching/01-learning-map.md](./docs/teaching/01-learning-map.md)
3. [docs/skill-learning-guide.md](./docs/skill-learning-guide.md)
4. [docs/skill-quickstart.md](./docs/skill-quickstart.md)
5. [docs/skill-spec.md](./docs/skill-spec.md)
6. [docs/skill-authoring.md](./docs/skill-authoring.md)
7. [docs/progressive-disclosure.md](./docs/progressive-disclosure.md)
8. [docs/harness-engineering.md](./docs/harness-engineering.md)
9. [docs/teaching/09-project-learning-roadmap.md](./docs/teaching/09-project-learning-roadmap.md)

如果你已经知道自己的目标，直接按角色进入更快：

- 新人 / onboarding：
  [docs/teaching/14-first-hour-onboarding.md](./docs/teaching/14-first-hour-onboarding.md)
- 第一次写 skill：
  [docs/teaching/10-learner-path.md](./docs/teaching/10-learner-path.md)
- 准备重构或新增 skill：
  [docs/teaching/11-skill-author-path.md](./docs/teaching/11-skill-author-path.md)
- 维护仓库和校验链路：
  [docs/teaching/12-maintainer-path.md](./docs/teaching/12-maintainer-path.md)
- 继续做 harness：
  [docs/teaching/13-harness-builder-path.md](./docs/teaching/13-harness-builder-path.md)

如果你想直接看可触发 skill，再进入：

- [skills/build-skills/SKILL.md](./skills/build-skills/SKILL.md)
- [skills/progressive-disclosure/SKILL.md](./skills/progressive-disclosure/SKILL.md)
- [skills/harness-engineering/SKILL.md](./skills/harness-engineering/SKILL.md)
- [skills/issue-triage-report/SKILL.md](./skills/issue-triage-report/SKILL.md)
- [skills/release-note-writer/SKILL.md](./skills/release-note-writer/SKILL.md)
- [skills/api-change-risk-review/SKILL.md](./skills/api-change-risk-review/SKILL.md)
- [skills/incident-postmortem-writer/SKILL.md](./skills/incident-postmortem-writer/SKILL.md)

如果你想走一条更课程化的路径，直接进入：

- [docs/teaching/README.md](./docs/teaching/README.md)
- [docs/teaching/01-learning-map.md](./docs/teaching/01-learning-map.md)
- [docs/teaching/03-build-your-first-skill.md](./docs/teaching/03-build-your-first-skill.md)
- [docs/teaching/05-harness-roadmap.md](./docs/teaching/05-harness-roadmap.md)
- [docs/teaching/07-case-gradient.md](./docs/teaching/07-case-gradient.md)
- [docs/teaching/08-evals-and-prototypes.md](./docs/teaching/08-evals-and-prototypes.md)
- [docs/teaching/09-project-learning-roadmap.md](./docs/teaching/09-project-learning-roadmap.md)
- [docs/teaching/10-learner-path.md](./docs/teaching/10-learner-path.md)
- [docs/teaching/11-skill-author-path.md](./docs/teaching/11-skill-author-path.md)
- [docs/teaching/12-maintainer-path.md](./docs/teaching/12-maintainer-path.md)
- [docs/teaching/13-harness-builder-path.md](./docs/teaching/13-harness-builder-path.md)
- [docs/teaching/14-first-hour-onboarding.md](./docs/teaching/14-first-hour-onboarding.md)

## 仓库结构

```text
.
|- docs/
|  `- teaching/
|- examples/
|  |- eval-harness/
|  |- lint-fixtures/
|  `- harness-prototypes/
|- scripts/
|- skills/
|  |- build-skills/
|  |- progressive-disclosure/
|  |- harness-engineering/
|  |- issue-triage-report/
|  |- release-note-writer/
|  |- api-change-risk-review/
|  `- incident-postmortem-writer/
|- templates/
|- CONTRIBUTING.md
`- .github/workflows/
```

## 校验命令

仓库当前提供多类本地检查入口：

- `python scripts/check_progressive_skills.py`
- `python scripts/check_docs_links.py`
- `python scripts/check_harness_prototypes.py`
- `python skills/build-skills/scripts/check_build_skills.py`
- `python skills/progressive-disclosure/scripts/check_progressive_disclosure.py`
- `python skills/harness-engineering/scripts/check_harness_engineering.py`
- `python skills/issue-triage-report/scripts/check_issue_triage_report.py`
- `python skills/release-note-writer/scripts/check_release_note_writer.py`
- `python skills/incident-postmortem-writer/scripts/check_incident_postmortem_writer.py`
- `python skills/api-change-risk-review/scripts/check_api_change_risk_review.py`
- `python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json`
- `python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml`

其中前两条分别检查结构约定与文档链接，第三条检查 harness prototype 的 schema / example / stub / runtime blueprint，六条已有 skill-local checker 加上一条新的多步业务 skill checker 负责验证各自技能包的关键资源与主链路，倒数第二条命令运行带 grader、baseline、diff 和 report 的 eval harness，最后一条命令运行最小可执行 harness runtime。

## 这个仓库对未来 skills 的判断

这个仓库的基本判断是：

- skill 不会消失，但会从“静态知识包”逐步演进成“agent system 的一个可组合层”
- 越往后，真正重要的不只是 prompt 或 reference，而是 trigger、tool contract、state、memory、eval、safety、automation 这些外围 harness
- 因此，做 skill 的同时就应该开始思考：哪些东西属于 skill，哪些东西应该上移到 harness

这也是本仓库同时保留 `build-skills`、`progressive-disclosure` 和 `harness-engineering` 三个教学入口的原因。

## 当前完善结果

这轮完善已经把原先的规划项基本落成稳定资产，仓库现在新增了：

- 角色化教学路径：
  [docs/teaching/10-learner-path.md](./docs/teaching/10-learner-path.md)、[docs/teaching/11-skill-author-path.md](./docs/teaching/11-skill-author-path.md)、[docs/teaching/12-maintainer-path.md](./docs/teaching/12-maintainer-path.md)、[docs/teaching/13-harness-builder-path.md](./docs/teaching/13-harness-builder-path.md)
- 一个更偏 tool-heavy / multi-step 的真实业务 skill：
  [docs/api-change-risk-review.md](./docs/api-change-risk-review.md)
- 更强的仓库 lint 和 docs lint：
  [scripts/check_progressive_skills.py](./scripts/check_progressive_skills.py)、[scripts/check_docs_links.py](./scripts/check_docs_links.py)
- 带 baseline / diff / skill summary 的 eval harness：
  [scripts/run_eval_harness.py](./scripts/run_eval_harness.py)
- 带 schema / checker / stub 的 harness prototypes：
  [docs/harness-prototypes.md](./docs/harness-prototypes.md)、[scripts/check_harness_prototypes.py](./scripts/check_harness_prototypes.py)、[scripts/run_harness_stub.py](./scripts/run_harness_stub.py)
- 把 automation、tool contract、gate 串成一次真实 run 的最小运行层：
  [docs/harness-runtime.md](./docs/harness-runtime.md)、[scripts/run_harness_runtime.py](./scripts/run_harness_runtime.py)
- contributor 指南和模板资产库：
  [CONTRIBUTING.md](./CONTRIBUTING.md)、[docs/template-library.md](./docs/template-library.md)

如果你想继续往下推进，最自然的下一步已经不再是“先写规划”，而是直接沿这三条线继续迭代：

- 再补更重的集成型业务案例
- 继续扩 baseline eval 与 regression 报告
- 把单条 runtime blueprint 推向多 skill orchestration 和更强的 state / audit 管理
