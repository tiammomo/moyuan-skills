# Moyuan Skills Market

这是一个面向 `skills market` 的中文教学型参考仓库，覆盖从 skill 设计、market 分发、client lifecycle、governance 到前后端联调的完整链路。

## 最新进展

这一轮把 docs action 再往前推进了一步，从“能顺着差异提示直接打开最值得先看的 drilldown”补到了“能先在 summary 层给出可扫描的 before / after 差异摘录”：

- docs action 现在除了 recent runs compare / filter、run diff summary 和 quick-open handoff，还会给出 artifact / stdout / stderr 的 inline diff excerpts
- result summary 会直接展示 selected run 与 pinned success 的 before / after 摘录，帮助用户先判断要不要展开完整 drilldown
- artifact / stdout / stderr 卡片仍然保留 changed、stable、baseline、empty 等状态，并继续高亮当前最值得先看的区块
- docs action history 仍然通过安全的 `doc kind + doc id + action id` 映射读取，前端只消费 allowlist action 的最近记录
- Playwright 已覆盖 docs action 的 diff summary、inline diff excerpts、quick-open handoff、失败输出复盘，以及刷新后的 last-success revisit

前端构建当前默认仍使用 `next build --webpack`，并在 [frontend/next.config.js](./frontend/next.config.js) 中把 `experimental.cpus` 收敛到更保守的值，减少 Windows 环境里 page-data 阶段偶发 `spawn UNKNOWN` 的风险。

## 当前能力

### 1. Skills 教学与案例

- skill 设计与学习路径见 [docs/skill-learning-guide.md](./docs/skill-learning-guide.md)
- 快速上手见 [docs/skill-quickstart.md](./docs/skill-quickstart.md)
- 渐进式披露与 harness 参考见 [docs/progressive-disclosure.md](./docs/progressive-disclosure.md) 和 [docs/harness-engineering.md](./docs/harness-engineering.md)
- 飞书与语雀案例见 [docs/feishu-doc-sync.md](./docs/feishu-doc-sync.md) 和 [docs/yuque-openapi.md](./docs/yuque-openapi.md)

### 2. Skills Market 与分发

- package / index / catalog / recommendations / federation / registry 都有本地脚本入口
- 统一 CLI 入口见 [scripts/skills_market.py](./scripts/skills_market.py)
- 规范与发布说明见 [docs/market-spec.md](./docs/market-spec.md)、[docs/publisher-guide.md](./docs/publisher-guide.md)、[docs/consumer-guide.md](./docs/consumer-guide.md)
- registry / federation 说明见 [docs/market-registry.md](./docs/market-registry.md)

### 3. Client Lifecycle 与治理

- install / update / remove / bundle / doctor / repair / baseline / governance / waiver / apply handoff / gate 已经全部落地
- installed-state 可以从页面跑通 doctor、低风险 repair、baseline capture、governance refresh
- waiver / apply 可以从页面跑通 `prepare / stage / verify`，并页面化展示 write handoff、approval record、audit timeline 和 evidence pack
- 治理说明见 [docs/market-governance.md](./docs/market-governance.md)

### 4. 前后端联调

- Python backend 说明见 [backend/README.md](./backend/README.md)
- 契约与页面映射见 [docs/frontend-backend-integration.md](./docs/frontend-backend-integration.md)
- skill / bundle 详情页支持真实 backend 本地执行与远端 registry install
- docs 详情页现在会把 repo 命令、安全执行状态、recent runs、compare / filter、run diff summary、inline diff excerpts、section diff 状态、quick-open handoff、last-success、artifact/stdout/stderr drilldown、顺序提示、前置条件、预期结果和产物提示一起展示，并为 allowlist 动作提供页内执行入口
- Playwright 已覆盖首页、skills、bundles、docs、`/studio` 以及详情页的端到端联调

## 中文 Skills 教学入口

推荐按下面的顺序学习：

1. [docs/teaching/README.md](./docs/teaching/README.md)
2. [docs/teaching/14-first-hour-onboarding.md](./docs/teaching/14-first-hour-onboarding.md)
3. [docs/skill-learning-guide.md](./docs/skill-learning-guide.md)
4. [docs/teaching/18-skills-market-learning-map.md](./docs/teaching/18-skills-market-learning-map.md)
5. [docs/teaching/22-doc-sync-skill-case-studies.md](./docs/teaching/22-doc-sync-skill-case-studies.md)

如果更关心真实案例，可以直接看：

- [docs/feishu-doc-sync.md](./docs/feishu-doc-sync.md)
- [docs/yuque-openapi.md](./docs/yuque-openapi.md)

## 快速开始

### 1. 先跑基础校验

```text
python scripts/check_progressive_skills.py
python scripts/skills_market.py smoke
python scripts/check_python_market_backend.py
```

### 2. 启动后端

```text
pip install -r backend/requirements.txt
set MOYUAN_SKILLS_REPO_ROOT=D:\moyuan\moyuan-skills
set MOYUAN_SKILLS_API_CORS=http://127.0.0.1:33003,http://localhost:33003
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 38083
```

开发辅助依赖单独放在：

```text
pip install -r backend/requirements-dev.txt
```

### 3. 启动前端

```text
set SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083
npm run dev:local --prefix frontend
```

默认联调端口：

- frontend: `33003`
- backend: `38083`

## 核心文档

- 文档总索引：[docs/README.md](./docs/README.md)
- 教学总入口：[docs/teaching/README.md](./docs/teaching/README.md)
- skills 学习指南：[docs/skill-learning-guide.md](./docs/skill-learning-guide.md)
- market 规范：[docs/market-spec.md](./docs/market-spec.md)
- market 治理：[docs/market-governance.md](./docs/market-governance.md)
- registry / federation：[docs/market-registry.md](./docs/market-registry.md)
- 前后端集成：[docs/frontend-backend-integration.md](./docs/frontend-backend-integration.md)
- 后续开发主线：[docs/market-pull-author-publish-plan.md](./docs/market-pull-author-publish-plan.md)
- 按周开发排期：[docs/market-weekly-delivery-plan.md](./docs/market-weekly-delivery-plan.md)
- 开发环境准备：[docs/dev-setup.md](./docs/dev-setup.md)
- 常用验证命令：[docs/repo-commands.md](./docs/repo-commands.md)

## 仓库结构

```text
.
|- backend/
|  |- requirements.txt
|  `- requirements-dev.txt
|- frontend/
|- bundles/
|- docs/
|  `- teaching/
|- examples/
|- governance/
|- publishers/
|- schemas/
|- scripts/
|- skills/
`- templates/
```

## 常用验证命令

- `python scripts/check_progressive_skills.py`
- `python scripts/check_docs_links.py`
- `python scripts/check_harness_prototypes.py`
- `python scripts/check_market_governance.py`
- `python scripts/validate_market_manifest.py`
- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-readme`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`

其中 `npm run build --prefix frontend` 当前默认走 `next build --webpack`，用来规避这台 Windows 环境下默认 Turbopack worker 的间歇性崩溃。

## 一句话定位

如果把这个项目压成一句话，它更接近：

“一套从 skill 设计逻辑出发，最终落到 skills market、client lifecycle、governance 和前后端交付的中文教学型参考实现。”
