# Publisher Guide

这份文档面向 skill 作者和发布者，说明当前仓库里一份 skill 要怎样变成真正的 market-ready 分发包。

如果你现在还在写 skill 本体，先看 [skill-authoring.md](../authoring/skill-authoring.md)。这里默认你已经完成作者链前半段，准备把 skill 推进到真正可分发状态。

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

### 1. 先跑作者链前半段

在进入发布视角前，先把下面这条链跑通：

```text
python scripts/skills_market.py doctor-skill skills/<skill-name> --run-checker
python scripts/skills_market.py validate skills/<skill-name>/market/skill.json
python scripts/skills_market.py package skills/<skill-name>
python scripts/skills_market.py provenance-check dist/market/install/<skill-name>-<version>.json
```

如果你只是先把 skill scaffold 在仓库内其他目录做预演，也可以先按路径打包：

```text
python scripts/skills_market.py package dist/authoring-smoke/<skill-name>
```

通过这一步，作者和发布者会先确认：

- checker 真的能跑
- manifest 真的能过 schema
- package artifact 能真的生成
- install spec 和 provenance 已经成形

### 2. 写好 manifest

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

### 3. 补 publisher profile

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

- [../publishers/moyuan.json](../../publishers/moyuan.json)

### 4. 做发布前校验

```text
python scripts/skills_market.py validate
python scripts/skills_market.py governance-check
```

### 5. 重新打包并生成 provenance

如果 manifest、publisher profile 或 lifecycle 状态改过，不要复用旧产物，重新跑一遍：

```text
python scripts/skills_market.py package release-note-writer
python scripts/skills_market.py package --all
python scripts/skills_market.py provenance-check dist/market/install/release-note-writer-0.1.0.json
```

这一步会生成：

- zip package
- provenance attestation
- install spec

### 6. 构建并校验 submission

当前最小 submission 闭环已经可用：

```text
python scripts/skills_market.py build-submission release-note-writer
python scripts/skills_market.py validate-submission dist/submissions/moyuan/release-note-writer/0.1.0/submission.json
python scripts/skills_market.py upload-submission dist/submissions/moyuan/release-note-writer/0.1.0/submission.json --inbox-dir incoming/submissions
```

如果你是从仓库里的其他目录预演 skill，也可以直接按路径构建：

```text
python scripts/skills_market.py build-submission dist/authoring-smoke/release-note-writer
```

这一步会生成：

- `dist/submissions/<publisher>/<skill>/<version>/submission.json`
- `dist/submissions/<publisher>/<skill>/<version>/payload.tgz`

上传后会再得到一个 self-contained inbox 副本：

- `incoming/submissions/<publisher>/<skill>/<version>/submission.json`
- `incoming/submissions/<publisher>/<skill>/<version>/payload.tgz`
- `incoming/submissions/<publisher>/<skill>/<version>/source/`
- `incoming/submissions/<publisher>/<skill>/<version>/artifacts/packages/`
- `incoming/submissions/<publisher>/<skill>/<version>/artifacts/install/`
- `incoming/submissions/<publisher>/<skill>/<version>/artifacts/provenance/`

当前建议把它当成发布前的标准交接物，而不是继续只依赖手工 `package / registry`。

### 7. 上传到 maintainer inbox

当前 repo-compatible 上传闭环已经可用：

```text
python scripts/skills_market.py upload-submission dist/submissions/moyuan/release-note-writer/0.1.0/submission.json --inbox-dir incoming/submissions
```

这一步会把交接物复制到：

- `incoming/submissions/<publisher>/<skill>/<version>/submission.json`
- `incoming/submissions/<publisher>/<skill>/<version>/payload.tgz`
- `incoming/submissions/<publisher>/<skill>/<version>/source/`
- `incoming/submissions/<publisher>/<skill>/<version>/artifacts/packages/`
- `incoming/submissions/<publisher>/<skill>/<version>/artifacts/install/`
- `incoming/submissions/<publisher>/<skill>/<version>/artifacts/provenance/`

### 8. maintainer review 并 ingest

maintainer 侧当前最小闭环是：

```text
python scripts/skills_market.py review-submission incoming/submissions/moyuan/release-note-writer/0.1.0/submission.json --review-status approved --reviewer "Market Maintainer" --summary "Submission passed inbox review." --run-checker
python scripts/skills_market.py ingest-submission incoming/submissions/moyuan/release-note-writer/0.1.0/submission.json
python scripts/skills_market.py registry
```

这一步会：

- 产出 `review.json`
- 产出 `ingest.json`
- 把 approved submission 写回 canonical `skills/` 和 `docs/`
- 让后续 registry rebuild 能包含新 skill

如果你 ingest 的是已经在 repo 里占了同名位置的 skill，可以显式用：

```text
python scripts/skills_market.py ingest-submission incoming/submissions/moyuan/release-note-writer/0.1.0/submission.json --force
```

如果你只想先预演 ingest，但不想碰仓库主 `skills/` 树，也可以改用 repo 内 staging 目录：

```text
python scripts/skills_market.py ingest-submission incoming/submissions/moyuan/release-note-writer/0.1.0/submission.json --skills-dir dist/ingested/skills --docs-dir dist/ingested/docs
```

如果你已经按 [frontend-backend-integration.md](../integration/frontend-backend-integration.md) 启好了 backend 和 frontend，同一套 submission 流程现在也能直接从页面触发：

- `/studio/new`
  对应 `build-submission`
- `/studio/submissions`
  对应 `upload / review / ingest`

需要特别注意的是，页面默认会把 ingest 指向 `dist/backend-author-ingested/*` staging 目录；CLI 默认仍然写回 canonical `skills/` 和 `docs/`。

### 9. 生成 public market 输出

```text
python scripts/skills_market.py index
python scripts/skills_market.py catalog
python scripts/skills_market.py recommend
python scripts/skills_market.py federation-feed
```

### 10. 生成 org/private market 输出

```text
python scripts/skills_market.py org-index governance/orgs/moyuan-internal.json
python scripts/skills_market.py catalog --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py recommend --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py federation-feed --org-policy governance/orgs/moyuan-internal.json
```

### 11. 跑发布前 smoke

```text
python scripts/skills_market.py smoke
```

## 发布者检查单

- 作者链里的 `doctor / validate / package / provenance-check` 是否都跑过？
- `build-submission / validate-submission` 是否都跑过？
- `upload-submission / review-submission / ingest-submission` 是否都跑过？
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
2. 跑过作者链里的 `doctor / validate / package / provenance-check`
3. 再跑 `build-submission / validate-submission`
4. 再跑 `upload-submission / review-submission / ingest-submission`
5. 再跑 market build / smoke
6. 再进入 `stable`

## 相关文档

- [market-spec.md](./market-spec.md)
- [market-governance.md](./market-governance.md)
- [market-registry.md](./market-registry.md)
- [consumer-guide.md](./consumer-guide.md)
