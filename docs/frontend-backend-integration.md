# 前端 / 后端集成

## 目标

让 `frontend/` 下的 skills market UI 在不改路由结构的前提下同时支持两种模式：

- 文件系统模式：直接读取仓库中的静态产物与文档
- API 模式：通过 Python FastAPI 后端走真实的前后端联调

当前仓库已经同时支持这两种模式。

## 当前实现

### 1. Python backend

后端位于 `backend/`，负责把仓库里已经生成好的 market、bundle、docs 与 installed-state 数据暴露成前端友好的 API。

当前核心接口包括：

- `GET /health`
- `GET /api/v1/market/index`
- `GET /api/v1/market/channels/{channel}`
- `GET /api/v1/market/skills`
- `GET /api/v1/market/skills/{name}`
- `GET /api/v1/market/skills/{name}/install-spec`
- `GET /api/v1/market/skills/{name}/doc`
- `GET /api/v1/market/categories`
- `GET /api/v1/market/tags`
- `GET /api/v1/market/bundles`
- `GET /api/v1/market/bundles/{bundle_id}`
- `POST /api/v1/local/skills/install`
- `POST /api/v1/local/skills/update`
- `POST /api/v1/local/skills/remove`
- `POST /api/v1/local/bundles/install`
- `POST /api/v1/local/bundles/update`
- `POST /api/v1/local/bundles/remove`
- `GET /api/v1/local/state`
- `GET /api/v1/local/state/baseline`
- `POST /api/v1/local/state/baseline/promote`
- `GET /api/v1/local/state/governance`
- `POST /api/v1/local/state/governance/refresh`
- `GET /api/v1/local/state/governance/waiver-apply`
- `POST /api/v1/local/state/governance/waiver-apply/prepare`
- `POST /api/v1/local/state/doctor`
- `POST /api/v1/local/state/repair`
- `POST /api/v1/registry/skills/install`
- `POST /api/v1/registry/bundles/install`
- `POST /api/v1/registry/cleanup`
- `POST /api/v1/registry/rollback`
- `GET /api/v1/local/jobs/{job_id}`
- `GET /api/v1/docs/catalog`
- `GET /api/v1/docs/teaching/{doc_id}`
- `GET /api/v1/docs/project/{doc_id}`

后端现在不仅提供只读浏览能力，也已经覆盖了本地 lifecycle、installed-state、remote registry install、remote cleanup 和受限作用域的 remote rollback。

### 2. 前端数据层

`frontend/lib/data.ts` 是前端统一的数据入口。

它负责：

- 在 `SKILLS_MARKET_API_BASE_URL` 未设置时走文件系统模式
- 在 `SKILLS_MARKET_API_BASE_URL` 已设置时走 FastAPI 模式
- 为 skill / bundle 详情页生成 remote trust summary、policy gate 状态、approval 文案与恢复提示
- 为 docs 详情页补齐上下文面板、运行顺序、前置条件、预期结果和产物提示

前端代理路由位于 `frontend/app/api/`，会把本地 lifecycle、installed-state 和 registry 相关请求统一转发到 Python backend。

### 3. 页面能力

当前前端已经具备这些集成能力：

- 首页、skills、bundles、docs 全部走 repo-backed 数据
- skill / bundle 详情页同时保留 copy-first CLI 指引和 backend execution 卡片
- installed-state 面板可读取 state、doctor、repair、baseline、governance、waiver/apply prepare
- remote execution 卡片现在具备：
  - trust summary
  - 明确的 policy gate 状态
  - approval 复选确认
  - retry
  - staged cache cleanup
  - 受限作用域的 remote target rollback

其中 rollback 只允许清理 `dist/frontend-remote-execution/` 下的专用远端目标目录，避免把通用本地安装目录误删成高风险动作。

### 4. 仓库数据来源

前后端共享的数据来源仍然是仓库中的真实产物：

- `dist/market/index.json`
- `dist/market/channels/*.json`
- `dist/market/install/*.json`
- `skills/*/market/skill.json`
- `docs/*.md`
- `docs/teaching/*.md`
- `bundles/*.json`

`docs/*-iteration.md` 这种临时规划文档会继续从 docs catalog 中排除，保证前端只展示面向用户的稳定文档。

## 本地联调

推荐端口：

- frontend: `33003`
- backend: `38083`

### 启动 backend

```text
pip install -r backend/requirements.txt
set MOYUAN_SKILLS_REPO_ROOT=D:\moyuan\moyuan-skills
set MOYUAN_SKILLS_API_CORS=http://127.0.0.1:33003,http://localhost:33003
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 38083
```

### 启动 frontend API 模式

```text
set SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083
npm run dev:local --prefix frontend
```

### 启动远端 registry fixture

如果要手动验证远端安装与 rollback，可以再开一个终端：

```text
python scripts/serve_market_registry_fixture.py --host 127.0.0.1 --port 38765 --output-dir dist/playwright-registry --clean
```

## 构建与验证

当前 `npm run build --prefix frontend` 默认走 `next build --webpack`。

这样做的原因是：在当前 Windows 环境里，Next.js 默认 Turbopack 构建多次稳定复现 worker 异常退出，而同一份代码走 webpack 可以完整通过静态页生成与类型检查。为了保证仓库里的默认验证命令稳定可复现，构建脚本先固定到 webpack。

推荐最小验证集合：

```text
python scripts/check_python_market_backend.py
python -m compileall backend
python scripts/check_docs_links.py
npm run build --prefix frontend
npm run e2e --prefix frontend
```

## Playwright 覆盖

E2E 现在覆盖的核心联调链路包括：

- 首页、skills、bundles、docs 的 API 模式加载
- skill / bundle 本地 install、update、remove
- installed-state doctor、repair、baseline、governance、waiver/apply prepare
- 远端 registry install
- 远端 trust summary、policy gate、approval
- 远端失败后的 retry、cleanup、rollback
- 至少一条被 policy gate 阻断的远端路径

相关文件：

- `frontend/playwright.config.ts`
- `frontend/tests/e2e/full-stack.spec.ts`
- `frontend/tests/e2e/readme-screenshots.spec.ts`

## 当前结论

这条前后端集成链路已经不再只是“浏览型 demo”，而是一个可运行、可验证、可扩展的产品化雏形：

- 浏览与教学链路已经完整
- 本地 lifecycle 已经能在页面内闭环
- 远端 install 已经具备第一轮风险提示与恢复动作
- 更深的治理 write-mode 执行仍然留在下一轮迭代

下一轮规划见 [frontend-governance-write-mode-iteration.md](./frontend-governance-write-mode-iteration.md)。
