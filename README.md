# Moyuan Skills Market

这是一个围绕 `skills market` 的中文参考仓库，覆盖 skill 设计、market 打包分发、安装后治理、作者提交流程，以及前后端联调。

## 当前状态

- 已落地：`scaffold-skill`、`doctor-skill`、`market-ready` 模板
- 已落地：submission `build / validate / upload / review / ingest`
- 已落地：backend author API、`/studio`、remote registry browse API
- 已落地：full-stack 与 `/studio` Playwright 覆盖
- 待继续：前端 `/registries/*` 页面、hosted publish service

前端默认使用 `next build --webpack`。Playwright 会优先复用仓库 `.venv` 的 Python，并固定单 worker 运行，减少 repo-backed 测试互踩。

## 文档地图

- 总索引：[docs/README.md](./docs/README.md)
- 环境与命令：[docs/setup/README.md](./docs/setup/README.md)
- Skill 制作：[docs/authoring/README.md](./docs/authoring/README.md)
- Harness：[docs/harness/README.md](./docs/harness/README.md)
- Market：[docs/market/README.md](./docs/market/README.md)
- 前后端联调：[docs/integration/README.md](./docs/integration/README.md)
- Roadmap：[docs/roadmap/README.md](./docs/roadmap/README.md)
- Skill 案例：[docs/skills/README.md](./docs/skills/README.md)
- 教学总览：[docs/teaching/README.md](./docs/teaching/README.md)

## 快速开始

```text
uv venv .venv
uv pip install --python .venv/bin/python -r backend/requirements.txt -r backend/requirements-dev.txt
npm ci --prefix frontend
PATH="$(pwd)/.venv/bin:$PATH"
python scripts/check_progressive_skills.py
python scripts/check_docs_links.py
python scripts/skills_market.py smoke
python scripts/check_python_market_backend.py
```

启动后端：

```text
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 38083
```

启动前端：

```text
SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083 \
npm run dev:local --prefix frontend
```

默认联调端口：

- frontend: `33003`
- backend: `38083`

## 当前能力

### Skill 制作

- `python scripts/skills_market.py scaffold-skill <name> --template market-ready`
- `python scripts/skills_market.py doctor-skill skills/<name> --run-checker`
- 入口文档见 [docs/authoring/skill-quickstart.md](./docs/authoring/skill-quickstart.md) 和 [docs/authoring/template-library.md](./docs/authoring/template-library.md)

### 提交与分发

- 统一 CLI 入口见 [scripts/skills_market.py](./scripts/skills_market.py)
- 规范见 [docs/market/market-spec.md](./docs/market/market-spec.md)
- 作者流程见 [docs/market/publisher-guide.md](./docs/market/publisher-guide.md)
- 消费侧流程见 [docs/market/consumer-guide.md](./docs/market/consumer-guide.md)
- registry 说明见 [docs/market/market-registry.md](./docs/market/market-registry.md)

### 安装后治理

- 本地 lifecycle 已支持 `install / update / remove / doctor / repair / baseline / governance`
- waiver / apply handoff 已支持 `prepare / stage / verify`
- 说明见 [docs/market/market-governance.md](./docs/market/market-governance.md)

### 前后端联调

- backend 说明见 [backend/README.md](./backend/README.md)
- API 与页面映射见 [docs/integration/frontend-backend-integration.md](./docs/integration/frontend-backend-integration.md)
- `/studio` 已接入 author submission workflow
- remote registry browse 已落到 CLI、backend API 和 Next.js 代理层

## 推荐阅读

1. [docs/teaching/README.md](./docs/teaching/README.md)
2. [docs/authoring/skill-learning-guide.md](./docs/authoring/skill-learning-guide.md)
3. [docs/market/market-spec.md](./docs/market/market-spec.md)
4. [docs/integration/frontend-backend-integration.md](./docs/integration/frontend-backend-integration.md)
5. [docs/roadmap/market-pull-author-publish-plan.md](./docs/roadmap/market-pull-author-publish-plan.md)

## 仓库结构

```text
.
|- backend/
|- frontend/
|- bundles/
|- docs/
|  |- authoring/
|  |- harness/
|  |- integration/
|  |- market/
|  |- roadmap/
|  |- setup/
|  |- skills/
|  `- teaching/
|- examples/
|- governance/
|- publishers/
|- schemas/
|- scripts/
|- skills/
`- templates/
```

## 常用验证

- `python scripts/check_progressive_skills.py`
- `python scripts/check_docs_links.py`
- `python scripts/check_harness_prototypes.py`
- `python scripts/check_market_governance.py`
- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-readme`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`

## 一句话定位

它是一套把 skill 设计、skills market、client lifecycle、治理与交付串成同一条链路的中文参考实现。
