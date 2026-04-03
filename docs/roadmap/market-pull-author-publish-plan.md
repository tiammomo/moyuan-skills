# Skills 商店后续开发主线

这份文档现在是项目后续开发的唯一主线 roadmap。

目标是把仓库从“repo-backed skills market 参考实现”推进到“能拉取、能制作、能上传、能远端浏览”的可交付技能商店。

具体按周执行排期见 [market-weekly-delivery-plan.md](./market-weekly-delivery-plan.md)。

## 1. 最终目标

项目需要补齐 3 条闭环：

1. 消费者可以从远端商店浏览未知 skill，并决定是否拉取。
2. 作者可以在仓库内快速制作一个 market-ready skill。
3. 发布者可以把新 skill 走完 submission、review、ingest 和 registry rebuild。

完整目标链路是：

`dev setup -> scaffold skill -> doctor/validate -> package -> build submission -> upload -> review -> ingest -> rebuild registry -> remote browse -> remote install`

## 2. 当前现状

### 2.1 已经具备

- 本地 `package -> install spec -> provenance -> install` 闭环。
- hosted registry 静态输出。
- repo-compatible `build / validate / upload / review / ingest` submission 闭环。
- backend author API 和前端 `/studio`、`/studio/new`、`/studio/submissions`。
- `search --registry`、`catalog --registry`、`inspect-remote-skill` 和 backend remote browse API。
- CLI 和前端 backend 都已经支持 remote install。
- `scaffold-skill`、`doctor-skill`、`market-ready` 模板已经落地。
- installed-state lifecycle、governance、remote install recovery 已经成型。

### 2.2 仍然缺失

- 远端 browse 还缺前端 `/registries/*` 页面和 registry profile 管理。
- remote trust summary 还没有从“本地 skill 详情页里的 install gate”升级成“远端浏览页里的独立 UI”。
- hosted publish 还没有 credential / namespace / object storage / review queue。
- hosted publish 之前的权限、审核状态机和 publisher dashboard 也还没有落地。

## 3. 开发顺序

必须按下面顺序推进：

1. Phase 0：工具链和作者链修正（已完成）
2. Phase 1：作者工作流闭环（已完成）
3. Phase 2：submission 上传闭环（已完成）
4. Phase 3：远端商店浏览与拉取（进行中）
5. Phase 4：hosted publish service（未开始）

原因：

- 没有稳定作者链，上传链只能建立在脆弱输入上。
- hosted publish 应该建立在已经稳定的 submission 模型和 author API 之上，而不是绕开 repo-compatible 交接边界。
- 没有前端远端浏览页和 trust summary UI，remote install 仍然更像“下载入口”，不是完整“商店入口”。

## 4. Phase 0：工具链和基础修正（已完成）

### 4.1 目标

把当前已经落地的作者链修稳，消除会影响后续开发的基础问题。

### 4.2 必做项

- 统一 Python 子进程解释器来源，避免文档、脚本和环境约定不一致。
- 把开发环境说明统一到 `uv` / `.venv` 工作流。
- 修复 `scaffold-skill` 生成 checker 在非默认路径下的导入问题。
- 统一脚手架输出的 next steps，避免继续提示不可用的解释器调用方式。

### 4.3 主要代码触点

- `scripts/scaffold_skill.py`
- `templates/skills/market-ready-skill/scripts/check_skill.py.template`
- `scripts/doctor_skill.py`
- `scripts/check_python_market_backend.py`
- `backend/app/main.py`

### 4.4 需要同步维护的文档

- [dev-setup.md](../setup/dev-setup.md)
- [skill-quickstart.md](../authoring/skill-quickstart.md)
- [repo-commands.md](../setup/repo-commands.md)

### 4.5 完成标准

- 在仓库根目录能稳定完成一次 `scaffold -> doctor -> validate -> checker`。
- 文档不再假设系统一定存在裸 `python` 命令。
- 任何 Python 子进程执行路径都优先使用 `sys.executable` 或明确的环境解释器。

## 5. Phase 1：作者工作流闭环（已完成）

### 5.1 目标

让作者在仓库内顺手完成“创建 skill -> 自检 -> 打包预览”。

### 5.2 需要交付

- `scaffold-skill` 支持稳定生成 beginner / advanced / market-ready 三类骨架。
- `doctor-skill` 能清晰覆盖 frontmatter、agents、manifest、checker、publisher profile、bundle 引用。
- 一个清晰的作者工作流文档，把“创建 -> 校验 -> 打包 -> provenance-check”串起来。

### 5.3 主要代码触点

- `scripts/scaffold_skill.py`
- `scripts/doctor_skill.py`
- `scripts/package_skill.py`
- `scripts/skills_market.py`
- `templates/skills/*`

### 5.4 需要同步维护的文档

- [skill-quickstart.md](../authoring/skill-quickstart.md)
- [skill-authoring.md](../authoring/skill-authoring.md)
- [publisher-guide.md](../market/publisher-guide.md)

### 5.5 验收标准

