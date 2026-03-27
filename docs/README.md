# Skills Market Docs

`docs/` 面向人类读者，负责解释这个项目怎么学、怎么扩、怎么维护。

其中：

- `docs/teaching/` 是整个 `skills market` 的教学目录
- 其余文档负责提供规范、案例、治理、分发和集成说明

## 新人先看

如果你是第一次进入这个仓库，推荐按下面顺序读：

1. [teaching/README.md](./teaching/README.md)
2. [teaching/14-first-hour-onboarding.md](./teaching/14-first-hour-onboarding.md)
3. [teaching/15-newcomer-faq.md](./teaching/15-newcomer-faq.md)
4. [skill-learning-guide.md](./skill-learning-guide.md)
5. [skill-quickstart.md](./skill-quickstart.md)
6. [repo-commands.md](./repo-commands.md)

## 核心方法论文档

- [skill-quickstart.md](./skill-quickstart.md)
  最小 skill 的起步路径。
- [skill-spec.md](./skill-spec.md)
  skill 结构、frontmatter 和资源组织约束。
- [skill-authoring.md](./skill-authoring.md)
  从需求收口到 skill 设计与维护。
- [progressive-disclosure.md](./progressive-disclosure.md)
  如何把知识切成可按需加载的层。
- [harness-engineering.md](./harness-engineering.md)
  skill 如何继续走向 harness。
- [harness-prototypes.md](./harness-prototypes.md)
  tool contract、safety gate、automation 原型。
- [harness-runtime.md](./harness-runtime.md)
  最小可执行 harness runtime。

## Skills Market 文档

- [market-spec.md](./market-spec.md)
  market manifest、install spec、channel index 和 quality signal。
- [market-governance.md](./market-governance.md)
  publisher、org policy、waiver、gate 与 source reconcile。
- [market-registry.md](./market-registry.md)
  provenance、bundle、recommendation、federation 与 hosted registry。
- [publisher-guide.md](./publisher-guide.md)
  skill 作者如何把能力包发布成 market-ready artifact。
- [consumer-guide.md](./consumer-guide.md)
  consumer 如何搜索、安装、更新、排障和治理本地状态。
- [frontend-backend-integration.md](./frontend-backend-integration.md)
  现有前端如何对接 Python backend 与 repo-backed docs，并把命令、产物、honest local install 提示、local install job API，以及新的 remote registry install API 一起纳入整体集成设计。
- [interaction-and-remote-install-roadmap.md](./interaction-and-remote-install-roadmap.md)
  盘点当前前后端交互闭环、未补完的按钮能力，以及“是否能直接从远端拉取 skill 到本地”的后续路线；当前已完成 honest local command UI、bundle-level local actions、skill / bundle 详情页上的本地执行 UI、backend local lifecycle API，以及 CLI/backend 侧的 remote registry install。

## 业务案例文档

- [release-note-writer.md](./release-note-writer.md)
- [issue-triage-report.md](./issue-triage-report.md)
- [api-change-risk-review.md](./api-change-risk-review.md)
- [incident-postmortem-writer.md](./incident-postmortem-writer.md)

## 教学目录

`docs/teaching/` 已经专门用于“整个 skills market 的教学内容”，当前课程如下：

### 基础与方法

- [teaching/01-learning-map.md](./teaching/01-learning-map.md)
- [teaching/02-read-the-repo.md](./teaching/02-read-the-repo.md)
- [teaching/03-build-your-first-skill.md](./teaching/03-build-your-first-skill.md)
- [teaching/04-progressive-disclosure-workshop.md](./teaching/04-progressive-disclosure-workshop.md)
- [teaching/05-harness-roadmap.md](./teaching/05-harness-roadmap.md)

### 练习、案例与基础设施

- [teaching/06-exercises-and-capstone.md](./teaching/06-exercises-and-capstone.md)
- [teaching/07-case-gradient.md](./teaching/07-case-gradient.md)
- [teaching/08-evals-and-prototypes.md](./teaching/08-evals-and-prototypes.md)
- [teaching/09-project-learning-roadmap.md](./teaching/09-project-learning-roadmap.md)

### 角色化路径

- [teaching/10-learner-path.md](./teaching/10-learner-path.md)
- [teaching/11-skill-author-path.md](./teaching/11-skill-author-path.md)
- [teaching/12-maintainer-path.md](./teaching/12-maintainer-path.md)
- [teaching/13-harness-builder-path.md](./teaching/13-harness-builder-path.md)
- [teaching/14-first-hour-onboarding.md](./teaching/14-first-hour-onboarding.md)
- [teaching/15-newcomer-faq.md](./teaching/15-newcomer-faq.md)

### Skills Market 专题

- [teaching/16-skills-market-evolution.md](./teaching/16-skills-market-evolution.md)
- [teaching/17-market-registry-and-federation.md](./teaching/17-market-registry-and-federation.md)
- [teaching/18-skills-market-learning-map.md](./teaching/18-skills-market-learning-map.md)
- [teaching/19-market-packaging-and-publishing.md](./teaching/19-market-packaging-and-publishing.md)
- [teaching/20-market-client-operations.md](./teaching/20-market-client-operations.md)
- [teaching/21-market-governance-and-delivery.md](./teaching/21-market-governance-and-delivery.md)

## 这份文档索引适合谁

- 想先理解项目全貌的人：从 [teaching/README.md](./teaching/README.md) 开始。
- 想从 skill 设计逻辑入门的人：从 [skill-learning-guide.md](./skill-learning-guide.md) 开始。
- 想直接研究 market 分发链的人：从 [market-spec.md](./market-spec.md) 和 [market-registry.md](./market-registry.md) 开始。
- 想做前后端联调的人：从 [frontend-backend-integration.md](./frontend-backend-integration.md) 开始。
