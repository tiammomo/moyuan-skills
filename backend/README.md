# Moyuan Skills Python Backend

这个后端把仓库里的真实 `market / docs / bundles / installed-state` 产物暴露成前端可消费的 API，并复用 `scripts/` 里的真实逻辑。

它直接服务于 `frontend/` 页面，读取的主要目录包括：

- `dist/market/index.json`
- `dist/market/channels/*.json`
- `dist/market/install/*.json`
- `skills/*/market/skill.json`
- `docs/skills/*.md`
- `docs/teaching/**/*.md`
- `docs/{setup,authoring,harness,market,integration,roadmap}/*.md`
- `bundles/*.json`

## 启动

推荐先按 [../docs/setup/dev-setup.md](../docs/setup/dev-setup.md) 建好 `.venv` 和前端依赖。

```text
uv venv .venv
uv pip install --python .venv/bin/python -r backend/requirements.txt -r backend/requirements-dev.txt
PATH="$(pwd)/.venv/bin:$PATH"
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 38083
```

如果当前工作目录不是仓库根目录，可以设置：

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
GET /api/v1/author/overview
GET /api/v1/author/submissions
POST /api/v1/author/submissions/build
POST /api/v1/author/submissions/upload
POST /api/v1/author/submissions/review
POST /api/v1/author/submissions/ingest
GET /api/v1/registry/remote/index
GET /api/v1/registry/remote/channels/{channel}
GET /api/v1/registry/remote/skills/{skill_id}
GET /api/v1/registry/remote/bundles/{bundle_id}
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
POST /api/v1/local/state/governance/waiver-apply/approval
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
GET /api/v1/local/docs/actions/history
POST /api/v1/local/docs/actions/run
GET /api/v1/docs/catalog
GET /api/v1/docs/teaching/{doc_id}
GET /api/v1/docs/project/{doc_id}
```

## 当前闭环

- author studio 的 `build / upload / review / ingest`
- 本地 skill / bundle lifecycle
- installed-state 的 doctor、repair、baseline、governance
- waiver / apply handoff 的 `prepare / stage / verify`
- remote registry browse 与 install
- docs action panel 的 allowlist 执行、recent runs 和 last-success

其中 waiver / apply 当前语义是：

- `prepare` 只生成 review pack
- `stage` 把治理源文件变更安全写入专用 staging root，并刷新 aggregate report
- `verify` 重新校验 staged 或 written 结果，并刷新 aggregate report
- `write` 仍然保持 CLI-only，不从页面直接写 repo governance source
- `GET /api/v1/local/state/governance/waiver-apply` 会额外返回 `write_handoff` 和 `approval_audit`，供前端解释 `pending / ready / blocked / drifted / completed` 五种 write 状态，以及当前审批记录与历史时间线
- `POST /api/v1/local/state/governance/waiver-apply/approval` 会把 operator note、evidence snapshot 与当前 handoff 指纹持久化到治理快照目录

另外，Windows 下的 staging 文件名已经做了短名 + hash 处理，避免超长路径导致 stage 失败。

## 前端对接说明

- 前端所有 mutation 都通过 Next.js API route 代理到这里
- mutation 返回 `job_id`
- 页面通过 `GET /api/v1/local/jobs/{job_id}` 轮询 job 完成状态
- `/studio`、`/studio/new`、`/studio/submissions` 通过 author API 暴露 submission workflow，并默认把 ingest 指向 `dist/backend-author-ingested/*` staging 目录
- `GET /api/v1/author/overview` 和 `GET /api/v1/author/submissions` 额外支持 `submissions_root` / `inbox_root`，用于隔离 author workspace 或测试目录
- `GET /api/v1/registry/remote/*` 当前主要供 CLI、Next.js 代理层和后续 `/registries/*` 页面复用；远端 browse 页面本身还没有落地
- docs catalog 同时返回按类型分组的数组和统一的 `all_docs`，并支持递归扫描 `docs/**`
- docs 详情页通过 `POST /api/v1/local/docs/actions/run` 触发安全 allowlist 命令，而不是把任意命令字符串直接交给后端
- docs 详情页通过 `GET /api/v1/local/docs/actions/history` 回看当前 backend 会话里的 recent runs 与 last-success

## 本地联调

推荐端口：

- frontend: `33003`
- backend: `38083`

前端 API 模式：

```text
npm ci --prefix frontend
SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083 \
npm run dev:local --prefix frontend
```

## 验证

```text
python scripts/check_python_market_backend.py
python scripts/check_market_pipeline.py --output-root dist/market-smoke-backend-readme
python scripts/check_docs_links.py
npm run build --prefix frontend
npm run e2e --prefix frontend
```

其中 `npm run e2e --prefix frontend` 依赖已有 `.next` 构建产物，并会优先使用仓库 `.venv` 里的 Python 启动 backend 和 registry fixture。
