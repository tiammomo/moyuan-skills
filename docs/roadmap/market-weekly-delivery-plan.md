# Skills 商店按周开发排期表

这份文档是 [market-pull-author-publish-plan.md](./market-pull-author-publish-plan.md) 的执行版。

这份排期保留原始周次设计，但当前代码快照已经提前覆盖 Week 1 到 Week 7 的交付范围。现在真正剩余的是 Week 8 到 Week 10 对应的 `/registries` UI、远端浏览到安装闭环，以及 hosted publish 预研。

## 1. 排期原则

- 先修工具链和作者链，再做 submission 上传，再做远端浏览，最后才进入 hosted publish。
- 每周必须有明确的代码交付、文档回写和验证命令，不接受“只讨论不落地”的空周。
- 每周结束时，都要留下可合并的最小闭环，而不是只留下半截接口。
- 如果某周目标未完成，顺延任务本身，不打乱后续 phase 顺序。

## 2. 原排期与当前状态

| 周次 | 日期 | 目标 | 当前状态 |
| --- | --- | --- | --- |
| Week 1 | 2026-04-06 至 2026-04-12 | 统一解释器、开发环境和脚手架执行基础 | 已完成 |
| Week 2 | 2026-04-13 至 2026-04-19 | 修稳作者链，补齐 `scaffold -> doctor -> validate -> checker` | 已完成 |
| Week 3 | 2026-04-20 至 2026-04-26 | 完成作者工作流闭环和作者文档回写 | 已完成 |
| Week 4 | 2026-04-27 至 2026-05-03 | 建立 submission schema 与 `build/validate` CLI | 已完成 |
| Week 5 | 2026-05-04 至 2026-05-10 | 完成 `upload/review/ingest` CLI 与 inbox 流程 | 已完成 |
| Week 6 | 2026-05-11 至 2026-05-17 | 接入 backend author API 与 frontend `/studio` 骨架 | 已完成 |
| Week 7 | 2026-05-18 至 2026-05-24 | 提供远端 registry 查询层和 browse API | 已完成 |
| Week 8 | 2026-05-25 至 2026-05-31 | 完成前端 `/registries` 页面和远端 trust summary | 待做 |
| Week 9 | 2026-06-01 至 2026-06-07 | 打通远端浏览到安装的端到端闭环 | 待做 |
| Week 10 | 2026-06-08 至 2026-06-14 | 做 hosted publish 的架构预研、稳定性收尾和版本验收 | 待做 |

下面各周的详细条目保留原始排期写法；是否已经完成，以这张状态表为准。

## 3. Week 1：工具链统一

日期：`2026-04-06` 至 `2026-04-12`

目标：

- 把本地解释器和开发环境约定统一到 `.venv` / `uv`。
- 清理文档中默认依赖裸 `python` 的表达。

交付物：

- 统一后的开发环境文档。
- 更新后的脚手架 next steps 文案。
- 至少一条稳定的本地 smoke 路径。

主要代码触点：

- `docs/setup/dev-setup.md`
- `docs/authoring/skill-quickstart.md`
- `docs/setup/repo-commands.md`
- `scripts/scaffold_skill.py`

验证命令：

```text
uv venv .venv
uv pip install --python .venv/bin/python -r backend/requirements.txt -r backend/requirements-dev.txt
PATH="$(pwd)/.venv/bin:$PATH" python scripts/check_python_market_backend.py
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py smoke
```

周完成标准：

- 团队成员不需要猜测该用 `python`、`python3` 还是系统环境。
- 文档和脚手架提示的执行方式一致。

## 4. Week 2：作者链修稳

日期：`2026-04-13` 至 `2026-04-19`

目标：

- 修复 `market-ready` 模板 checker 的路径兼容性。
- 保证 `scaffold -> doctor -> validate -> checker` 在默认路径和自定义路径都可用。

交付物：

- 修复后的 `check_skill.py.template`。
- 作者链 smoke 用例。
- `doctor-skill --run-checker` 通过的回归验证。

主要代码触点：

- `templates/skills/market-ready-skill/scripts/check_skill.py.template`
- `scripts/doctor_skill.py`
- `scripts/scaffold_skill.py`

验证命令：

