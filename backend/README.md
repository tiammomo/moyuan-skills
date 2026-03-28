# Moyuan Skills Python Backend

这个后端把当前仓库里的真实 `market / docs / bundles / installed-state` 产物暴露成前端可直接消费的 API。

它服务于 `frontend/` 下的 Next.js 页面，也复用仓库现有的脚本和产物目录，例如：

- `dist/market/index.json`
- `dist/market/channels/*.json`
- `dist/market/install/*.json`
- `skills/*/market/skill.json`
- `docs/*.md`
- `docs/teaching/*.md`
- `bundles/*.json`

## 为什么需要这个后端

前端现在已经不只是静态浏览页，而是要承接这些真实动作：

- skills / bundles / docs 的 repo-backed 浏览
- skill / bundle 的本地 `install / update / remove`
- installed-state 的 `doctor / repair / baseline / governance`
- waiver / apply handoff 的 `prepare / stage / verify`
- governance write handoff 的 eligibility、approval guidance、evidence pack 与工件交接
- remote registry install 的 trust / approval / retry / cleanup / rollback

这些能力都应该直接复用 `scripts/` 里的真实逻辑，而不是在前端重写一套。

## 启动

```text
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 38083
```

开发辅助依赖单独放在：

```text
pip install -r backend/requirements-dev.txt
```

如果当前工作目录不是仓库根目录，可以先设置：

```text
set MOYUAN_SKILLS_REPO_ROOT=D:\moyuan\moyuan-skills
```

可选的 CORS 覆盖：

```text
set MOYUAN_SKILLS_API_CORS=http://127.0.0.1:33003,http://localhost:33003
```

## 核心接口

```text
GET /health
GET /api/v1/meta/repo
GET /api/v1/market/index
GET /api/v1/market/channels/{channel}
GET /api/v1/market/skills
GET /api/v1/market/skills/{name}
GET /api/v1/market/skills/{name}/install-spec
GET /api/v1/market/skills/{name}/doc
GET /api/v1/market/categories
GET /api/v1/market/tags
GET /api/v1/market/bundles
GET /api/v1/market/bundles/{bundle_id}
POST /api/v1/local/skills/install
POST /api/v1/local/skills/update
POST /api/v1/local/skills/remove
POST /api/v1/local/bundles/install
POST /api/v1/local/bundles/update
POST /api/v1/local/bundles/remove
GET /api/v1/local/state
GET /api/v1/local/state/baseline
POST /api/v1/local/state/baseline/promote
GET /api/v1/local/state/governance
POST /api/v1/local/state/governance/refresh
GET /api/v1/local/state/governance/waiver-apply
POST /api/v1/local/state/governance/waiver-apply/prepare
POST /api/v1/local/state/governance/waiver-apply/stage
POST /api/v1/local/state/governance/waiver-apply/verify
POST /api/v1/local/state/doctor
POST /api/v1/local/state/repair
POST /api/v1/registry/skills/install
POST /api/v1/registry/bundles/install
POST /api/v1/registry/cleanup
POST /api/v1/registry/rollback
GET /api/v1/local/jobs/{job_id}
GET /api/v1/docs/catalog
GET /api/v1/docs/teaching/{doc_id}
GET /api/v1/docs/project/{doc_id}
```

## 当前闭环

后端现在已经稳定支撑这些页面动作：

- 本地 skill / bundle lifecycle
- installed-state doctor、低风险 repair、baseline history、governance summary
- waiver / apply handoff 的 `prepare / safe stage / refresh verify`
- governance write handoff 的状态说明、阻断原因、命令包、approval guidance、evidence pack 与 checklist
- remote registry install 的审批、失败恢复、staged cache cleanup、限定目标 rollback

其中 waiver / apply 当前语义是：

- `prepare` 只生成 review pack
- `stage` 把治理源文件变更安全写入专用 staging root，并刷新 aggregate report
- `verify` 重新校验 staged 或 written 结果，并刷新 aggregate report
- `write` 仍然保持 CLI-only，不从页面直接写 repo governance source
- `GET /api/v1/local/state/governance/waiver-apply` 会额外返回 `write_handoff`，供前端解释 `pending / ready / blocked / drifted / completed` 五种 write 状态
- `write_handoff` 同时包含 approval guidance 和 evidence pack，帮助页面解释审批边界与事后复核材料

另外，Windows 下的 staging 文件名已经做了短名 + hash 处理，避免超长路径导致 stage 失败。

## 前端对接说明

- 前端所有 mutation 都通过 Next.js API route 代理到这里
- mutation 返回 `job_id`
- 页面通过 `GET /api/v1/local/jobs/{job_id}` 轮询 job 完成状态
- docs catalog 同时返回按类型分组的数组和统一的 `all_docs`

## 本地联调

推荐端口：

- frontend: `33003`
- backend: `38083`

前端 API 模式：

```text
set SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083
npm run dev:local --prefix frontend
```

## 验证

```text
python scripts/check_python_market_backend.py
python scripts/check_docs_links.py
npm run build --prefix frontend
npm run e2e --prefix frontend
```
