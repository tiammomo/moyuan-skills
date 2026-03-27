# Skills Market Learning Map

这篇文档把整个 `moyuan-skills` 当成一个 `skills market` 项目来重新看一遍。

目标不是再解释“什么是一个 skill”，而是解释：

- skill 为什么会继续演进成可发布的 market artifact
- market 为什么不只是一个 catalog 页面
- 为什么 client、governance、frontend/backend 也属于 skills market 的学习范围

## 先把项目拆成五层

1. `skill design`
   对应 `build-skills`、`progressive-disclosure`、`harness-engineering`。
2. `package pipeline`
   对应 manifest、install spec、package、provenance、channel index。
3. `client lifecycle`
   对应 install、bundle、doctor、snapshot、baseline history。
4. `governance`
   对应 publisher、org policy、waiver、gate、source reconcile。
5. `product delivery`
   对应 backend API、frontend docs center、Playwright 全链路验证。

## 每一层在仓库里对应什么

- `skills/`
  真实 skill 与业务案例。
- `scripts/`
  package、registry、client、governance 和 smoke 脚本。
- `schemas/`
  skills market 的结构约束。
- `bundles/`
  starter bundle 资产。
- `publishers/` 与 `governance/`
  publisher、org policy、policy profile、waiver 资产。
- `backend/` 与 `frontend/`
  产品化交付层。

## 推荐学习顺序

1. [16-skills-market-evolution.md](./16-skills-market-evolution.md)
2. [17-market-registry-and-federation.md](./17-market-registry-and-federation.md)
3. [19-market-packaging-and-publishing.md](./19-market-packaging-and-publishing.md)
4. [20-market-client-operations.md](./20-market-client-operations.md)
5. [21-market-governance-and-delivery.md](./21-market-governance-and-delivery.md)

## 读这篇时建议同时看哪些项目文档

- [../market-spec.md](../market-spec.md)
- [../market-registry.md](../market-registry.md)
- [../market-governance.md](../market-governance.md)
- [../frontend-backend-integration.md](../frontend-backend-integration.md)

## 最小确认命令

```text
python scripts/skills_market.py smoke
python scripts/check_market_governance.py
python scripts/check_python_market_backend.py
npm run e2e --prefix frontend
```

## 学完后应该能回答

- 这个仓库为什么已经不是单纯的 skills 目录
- skills market 的最小闭环为什么至少要包含 package、client、governance 和 delivery
- 为什么 `docs/teaching/` 必须承担整套 skills market 的教学入口
