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

## 新人术语速查

第一次读这个仓库时，先只记住下面几个词就够了：

- `frontmatter`
  `SKILL.md` 顶部那段最短的触发描述，负责说明“这个 skill 做什么、什么时候用”
- `Task Router`
  `SKILL.md` 里的路由区，负责把不同问题导向不同 reference、script 或 workflow
- `checker`
  一条可以反复运行的检查命令，用来确认 skill 资源和主链路没有坏
- `eval`
  一组固定 case 和 grader，用来判断输出质量有没有退化
- `harness`
  skill 外面的系统层，负责 tool contract、state、eval、safety、automation 这些能力

如果这些词还不熟，先看 [docs/teaching/15-newcomer-faq.md](./docs/teaching/15-newcomer-faq.md)。

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
- 想先补齐术语和常见疑问：
  [docs/teaching/15-newcomer-faq.md](./docs/teaching/15-newcomer-faq.md)

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
- [docs/teaching/15-newcomer-faq.md](./docs/teaching/15-newcomer-faq.md)
- [docs/teaching/16-skills-market-evolution.md](./docs/teaching/16-skills-market-evolution.md)
- [docs/teaching/17-market-registry-and-federation.md](./docs/teaching/17-market-registry-and-federation.md)

## 仓库结构

```text
.
|- docs/
|  `- teaching/
|- examples/
|  |- eval-harness/
|  |- lint-fixtures/
|  `- harness-prototypes/
|- schemas/
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

## Skills Market 方向

这个项目接下来的核心演进目标，是从“教学型 skills 实验室”继续走向“skills market 参考实现”。

目标不是只继续堆 skill，而是同时补齐：

- skill 包如何标准化
- skill 如何被搜索、筛选、安装、更新
- quality / trust / review 信号如何进入 market
- public market 和 private market 如何并存

对应草案见：

- [docs/market-spec.md](./docs/market-spec.md)
- [docs/market-governance.md](./docs/market-governance.md)
- [docs/market-registry.md](./docs/market-registry.md)
- [docs/publisher-guide.md](./docs/publisher-guide.md)
- [docs/consumer-guide.md](./docs/consumer-guide.md)

当前本地已经跑通的最小 market 执行闭环是：

```text
python scripts/skills_market.py smoke
```

## Skills Market Client Workflow

如果你想从“搜索 skill”一路走到“本地安装、查看、更新、移除”，当前最小可运行链路是：

```text
python scripts/skills_market.py package release-note-writer
python scripts/skills_market.py provenance-check dist/market/install/release-note-writer-0.1.0.json
python scripts/skills_market.py install dist/market/install/release-note-writer-0.1.0.json --target-root dist/installed-skills
python scripts/skills_market.py list-installed --target-root dist/installed-skills
python scripts/skills_market.py update moyuan.release-note-writer --index dist/market/channels/stable.json --target-root dist/installed-skills --dry-run
python scripts/skills_market.py remove moyuan.release-note-writer --target-root dist/installed-skills
```

这条链路补齐了当前本地 market client 的最小生命周期：

- `install` 会校验 `checksum`、`provenance` 和 `lifecycle`
- `list-installed` 会读取 `skills.lock.json`
- `update` 会从 channel index 解析最新 install spec
- `remove` 会删除安装目录并同步更新 lock

## Skills Market Bundle Workflow

如果你想一次性拉下一组 starter bundle，而不是逐个安装 skill，当前本地 market 已经支持：

```text
python scripts/skills_market.py list-bundles
python scripts/skills_market.py install-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
python scripts/skills_market.py install-bundle skill-authoring-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
```

这条链路补的是 bundle 级消费能力：

- `list-bundles` 负责发现一组适合一起安装的能力包
- `install-bundle` 会按 bundle 内 skill 的 channel 解析 install spec
- `archived` 或 `blocked` 的 skill 会被清晰跳过，而不是让整组安装直接崩掉
- 实际安装后会在目标目录下生成 bundle report，方便回看结果

## Skills Market Bundle State Workflow

如果你已经装过 starter bundle，当前也可以继续查看和移除它：

```text
python scripts/skills_market.py list-installed-bundles --target-root dist/installed-bundles
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles
```

这条链路补的是 bundle 安装后的状态管理：

- `install` 会把 direct install 和 bundle install 的来源一起写进 `skills.lock.json`
- `list-installed-bundles` 会把 bundle report 和当前 lock 状态对齐后展示
- `remove-bundle` 会只删掉真正只属于这个 bundle 的 skill
- 如果某个 skill 同时属于 direct install 或别的 bundle，它会被保留，只移除当前 bundle 的 ownership

## Skills Market Bundle Update Workflow

如果你已经装过一个 starter bundle，当前也可以按最新 market 状态把它重新对齐：

```text
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
```

这条链路补的是 bundle 的“升级和修复”能力：

- 会重新解析 bundle 当前应该包含哪些 skill
- 会按最新 channel index 刷新这些 skill 的 install spec
- 如果某个 skill 已经不再属于 bundle，或者现在变成 `archived / blocked`，会在 reconcile 阶段移除当前 bundle 的 ownership
- 如果某个 skill 还有 direct install 或别的 bundle 作为来源，它仍然会被保留

## Skills Market Installed-State Doctor

如果你想确认本地安装态没有漂移，当前也可以直接跑安装态体检：

```text
python scripts/skills_market.py doctor-installed --target-root dist/installed-skills
python scripts/skills_market.py doctor-installed --target-root dist/installed-skills --strict
python scripts/skills_market.py repair-installed --target-root dist/installed-skills --dry-run
python scripts/skills_market.py repair-installed --target-root dist/installed-skills
python scripts/skills_market.py snapshot-installed --target-root dist/installed-skills --output-path dist/installed-skills/snapshots/latest.json --markdown-path dist/installed-skills/snapshots/latest.md
python scripts/skills_market.py diff-installed dist/installed-skills/snapshots/before.json dist/installed-skills/snapshots/after.json --output-path dist/installed-skills/snapshots/diff.json --markdown-path dist/installed-skills/snapshots/diff.md
python scripts/skills_market.py verify-installed dist/installed-skills/snapshots/baseline.json --target-root dist/installed-skills --output-dir dist/installed-skills/verification --strict
python scripts/skills_market.py verify-installed-history dist/installed-skills/snapshots/baseline-history.json latest --target-root dist/installed-skills --output-dir dist/installed-skills/verification-history --strict
python scripts/skills_market.py diff-installed-history dist/installed-skills/snapshots/baseline-history.json 1 latest --output-path dist/installed-skills/snapshots/history-diff.json --markdown-path dist/installed-skills/snapshots/history-diff.md
python scripts/skills_market.py promote-installed-baseline dist/installed-skills/snapshots/baseline.json --target-root dist/installed-skills --markdown-path dist/installed-skills/snapshots/baseline.md --diff-output-path dist/installed-skills/snapshots/baseline-transition.json --diff-markdown-path dist/installed-skills/snapshots/baseline-transition.md --history-path dist/installed-skills/snapshots/baseline-history.json --history-markdown-path dist/installed-skills/snapshots/baseline-history.md --archive-dir dist/installed-skills/snapshots/baseline-archive
python scripts/skills_market.py list-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json
python scripts/skills_market.py report-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --output-path dist/installed-skills/snapshots/history-report.json --markdown-path dist/installed-skills/snapshots/history-report.md
python scripts/skills_market.py list-installed-history-policies
python scripts/skills_market.py list-installed-history-waivers
python scripts/skills_market.py audit-installed-history-waivers dist/installed-skills/snapshots/baseline-history.json --strict
python scripts/skills_market.py remediate-installed-history-waivers dist/installed-skills/snapshots/baseline-history.json --strict
python scripts/skills_market.py draft-installed-history-waiver-execution dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-execution --strict
python scripts/skills_market.py preview-installed-history-waiver-execution dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-preview --strict
python scripts/skills_market.py prepare-installed-history-waiver-apply dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --strict
python scripts/skills_market.py execute-installed-history-waiver-apply dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --stage-dir dist/installed-skills/snapshots/waiver-stage --strict
python scripts/skills_market.py audit-installed-history-waiver-sources dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --strict
python scripts/skills_market.py reconcile-installed-history-waiver-sources dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --strict
python scripts/skills_market.py execute-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --stage-dir dist/installed-skills/snapshots/waiver-source-reconcile-stage --strict
python scripts/skills_market.py verify-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --strict
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --waiver approved-release-engineering-downsize --strict
python scripts/skills_market.py restore-installed-baseline dist/installed-skills/snapshots/baseline-history.json latest --baseline-path dist/installed-skills/snapshots/baseline.json --markdown-path dist/installed-skills/snapshots/baseline.md
python scripts/skills_market.py prune-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --keep-last 5
```

这条链路补的是“本地 market client 能不能自查”：

- 会检查 `skills.lock.json`、bundle report、安装目录三者是否一致
- 会检查 lock 里的 `install_spec`、`provenance_path` 和 installed entrypoint 是否仍然有效
- 会检查 bundle ownership 是否指向真实存在的 bundle report
- 会识别未被 lock 追踪的 orphan 安装目录
- 会保守修复 orphan 安装目录和已经失效的 bundle report
- 会导出一份 installed-state snapshot，方便归档、review 和后续 diff
- 会对比两次 snapshot，沉淀出 skill / bundle 的变化报告
- 会拿当前安装态直接对比基线 snapshot，把 drift 变成可失败的校验门禁
- 会在 drift 被接受后，把当前 live state 提升成新的 baseline，并保留 transition diff
- 会为每次 baseline promotion 留下 history，方便回看基线演进轨迹
- 会把 retained history 汇总成一份 timeline/report，方便维护者快速回顾 accepted baseline 是怎么一路变化的
- 会在 retained transition 超过阈值时直接给出 alert/gate 信号，方便把大变更接进 review 或本地门禁
- 会把常用的 history alert 阈值沉淀成可复用 policy profile，避免每次都手敲一整组 threshold flags
- 会把已审批的大变更留成明确的 waiver record，让团队能区分“已接受例外”和“意外漂移”
- 会周期性 audit waiver record，主动识别 expired、unmatched、stale 的例外记录，避免治理资产悄悄失效
- 会把 waiver audit 的结果继续变成 remediation 建议，明确告诉维护者该续期、清理还是重写 selector

如果你想直接生成静态 market catalog，可以跑：

```text
python scripts/skills_market.py catalog
python scripts/skills_market.py recommend
python scripts/skills_market.py federation-feed
python scripts/skills_market.py registry
```

如果你想验证 publisher / org policy 并生成 org/private market：

```text
python scripts/skills_market.py governance-check
python scripts/skills_market.py provenance-check dist/market/install/release-note-writer-0.1.0.json
python scripts/skills_market.py org-index governance/orgs/moyuan-internal.json
python scripts/skills_market.py catalog --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py recommend --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py federation-feed --org-policy governance/orgs/moyuan-internal.json
```

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
- 把 skill 包、registry、installer 和 trust 信号收敛成一套可运行的 skills market
