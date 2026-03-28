# Moyuan Skills Market

这是一个面向 `skills market` 的中文教学型参考仓库，覆盖从 skill 设计、market 分发、client lifecycle、governance 到前后端联调的完整链路。

## 最新进展

这一轮把 installed-state governance 的 write execution 再往前推进了一步：

- skill / bundle 详情页里的 waiver / apply 面板已经支持 `prepare / stage / verify + write handoff`
- write handoff 现在会展示 `pending / ready / blocked / drifted / completed` 五种状态，并解释为什么当前还不能进入最终 CLI write
- 页面新增持久化 approval record，能把 target root、report、operator note 与 evidence snapshot 一起写入治理快照目录
- 页面新增 audit timeline 与 evidence pack，能展示 apply / execute / verify / target root 等交接证据，并区分当前记录与历史记录
- Playwright 已覆盖 `approval persisted -> audit trail visible -> restage invalidates old approval -> post-write evidence refreshed` 这条真实路径
- Windows 下 staged artifact 继续使用短名 + hash，降低超长路径导致 stage 失败的风险

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
- docs 详情页会把 repo 命令、顺序提示、前置条件、预期结果和产物提示一起展示
- Playwright 已覆盖首页、skills、bundles、docs 与详情页的端到端联调

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