```text
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py scaffold-skill smoke-skill --template market-ready --path dist/authoring-smoke
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py doctor-skill dist/authoring-smoke/smoke-skill --run-checker
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py validate dist/authoring-smoke/smoke-skill/market/skill.json
```

周完成标准：

- 自定义 `--path` 不再导致 checker 导入失败。
- 新生成 skill 能完成完整本地作者自检。

## 5. Week 3：作者工作流闭环

日期：`2026-04-20` 至 `2026-04-26`

目标：

- 把作者链正式收成一条可交付流程。
- 补齐作者文档与发布者文档。

交付物：

- 一套稳定的 beginner / advanced / market-ready 模板使用说明。
- 更新后的作者工作流文档。
- `package` 和 `provenance-check` 接在作者链末端。

主要代码触点：

- `docs/authoring/skill-authoring.md`
- `docs/market/publisher-guide.md`
- `templates/README.md`
- `scripts/package_skill.py`

验证命令：

```text
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py scaffold-skill release-helper --template market-ready --path dist/authoring-smoke
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py doctor-skill dist/authoring-smoke/release-helper
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py package release-note-writer
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py provenance-check dist/market/install/release-note-writer-0.1.0.json
```

周完成标准：

- 作者从创建到打包预览不需要跳出仓库外找额外流程说明。

## 6. Week 4：submission schema 与 build/validate

日期：`2026-04-27` 至 `2026-05-03`

目标：

- 定义 submission 数据模型。
- 先把 `build-submission` 和 `validate-submission` 做出来。

交付物：

- `schemas/skill-submission.schema.json`
- `schemas/skill-submission-review.schema.json`
- `scripts/build_skill_submission.py`
- `scripts/validate_skill_submission.py`
- `skills_market.py` 新子命令接入

主要代码触点：

- `schemas/`
- `scripts/`
- `docs/market/market-spec.md`

验证命令：

```text
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py build-submission release-note-writer
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py validate-submission dist/submissions/moyuan/release-note-writer/0.1.0/submission.json
```

周完成标准：

- submission 可以从 skill 源自动构建并独立校验。

## 7. Week 5：upload/review/ingest CLI

日期：`2026-05-04` 至 `2026-05-10`

目标：

- 完成 repo-compatible submission 流程。
- 打通 inbox、review、ingest、registry rebuild。

交付物：

- `scripts/upload_skill_submission.py`
- `scripts/review_skill_submission.py`
- `scripts/ingest_skill_submission.py`
- `incoming/submissions/` 约定

主要代码触点：

- `scripts/skills_market.py`
- `docs/market/publisher-guide.md`
- `docs/market/market-spec.md`

验证命令：

```text
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py upload-submission dist/submissions/moyuan/release-note-writer/0.1.0/submission.json --inbox-dir incoming/submissions
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py review-submission incoming/submissions/moyuan/release-note-writer/0.1.0/submission.json --review-status approved --summary "Submission passed inbox review."
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py ingest-submission incoming/submissions/moyuan/release-note-writer/0.1.0/submission.json
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py registry
```

周完成标准：

- maintainer 能基于 inbox 完成 review 和 ingest。
- ingest 后 registry 产物能刷新出来。

## 8. Week 6：author API 与 `/studio` 骨架

日期：`2026-05-11` 至 `2026-05-17`

目标：

- 把 submission CLI 暴露为 backend author API。
- 新增 frontend 作者工作台骨架。

交付物：

- `GET /api/v1/author/overview`
- `GET /api/v1/author/submissions`
- `POST /api/v1/author/submissions/build`
- `POST /api/v1/author/submissions/upload`
- `POST /api/v1/author/submissions/review`
- `POST /api/v1/author/submissions/ingest`
- `/studio`
- `/studio/new`
- `/studio/submissions`

主要代码触点：

- `backend/app/main.py`
- `frontend/app/studio/*`
- `docs/integration/frontend-backend-integration.md`

验证命令：

```text
PATH="$(pwd)/.venv/bin:$PATH" python scripts/check_python_market_backend.py
npm run build --prefix frontend
npm run e2e --prefix frontend
```

周完成标准：

- 作者和 maintainer 不必只靠终端，也能从页面触发 submission 流程。

## 9. Week 7：远端 registry 查询层

日期：`2026-05-18` 至 `2026-05-24`

目标：

- 把远端 registry 从“安装下载源”升级成“可查询数据源”。
- 先补 CLI 和 backend 的 browse 能力。

