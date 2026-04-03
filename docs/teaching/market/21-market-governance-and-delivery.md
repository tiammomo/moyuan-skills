# Market Governance And Delivery

这篇文档把 `skills market` 的最后一层串起来：治理、交付和前后端消费。

## 这篇要回答的问题

- publisher、org policy、waiver 和 gate 为什么会进入 market
- source reconcile 为什么是治理链的必要部分
- registry 数据怎样进入 frontend / backend
- 为什么 Playwright 联调也属于 skills market 的完成条件

## 治理层重点资产

- [../market-governance.md](../../market/market-governance.md)
- `publishers/*.json`
- `governance/orgs/*.json`
- `governance/history-alert-policies/*.json`
- `governance/history-alert-waivers/*.json`
- `governance/source-reconcile-gate-policies/*.json`
- `governance/source-reconcile-gate-waivers/*.json`

## 交付层重点资产

- [../market-registry.md](../../market/market-registry.md)
- [../frontend-backend-integration.md](../../integration/frontend-backend-integration.md)
- [../../backend/app/main.py](../../../backend/app/main.py)
- [../../frontend/lib/data.ts](../../../frontend/lib/data.ts)
- [../../frontend/tests/e2e/full-stack.spec.ts](../../../frontend/tests/e2e/full-stack.spec.ts)

## 推荐命令链路

```text
python scripts/check_market_governance.py
python scripts/skills_market.py catalog
python scripts/skills_market.py registry
python scripts/check_python_market_backend.py
npm run build --prefix frontend
npm run e2e --prefix frontend
```

## 这一层真正的学习重点

- 治理不是附加说明，而是分发能力的一部分
- 交付不是“最后做个页面”，而是让 market 数据被真实消费
- backend 负责把 repo 里的 skills、bundles、docs 和 registry 组织成稳定 API
- frontend 负责把 market、docs、teaching 和 project 内容变成新人可直接使用的学习和操作界面

## 学完后应该能做什么

- 能解释 `publisher -> policy -> waiver -> gate -> source reconcile` 的治理链路
- 能解释 `repository data -> backend API -> frontend pages -> Playwright` 的交付链路
- 能把整个项目讲成一套完整的 `skills market` 课程，而不是只讲 skill 写法
