# 前端 / 后端集成

## 目标

让 `frontend/` 下的 skills market 页面既能继续读取仓库里的真实产物，又能在需要时通过 Python backend 走真实执行链路，而不是停留在 copy-first demo。

当前这条集成链已经覆盖：

- skills / bundles / docs 的 repo-backed 浏览
- 本地 install / update / remove
- installed-state doctor / repair / baseline / governance
- waiver / apply handoff 的 prepare / stage / verify
- remote registry install 的 trust / approval / retry / cleanup / rollback

## 当前分层

### 1. 前端数据层

`frontend/lib/data.ts` 负责统一处理两种模式：

- 未配置 `SKILLS_MARKET_API_BASE_URL` 时，直接读仓库产物
- 配置后，通过 Next.js API route 代理到 Python backend

它还负责把 skill / bundle / docs 数据整理成前端真正需要的结构，例如：

- docs 上下文面板
- action panel 的命令、顺序、前置条件、预期产物
- remote execution 的 trust summary、policy gate、approval 文案

### 2. Next.js API 代理层

`frontend/app/api/` 是前端和 Python backend 之间的适配层。

当前已经覆盖：

- local lifecycle
- installed-state lifecycle
- remote registry lifecycle
- docs catalog 与详情

waiver / apply 现在新增了两条代理路由：

- `/api/local/state/governance/waiver-apply/stage`
- `/api/local/state/governance/waiver-apply/verify`

### 3. Python backend

`backend/app/main.py` 负责把真实脚本包装成 job API。

当前和 installed-state governance 直接相关的接口是：

```text
GET /api/v1/local/state/governance
POST /api/v1/local/state/governance/refresh
GET /api/v1/local/state/governance/waiver-apply
POST /api/v1/local/state/governance/waiver-apply/prepare
POST /api/v1/local/state/governance/waiver-apply/stage
POST /api/v1/local/state/governance/waiver-apply/verify
GET /api/v1/local/jobs/{job_id}
```

## waiver / apply 当前语义

页面现在已经能跑通一条完整的安全链路：

1. `prepare`
   生成 apply handoff pack、patch、report 和 CLI follow-up
2. `stage`
   把治理源文件的变更安全写入专用 staging root，并刷新 aggregate report
3. `verify`
   重新校验 staged 结果，并刷新 aggregate report

需要特别说明：

- `stage` 和 `verify` 面向的是 governance staging flow，而不是 installed target root 本身
- `write` 仍然保持 CLI-only
- 页面展示的是 report 聚合结果，不需要自行拼装 apply / execute / verify 三份摘要

为了兼容 Windows，本轮还把 staged artifact 文件名改成了短名 + hash，避免超长路径导致 stage 失败。

## remote install 当前语义

remote execution 卡片现在已经具备：

- trust summary
- policy gate
- explicit approval
- failed run 的 retry
- staged cache cleanup
- 限定在 `dist/frontend-remote-execution/` 作用域内的 rollback

也就是说，前端已经不仅能解释“怎么跑”，还能够解释“为什么不能跑”和“失败后先怎么清理”。

## 本地联调

推荐端口：

- frontend: `33003`
- backend: `38083`

启动 backend：

```text
pip install -r backend/requirements.txt
set MOYUAN_SKILLS_REPO_ROOT=D:\moyuan\moyuan-skills
set MOYUAN_SKILLS_API_CORS=http://127.0.0.1:33003,http://localhost:33003
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 38083
```

启动 frontend：

```text
set SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083
npm run dev:local --prefix frontend
```

## 构建与验证

当前前端构建默认使用：

```text
next build --webpack
```

同时在 `frontend/next.config.js` 里把 `experimental.cpus` 收敛到更保守的值，减少 Windows 上 page-data 阶段偶发 `spawn UNKNOWN` 的风险。

推荐验证命令：

```text
python scripts/check_python_market_backend.py
python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-governance-write-mode
python scripts/check_docs_links.py
npm run build --prefix frontend
npm run e2e --prefix frontend
```