- 新 skill 可通过一条命令生成。
- 生成后的 skill 能继续执行 `doctor-skill`、`validate`、`package`、`provenance-check`。
- 作者不需要依赖仓库外脚手架或 `CODEX_HOME` 才能开始。

## 6. Phase 2：submission 上传闭环（已完成）

### 6.1 目标

把“手工 package / registry”升级成标准 submission 流程。

### 6.2 需要交付

- `skill submission` 数据模型。
- `build-submission`、`validate-submission`、`upload-submission`、`review-submission`、`ingest-submission` CLI。
- repo inbox 目录和 maintainer review/ingest 语义。
- backend author API。
- frontend 作者入口：`/studio`、`/studio/new`、`/studio/submissions`。

### 6.3 建议数据落盘

- `dist/submissions/<publisher>/<skill>/<version>/submission.json`
- `dist/submissions/<publisher>/<skill>/<version>/payload.tgz`
- `incoming/submissions/<publisher>/<skill>/<version>/`

### 6.4 主要代码触点

- `schemas/skill-submission.schema.json`
- `schemas/skill-submission-review.schema.json`
- `scripts/build_skill_submission.py`
- `scripts/validate_skill_submission.py`
- `scripts/upload_skill_submission.py`
- `scripts/review_skill_submission.py`
- `scripts/ingest_skill_submission.py`
- `scripts/skills_market.py`
- `backend/app/main.py`
- `frontend/app/studio/*`

### 6.5 需要同步维护的文档

- [publisher-guide.md](../market/publisher-guide.md)
- [market-spec.md](../market/market-spec.md)
- [frontend-backend-integration.md](../integration/frontend-backend-integration.md)

### 6.6 验收标准

- 作者能从 skill 源码直接生成 submission。
- maintainer 能从 inbox review 并 ingest。
- ingest 后能重新生成 registry，且新 skill 可继续被远端安装。

## 7. Phase 3：远端商店浏览与拉取（进行中）

### 7.1 目标

把 remote install 提升成真正的远端商店浏览体验。

### 7.2 需要交付

- 已完成：远端 registry 浏览 API。
- 已完成：`search --registry`、`catalog --registry`、`inspect-remote-skill` CLI。
- 待完成：前端 registry 列表页、详情页、skill 详情页。
- 待完成：基于远端 manifest / publisher / provenance / install spec 的 trust summary UI。
- 待完成：registry profile 管理，而不是只让用户手输 URL。

### 7.3 主要代码触点

- `scripts/search_skills.py`
- `scripts/catalog_remote_registry.py`
- `scripts/inspect_remote_skill.py`
- `scripts/skills_market.py`
- `scripts/install_remote_skill.py`
- `scripts/install_remote_bundle.py`
- `backend/app/main.py`
- `frontend/app/api/registry/remote/*`
- `frontend/lib/data.ts`
- `frontend/app/registries/*`

### 7.4 需要同步维护的文档

- [consumer-guide.md](../market/consumer-guide.md)
- [market-registry.md](../market/market-registry.md)
- [frontend-backend-integration.md](../integration/frontend-backend-integration.md)

### 7.5 验收标准

- 用户不依赖本地已有同名 skill，也能浏览远端 registry。
- 用户能搜索、查看详情、阅读 trust summary，再决定是否安装。
- 前端远端详情页可以直接触发 remote install。

## 8. Phase 4：Hosted Publish Service

### 8.1 目标

在 repo-compatible submission 稳定后，再升级成真正的 hosted 上传平台。

### 8.2 需要交付

- publisher credential 或 namespace 认证。
- hosted upload API。
- object storage / artifact store。
- review queue、accept/reject 状态机。
- publisher dashboard。

### 8.3 主要代码触点

- backend publish API
- artifact storage integration
- submission state machine
- frontend publisher dashboard

### 8.4 验收标准

- publisher 能独立提交新版本。
- maintainer 能在 hosted queue 中 review 和决策。
- accept 后 registry 自动更新并暴露给远端浏览入口。

## 9. 当前 backlog 优先级

当前只剩下面 8 项，不要跳步：

1. 新增前端 `/registries` 列表页。
2. 新增前端 `/registries/[registryId]` 和远端 skill / bundle 详情页。
3. 把 remote trust summary 从本地 detail gate 升级成远端浏览页的独立 UI。
4. 新增 registry profile 管理，而不是每次手输 URL。
5. 把 remote browse -> install 做成前端端到端闭环。
6. 设计 publisher credential / namespace 认证边界。
7. 接入 artifact storage / review queue / submission 状态机。
8. 新增 publisher dashboard 和 hosted publish 提交流程。

## 10. 文档治理

后续文档按下面规则维护：

- 这份文档是唯一的开发主线，不再新增同级“下一轮路线图”。
- 某条能力线如果只是主线中的一个阶段，应直接回写到这里，不单独新建临时 roadmap。
- 根目录文档只保留当前有效的长期说明；一次性迭代记录和排障说明不再常驻 `docs/`。
- 功能落地后，必须同步回写对应权威文档，而不是继续依赖开发计划文档解释现状。