交付物：

- `search --registry`
- `catalog --registry`
- `inspect-remote-skill`
- `GET /api/v1/registry/remote/index`
- `GET /api/v1/registry/remote/channels/{channel}`
- `GET /api/v1/registry/remote/skills/{skill_id}`
- `GET /api/v1/registry/remote/bundles/{bundle_id}`

主要代码触点：

- `scripts/search_skills.py`
- `scripts/skills_market.py`
- `backend/app/main.py`
- 远端 registry 查询工具层

验证命令：

```text
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py search --registry http://127.0.0.1:8765 --query release
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py catalog --registry http://127.0.0.1:8765
```

周完成标准：

- 用户可以只知道 registry URL，不知道本地已有 skill，也能开始浏览远端技能。

## 10. Week 8：前端 registry 页面

日期：`2026-05-25` 至 `2026-05-31`

目标：

- 前端提供真实远端商店页面。
- trust summary 改为基于远端元数据构建。

交付物：

- `/registries`
- `/registries/[registryId]`
- `/registries/[registryId]/skills/[skillId]`
- registry profile 管理
- 新的 remote trust summary 组合逻辑

主要代码触点：

- `frontend/lib/data.ts`
- `frontend/app/registries/*`
- `frontend/types/market.ts`

验证命令：

```text
npm run build --prefix frontend
npm run e2e --prefix frontend
```

周完成标准：

- 用户可以从页面浏览未知远端 skill，而不是只能在本地 skill 详情页里输 URL。

## 11. Week 9：远端浏览到安装闭环

日期：`2026-06-01` 至 `2026-06-07`

目标：

- 把远端 browse、trust、install 真正串成一条端到端体验。
- 同步回写 consumer 侧文档。

交付物：

- registry 详情页直接触发 remote install
- browse -> trust review -> approval -> install 的完整前端交互
- 更新后的使用者文档和 registry 文档

主要代码触点：

- `frontend/app/registries/*`
- `frontend/components/market/*`
- `docs/market/consumer-guide.md`
- `docs/market/market-registry.md`

验证命令：

```text
npm run e2e --prefix frontend
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py install moyuan.release-note-writer --registry http://127.0.0.1:8765 --dry-run
```

周完成标准：

- 用户能在远端商店浏览页面里直接完成决策和安装。

## 12. Week 10：稳定性收尾与 Hosted Publish 预研

日期：`2026-06-08` 至 `2026-06-14`

目标：

- 完成第一轮主线验收。
- 把 Phase 4 的 hosted publish 收敛成架构方案和最小实现切片。

交付物：

- 10 周主线回归报告
- 当前缺口清单
- hosted publish RFC 或实施草图
- 下一阶段 backlog

主要代码触点：

- `docs/roadmap/market-pull-author-publish-plan.md`
- `docs/integration/frontend-backend-integration.md`
- backend publish 设计草稿

验证命令：

```text
PATH="$(pwd)/.venv/bin:$PATH" python scripts/check_docs_links.py
PATH="$(pwd)/.venv/bin:$PATH" python scripts/skills_market.py smoke
PATH="$(pwd)/.venv/bin:$PATH" python scripts/check_python_market_backend.py
npm run build --prefix frontend
npm run e2e --prefix frontend
```

周完成标准：

- Phase 0 到 Phase 3 都有可运行闭环。
- Phase 4 不直接拍脑袋开工，而是先有清晰边界和实施切片。

## 13. 周会执行模板

每周都按下面模板推进：

1. 周一确认本周目标、代码触点、文档触点和验收标准。
2. 周二到周四完成核心实现和最小验证。
3. 周五补文档、补测试、跑联调。
4. 周末前输出本周结果、阻塞点和下周接力项。

每周周报至少回答这 4 个问题：

1. 本周交付了什么最小闭环。
2. 哪些验证命令已经实际跑过。
3. 哪些风险还在，是否会影响下一周。
4. 哪些文档已经同步更新。

## 14. 使用说明

- 这份文档现在同时承担“原始排期 + 当前状态”两种职责，不再平行维护第二份历史表。
- 如果周次发生变化，直接整体更新这份文档，不再平行新增第二份周计划。
- Phase 完成后，应把“现状”回写到主线 roadmap 和权威文档，而不是只在周计划里记录。
