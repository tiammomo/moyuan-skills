# Publisher Guide

这份文档面向 skill 作者和发布者，说明当前仓库里一份 skill 要怎样变成真正的 market-ready 分发包。

## 一份 skill 要具备什么

当前最低要求是：

- skill 本体已经存在
- `SKILL.md`、`references/`、`scripts/`、`assets/` 结构清楚
- 有可重复运行的 checker
- 有 `skills/<skill>/market/skill.json`

更完整的 market-ready 版本还要补上：

- eval 命令
- lifecycle 状态
- distribution.capabilities
- starter bundle 归属
- publisher profile
- package artifact
- provenance attestation
- install spec

## 推荐流程

### 1. 写好 manifest

位置：

```text
skills/<skill-name>/market/skill.json
```

当前要特别留意这些字段：

- `id`
- `channel`
- `quality.review_status`
- `lifecycle.status`
- `permissions`
- `distribution.capabilities`
- `distribution.starter_bundle_ids`

### 2. 补 publisher profile

位置：

```text
publishers/<publisher-id>.json
```

当前 verified publisher 还需要：

- `verification.issued_by`
- `verification.issued_at`
- `verification.policy_url`
- `verification.method`

参考：

- [../publishers/moyuan.json](../publishers/moyuan.json)

### 3. 本地校验

```text
python scripts/skills_market.py validate
python scripts/skills_market.py governance-check
```

### 4. 打包并生成 provenance

```text
python scripts/skills_market.py package release-note-writer
python scripts/skills_market.py package --all
python scripts/skills_market.py provenance-check dist/market/install/release-note-writer-0.1.0.json
```

这一步会生成：

- zip package
- provenance attestation
- install spec

### 5. 生成 public market 输出

```text
python scripts/skills_market.py index
python scripts/skills_market.py catalog
python scripts/skills_market.py recommend
python scripts/skills_market.py federation-feed
```

### 6. 生成 org/private market 输出

```text
python scripts/skills_market.py org-index governance/orgs/moyuan-internal.json
python scripts/skills_market.py catalog --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py recommend --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py federation-feed --org-policy governance/orgs/moyuan-internal.json
```

### 7. 跑发布前 smoke

```text
python scripts/skills_market.py smoke
```

## 发布者检查单

- 这个 skill 真的适合复用吗
- summary 是否让陌生用户也能看懂
- permissions 是否保守且准确
- lifecycle 状态是否选对
- checker / eval 是否真的能跑
- starter bundle 是否放对
- stable / beta / internal 是否选对

## 当前建议

对大多数新 skill，建议顺序仍然是：

1. 先进入 `internal` 或 `beta`
2. 跑过 package / provenance / smoke
3. 再进入 `stable`

## 相关文档

- [market-spec.md](./market-spec.md)
- [market-governance.md](./market-governance.md)
- [market-registry.md](./market-registry.md)
- [consumer-guide.md](./consumer-guide.md)
