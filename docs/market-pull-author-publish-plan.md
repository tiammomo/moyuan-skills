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
- CLI 和前端 backend 都已经支持 remote install。
- `scaffold-skill`、`doctor-skill`、`market-ready` 模板已经落地。
- installed-state lifecycle、governance、remote install recovery 已经成型。

### 2.2 仍然缺失

- 远端消费还是“已知 skill 的 remote install”，不是“远端商店浏览与发现”。
- remote trust summary 仍然主要依赖本地 metadata，不是远端 registry 实时数据。
- 没有 submission schema、upload/review/ingest CLI、author API、`/studio` 页面。
- 作者链虽然已初步落地，但解释器约定、脚手架 checker 和路径兼容性还不够稳。

## 3. 开发顺序

必须按下面顺序推进：

1. Phase 0：工具链和作者链修正
2. Phase 1：作者工作流闭环
3. Phase 2：submission 上传闭环
4. Phase 3：远端商店浏览与拉取
5. Phase 4：hosted publish service

原因：

- 没有稳定作者链，上传链只能建立在脆弱输入上。
- 没有 submission 模型，后端 author API 和前端作者页都无法做干净。
- 没有远端浏览数据模型，remote install 永远只是“下载入口”，不是“商店入口”。

## 4. Phase 0：工具链和基础修正

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

- [dev-setup.md](./dev-setup.md)
- [skill-quickstart.md](./skill-quickstart.md)
- [repo-commands.md](./repo-commands.md)

### 4.5 完成标准

- 在仓库根目录能稳定完成一次 `scaffold -> doctor -> validate -> checker`。
- 文档不再假设系统一定存在裸 `python` 命令。
- 任何 Python 子进程执行路径都优先使用 `sys.executable` 或明确的环境解释器。

## 5. Phase 1：作者工作流闭环

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

- [skill-quickstart.md](./skill-quickstart.md)
- [skill-authoring.md](./skill-authoring.md)
- [publisher-guide.md](./publisher-guide.md)

### 5.5 验收标准

- 新 skill 可通过一条命令生成。
- 生成后的 skill 能继续执行 `doctor-skill`、`validate`、`package`、`provenance-check`。
- 作者不需要依赖仓库外脚手架或 `CODEX_HOME` 才能开始。

## 6. Phase 2：submission 上传闭环

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

- [publisher-guide.md](./publisher-guide.md)
- [market-spec.md](./market-spec.md)
- [frontend-backend-integration.md](./frontend-backend-integration.md)

### 6.6 验收标准

- 作者能从 skill 源码直接生成 submission。
- maintainer 能从 inbox review 并 ingest。
- ingest 后能重新生成 registry，且新 skill 可继续被远端安装。

## 7. Phase 3：远端商店浏览与拉取

### 7.1 目标

把 remote install 提升成真正的远端商店浏览体验。

### 7.2 需要交付

- 远端 registry 浏览 API。
- `search --registry`、`catalog --registry`、`inspect-remote-skill` CLI。
- 前端 registry 列表页、详情页、skill 详情页。
- 基于远端 manifest / publisher / provenance / install spec 的 trust summary。
- registry profile 管理，而不是只让用户手输 URL。

### 7.3 主要代码触点

- `scripts/search_skills.py`
- `scripts/skills_market.py`
- `scripts/install_remote_skill.py`
- `scripts/install_remote_bundle.py`
- `backend/app/main.py`
- `frontend/lib/data.ts`
- `frontend/app/registries/*`

### 7.4 需要同步维护的文档

- [consumer-guide.md](./consumer-guide.md)
- [market-registry.md](./market-registry.md)
- [frontend-backend-integration.md](./frontend-backend-integration.md)

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

先做下面 8 项，不要跳步：

1. 修复脚手架 checker 的 repo root 解析和解释器提示。
2. 把开发环境说明统一到 `uv` / `.venv`。
3. 把 `skill-quickstart`、`repo-commands`、`publisher-guide` 同步到新作者链。
4. 新增 submission schema。
5. 新增 `build-submission` / `validate-submission`。
6. 新增 `upload-submission` / `review-submission` / `ingest-submission`。
7. 新增 backend author submission API。
8. 新增 frontend `/studio` 系列页面。

## 10. 文档治理

后续文档按下面规则维护：

- 这份文档是唯一的开发主线，不再新增同级“下一轮路线图”。
- 某条能力线如果只是主线中的一个阶段，应直接回写到这里，不单独新建临时 roadmap。
- 根目录文档只保留当前有效的长期说明；一次性迭代记录和排障说明不再常驻 `docs/`。
- 功能落地后，必须同步回写对应权威文档，而不是继续依赖开发计划文档解释现状。
