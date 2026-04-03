# Template Packs

`templates/` 是这个仓库的模板资产区。

它和 `skills/` 的区别是：

- `skills/` 是可触发、可执行、可检查的真实能力包
- `templates/` 是帮助作者起步或扩展的半成品骨架

## Packs

- `skills/beginner-skill/`
- `skills/advanced-skill/`
- `skills/market-ready-skill/`
- `harness/harness-ready/`

## 使用原则

- 从最小模板起步，不要一上来复制最重的骨架
- 复制后优先删除不需要的部分
- 如果模板已经稳定复用，再把经验沉淀回 `docs/` 或 `skills/`
- `harness-ready/` 现在除了 tool contract / safety / automation，也包含 runtime blueprint 模板
- `python scripts/skills_market.py scaffold-skill <name> --template market-ready` 会直接使用仓库内的 market-ready 模板包
- `market-ready` 模板默认服务这条作者链：
  `scaffold -> doctor-skill -> validate -> package -> provenance-check`
