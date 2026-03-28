# 前端 / 后端集成

## 目标

让 `frontend/` 下的 skills market 页面既能继续读取仓库里的真实产物，又能在需要时通过 Python backend 走真实执行链路，而不是停留在 copy-first demo。

当前这条集成链已经覆盖：

- skills / bundles / docs 的 repo-backed 浏览
- 本地 install / update / remove
- installed-state doctor / repair / baseline / governance
- waiver / apply handoff 的 `prepare / stage / verify`
- governance write handoff 的 eligibility、approval record、audit timeline、evidence pack 与 review checklist
- remote registry install 的 trust / approval / retry / cleanup / rollback
- docs action panel 的 allowlist backend 执行、copy fallback、前置条件状态与结果摘要

## 当前分层

### 1. 前端数据层

`frontend/lib/data.ts` 负责统一处理两种模式：

- 未配置 `SKILLS_MARKET_API_BASE_URL` 时，直接读取仓库产物
- 配置后，通过 Next.js API route 代理到 Python backend

它还负责把 skill / bundle / docs 数据整理成前端真正需要的结构，例如：

- docs 上下文面板
- action panel 的命令、执行模式、顺序、前置条件、预期产物与结果摘要
- remote execution 的 trust summary、policy gate、approval 文案

### 2. Next.js API 代理层

`frontend/app/api/` 是前端和 Python backend 之间的适配层。

当前已经覆盖：

- local lifecycle
- installed-state lifecycle
- remote registry lifecycle
- docs catalog 与详情
- docs action execution 代理

waiver / apply 相关代理包括：

- `/api/local/state/governance/waiver-apply`
- `/api/local/state/governance/waiver-apply/approval`
- `/api/local/state/governance/waiver-apply/prepare`
- `/api/local/state/governance/waiver-apply/stage`
- `/api/local/state/governance/waiver-apply/verify`
- `/api/local/docs/actions/run`

### 3. Python backend

`backend/app/main.py` 负责把真实脚本封装成 job API。

当前和页面执行链直接相关的接口是：

```text
GET /api/v1/local/state/governance
POST /api/v1/local/state/governance/refresh
GET /api/v1/local/state/governance/waiver-apply
POST /api/v1/local/state/governance/waiver-apply/approval
POST /api/v1/local/state/governance/waiver-apply/prepare
POST /api/v1/local/state/governance/waiver-apply/stage
POST /api/v1/local/state/governance/waiver-apply/verify
POST /api/v1/local/docs/actions/run
GET /api/v1/local/jobs/{job_id}
```

## Waiver / Apply 当前语义

页面现在已经能跑通一条完整的安全链路：

1. `prepare`
   生成 apply handoff pack、patch、report 和 CLI follow-up。
2. `stage`
   把治理源文件的变更安全写入专用 staging root，并刷新 aggregate report。
3. `verify`
   重新校验 staged 或 written 结果，并刷新 aggregate report。
4. `approval`
   页面把 operator note、当前 handoff 指纹和 evidence snapshot 持久化到治理快照目录，形成可追溯审批记录。
5. `write handoff`
   页面根据最新 report 汇总 `pending / ready / blocked / drifted / completed` 五种 write 状态，并给出 CLI write/verify 命令、planned governance source、review artifacts、approval checklist、approval audit 和 evidence pack。

需要特别说明：

- `stage` 和 `verify` 面向的是 governance staging flow，而不是 installed target root 本身
- `write` 仍然保持 CLI-only
- approval record 通过 backend 持久化，但仍然不会绕过 CLI write 边界
- audit timeline 会把当前 approval record 与旧记录分开显示；当 handoff 再次 stage / verify / write 后，旧记录会自动转入历史
- evidence pack 会把 apply / execute / verify / target root 等关键证据聚合展示，方便人工审批和事后复核
- handoff 的目标是把高风险动作解释清楚，而不是把 repo-source write 偷偷藏进 UI

为了兼容 Windows，本轮继续保持 staged artifact 的短名 + hash，避免超长路径导致 stage 失败。

## Playwright 覆盖点

当前 E2E 已覆盖这些关键路径：

- skill detail 本地 install -> doctor -> repair -> baseline -> governance refresh
- waiver / apply `prepare -> stage -> verify`
- `approval persisted -> audit trail visible -> restage invalidates old approval -> post-write evidence refreshed`
- remote registry install 的 approval / retry / cleanup / rollback
- docs 页面搜索、详情页 action panel、context panel、相关文档跳转与 project doc allowlist action 真执行

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

同时在 `frontend/next.config.js` 里把 `experimental.cpus` 收敛到更保守的值，减少 Windows 下 page-data 阶段偶发 `spawn UNKNOWN` 的风险。

推荐验证命令：

```text
python scripts/check_python_market_backend.py
python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-docs-action-execution
python scripts/check_docs_links.py
npm run build --prefix frontend
npm run e2e --prefix frontend
```
