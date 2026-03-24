# Moyuan Skills

这个仓库被重构成一个“教学型 skills 实验室”。

它的目标不是先堆业务集成，而是先把三件更底层的事情讲明白：

- 如何构建一个可触发、可维护、可验证的 skill
- 如何设计渐进式披露策略，让上下文按需加载而不是一次性塞满
- 如何把 skill 放进更大的 harness engineering 体系里，思考它未来会怎样演进

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

截至 2026-03-24，这个仓库包含三份教学型 skill 和三份示范型业务 skill：

| Skill | 类型 | 主题 | 当前状态 | 入口 |
| --- | --- | --- | --- | --- |
| `build-skills` | 教学型 | 如何设计、搭建、校验一个 skill | 已完成首版 | [docs/skill-authoring.md](./docs/skill-authoring.md) |
| `progressive-disclosure` | 教学型 | 如何把知识切到 frontmatter / `SKILL.md` / `references/` / `scripts/` / `assets/` | 已完成首版 | [docs/progressive-disclosure.md](./docs/progressive-disclosure.md) |
| `harness-engineering` | 教学型 | 如何从 skill 继续演进到工具编排、评测闭环和 agent operating system | 已完成首版 | [docs/harness-engineering.md](./docs/harness-engineering.md) |
| `issue-triage-report` | 示范型业务 | 如何从 CSV issue 导出生成 triage 摘要 | 已完成首版 | [docs/issue-triage-report.md](./docs/issue-triage-report.md) |
| `release-note-writer` | 示范型业务 | 如何从结构化变更输入生成并校验发布说明 | 已完成首版 | [docs/release-note-writer.md](./docs/release-note-writer.md) |
| `incident-postmortem-writer` | 示范型业务 | 如何从 incident record 生成并校验 postmortem | 已完成首版 | [docs/incident-postmortem-writer.md](./docs/incident-postmortem-writer.md) |

## 推荐学习路径

如果你第一次进入这个仓库，推荐按下面顺序阅读：

1. [docs/teaching/README.md](./docs/teaching/README.md)
2. [docs/skill-learning-guide.md](./docs/skill-learning-guide.md)
3. [docs/skill-quickstart.md](./docs/skill-quickstart.md)
4. [docs/skill-spec.md](./docs/skill-spec.md)
5. [docs/skill-authoring.md](./docs/skill-authoring.md)
6. [docs/progressive-disclosure.md](./docs/progressive-disclosure.md)
7. [docs/harness-engineering.md](./docs/harness-engineering.md)
8. [docs/skill-future-roadmap.md](./docs/skill-future-roadmap.md)

如果你想直接看可触发 skill，再进入：

- [skills/build-skills/SKILL.md](./skills/build-skills/SKILL.md)
- [skills/progressive-disclosure/SKILL.md](./skills/progressive-disclosure/SKILL.md)
- [skills/harness-engineering/SKILL.md](./skills/harness-engineering/SKILL.md)
- [skills/issue-triage-report/SKILL.md](./skills/issue-triage-report/SKILL.md)
- [skills/release-note-writer/SKILL.md](./skills/release-note-writer/SKILL.md)
- [skills/incident-postmortem-writer/SKILL.md](./skills/incident-postmortem-writer/SKILL.md)

如果你想走一条更课程化的路径，直接进入：

- [docs/teaching/README.md](./docs/teaching/README.md)
- [docs/teaching/01-learning-map.md](./docs/teaching/01-learning-map.md)
- [docs/teaching/03-build-your-first-skill.md](./docs/teaching/03-build-your-first-skill.md)
- [docs/teaching/05-harness-roadmap.md](./docs/teaching/05-harness-roadmap.md)
- [docs/teaching/07-case-gradient.md](./docs/teaching/07-case-gradient.md)
- [docs/teaching/08-evals-and-prototypes.md](./docs/teaching/08-evals-and-prototypes.md)

## 仓库结构

```text
.
|- docs/
|  `- teaching/
|- examples/
|  |- eval-harness/
|  `- harness-prototypes/
|- scripts/
|- skills/
|  |- build-skills/
|  |- progressive-disclosure/
|  |- harness-engineering/
|  |- issue-triage-report/
|  |- release-note-writer/
|  `- incident-postmortem-writer/
`- .github/workflows/
```

## 校验命令

仓库当前提供多类本地检查入口：

- `python scripts/check_progressive_skills.py`
- `python skills/build-skills/scripts/check_build_skills.py`
- `python skills/progressive-disclosure/scripts/check_progressive_disclosure.py`
- `python skills/harness-engineering/scripts/check_harness_engineering.py`
- `python skills/issue-triage-report/scripts/check_issue_triage_report.py`
- `python skills/release-note-writer/scripts/check_release_note_writer.py`
- `python skills/incident-postmortem-writer/scripts/check_incident_postmortem_writer.py`
- `python scripts/run_eval_harness.py`

其中第一条检查整个仓库的渐进式结构、router 质量、teaching 完整性和 `openai.yaml` 一致性，六条 skill-local checker 检查各自技能包的关键资源与样例链路，最后一条命令运行带 grader 和 report 的 eval harness。

## 这个仓库对未来 skills 的判断

这个仓库的基本判断是：

- skill 不会消失，但会从“静态知识包”逐步演进成“agent system 的一个可组合层”
- 越往后，真正重要的不只是 prompt 或 reference，而是 trigger、tool contract、state、memory、eval、safety、automation 这些外围 harness
- 因此，做 skill 的同时就应该开始思考：哪些东西属于 skill，哪些东西应该上移到 harness

这也是本仓库同时保留 `build-skills`、`progressive-disclosure` 和 `harness-engineering` 三个教学入口的原因。

## 项目下一步完善方向

我已经补了一份更完整的规划文档：

- [docs/project-improvement-plan.md](./docs/project-improvement-plan.md)

当前最值得优先推进的方向有六类：

1. 把 `docs/teaching/` 继续扩成完整课程体系，补练习、作业和 capstone。
2. 增加 2 到 3 个真实示范型业务 skill，验证方法论如何落地。
3. 增强渐进式披露相关 lint，让更多规范可自动回归。
4. 开始建设 harness 原型，包括 tool contract、eval、safety gate、automation。
5. 补开发环境与仓库运维说明，提升长期维护体验。
6. 把现有方法论继续沉淀成更细的模板资产。

如果把这个项目看成一个长期演进的实验平台，那么下一阶段的核心目标不是“文档更多”，而是：

- 学习路径更完整
- 案例更真实
- harness 更可落地

这 6 个方向的详细拆解已经整理到：

- [docs/project-improvement-plan.md](./docs/project-improvement-plan.md)

其中教学体系这一条线，已经进一步落到：

- [docs/teaching/06-exercises-and-capstone.md](./docs/teaching/06-exercises-and-capstone.md)

当前已经补上的下一阶段资产包括：

- 两份新示范型业务 skill：
  [docs/issue-triage-report.md](./docs/issue-triage-report.md) 和 [docs/incident-postmortem-writer.md](./docs/incident-postmortem-writer.md)
- 一套升级后的 eval harness：
  [scripts/run_eval_harness.py](./scripts/run_eval_harness.py)
- 三类 harness 原型：
  [docs/harness-prototypes.md](./docs/harness-prototypes.md)
