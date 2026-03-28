# Moyuan Skills Market

这是一个面向 `skills market` 的教学型参考仓库。

仓库同时覆盖 6 层能力：

1. skill 设计、渐进式披露与 harness/eval
2. market manifest、package、provenance 与发布分发
3. client install / update / remove / bundle lifecycle
4. installed-state doctor / repair / baseline / governance
5. waiver / policy / gate / source reconcile 治理链路
6. frontend / backend / HTML 交付与前后端联调

## 最新进展

这轮把 installed-state governance 的 write-approval 再往前推进了一步：

- skill / bundle 详情页里的 waiver / apply 面板现在支持 `prepare / stage / verify + write handoff`
- 页面会区分 `pending / ready / blocked / drifted / completed` 五种 write 资格，并解释为什么当前还不能进入 CLI write
- handoff 区块会直接展示 CLI `write` / `verify` 命令、planned governance source、review artifacts、approval checklist 和 rollback hint
- repo governance source 的真实 `write` 仍然保持 CLI-only；页面负责把高风险动作解释清楚并交接出去
- Playwright 已覆盖 `stage verified -> write handoff ready` 以及 `tamper staged artifact -> drifted / handoff disabled` 两条真实路径
- Windows 下 staged artifact 继续使用短名 + hash，避免超长路径导致 stage 失败

另外，前端构建当前默认仍走 `next build --webpack`，并在 [frontend/next.config.js](./frontend/next.config.js) 中把 `experimental.cpus` 收敛到更保守的值，用来降低 Windows 下 page-data 阶段偶发 `spawn UNKNOWN` 的风险。

## 当前能力

### 1. Skills 教学与案例

- skill 设计与教学见 [docs/skill-learning-guide.md](./docs/skill-learning-guide.md)
- 快速上手见 [docs/skill-quickstart.md](./docs/skill-quickstart.md)
- 渐进式披露与 harness 参考见 [docs/progressive-disclosure.md](./docs/progressive-disclosure.md) 与 [docs/harness-engineering.md](./docs/harness-engineering.md)
- 新增的中文业务案例见 [docs/feishu-doc-sync.md](./docs/feishu-doc-sync.md) 与 [docs/yuque-openapi.md](./docs/yuque-openapi.md)

### 2. Skills Market 与分发

- package / index / catalog / recommendations / federation / registry 都已经具备本地脚本入口
- 统一 CLI 入口见 [scripts/skills_market.py](./scripts/skills_market.py)
- 规范与发布说明见 [docs/market-spec.md](./docs/market-spec.md)、[docs/publisher-guide.md](./docs/publisher-guide.md)、[docs/consumer-guide.md](./docs/consumer-guide.md)
- registry / federation 说明见 [docs/market-registry.md](./docs/market-registry.md)

### 3. Client Lifecycle 与治理

- install / update / remove / bundle / doctor / repair / baseline / governance / waiver / apply handoff / gate 已全部落地
- installed-state 现在已经能从页面跑通 doctor、低风险 repair、baseline capture、governance refresh
- waiver / apply 现在已经能从页面跑通 `prepare / stage / verify`，并页面化展示 write handoff
- 治理说明见 [docs/market-governance.md](./docs/market-governance.md)

### 4. 前后端联调

- Python backend 见 [backend/README.md](./backend/README.md)
- 前后端契约与页面映射见 [docs/frontend-backend-integration.md](./docs/frontend-backend-integration.md)
- skill / bundle 详情页已经支持真实 backend 本地执行与远端 registry install
- docs 详情页会把 repo 命令、顺序提示、前置条件、预期结果和产物输出提示一起展示出来
- Playwright 已覆盖首页、skills、bundles、docs 与详情页的端到端联调

## 中文 Skills 教学入口

推荐按下面的顺序学习：

1. [docs/teaching/README.md](./docs/teaching/README.md)
2. [docs/teaching/14-first-hour-onboarding.md](./docs/teaching/14-first-hour-onboarding.md)
3. [docs/skill-learning-guide.md](./docs/skill-learning-guide.md)
4. [docs/teaching/18-skills-market-learning-map.md](./docs/teaching/18-skills-market-learning-map.md)
5. [docs/teaching/22-doc-sync-skill-case-studies.md](./docs/teaching/22-doc-sync-skill-case-studies.md)

如果你更关心真实案例，可以直接看：

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
- 交互与远端安装路线图：[docs/interaction-and-remote-install-roadmap.md](./docs/interaction-and-remote-install-roadmap.md)

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

## 常用校验命令

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
