# Skills Market Governance

这份文档专门讲当前仓库里已经落地的 `skills market` 治理层。

## 当前治理对象

仓库现在有 4 类治理资产：

1. `publisher profile`
   位置：`publishers/*.json`
2. `org market policy`
   位置：`governance/orgs/*.json`
3. `installed history alert policy`
   位置：`governance/history-alert-policies/*.json`
4. `governance checker`
   位置：`scripts/check_market_governance.py`

## Publisher Profile

publisher profile 当前回答这些问题：

- 发布者是谁
- 是否 verified
- trust level 是什么
- 联系方式是什么
- 有哪些 namespace
- verified 是由谁签发的

当前参考：

- [../publishers/moyuan.json](../publishers/moyuan.json)
- [../schemas/publisher-profile.schema.json](../schemas/publisher-profile.schema.json)

verified publisher 现在会显式带：

- `issued_by`
- `issued_at`
- `policy_url`
- `method`

## Org Market Policy

org policy 当前回答这些问题：

- 哪些 channel 可以进入这个 org market
- 哪些 publisher 被允许进入
- 哪些 review_status 被允许进入
- 哪些 lifecycle_status 被允许进入
- 哪些 skill 要显式 block
- 哪些 bundle 要作为 featured bundles 展示
- 是否要求 verified publisher

当前参考：

- [../governance/orgs/moyuan-internal.json](../governance/orgs/moyuan-internal.json)
- [../schemas/org-market-policy.schema.json](../schemas/org-market-policy.schema.json)

## Installed History Alert Policy

installed history alert policy 当前回答这些问题：

- installed baseline history 应该用哪一组阈值做 alert/gate
- 默认只看 latest transition，还是检查 retained history 全部 transition
- 团队想复用的 gate 名称、标题和说明是什么

当前参考：

- [../governance/history-alert-policies/latest-release-gate.json](../governance/history-alert-policies/latest-release-gate.json)
- [../governance/history-alert-policies/history-audit.json](../governance/history-alert-policies/history-audit.json)
- [../schemas/installed-history-alert-policy.schema.json](../schemas/installed-history-alert-policy.schema.json)

这类 policy 会被 `scripts/check_market_governance.py` 一起校验，也会进入本地 client 的 installed baseline history alert 工作流。

## 当前治理信号已经进入哪里

这些治理信号现在已经进入：

- public / org channel index
- static catalog
- install spec
- provenance attestation
- federation feed
- hosted registry output

也就是说，用户现在已经可以看到：

- skill 来自哪个 publisher
- publisher 是否 verified
- skill 当前 review_status 是什么
- skill 当前 lifecycle_status 是什么
- skill 是否能进入某个 org market

## 当前安装侧语义

安装链路当前对 lifecycle 的行为是：

- `active`
  正常安装
- `deprecated`
  给出 warning，但允许安装
- `blocked`
  拒绝安装
- `archived`
  拒绝安装

## 当前命令

### 1. 校验治理配置

```text
python scripts/check_market_governance.py
python scripts/skills_market.py governance-check
```

### 2. 生成 org/private index

```text
python scripts/build_org_market_index.py governance/orgs/moyuan-internal.json
python scripts/skills_market.py org-index governance/orgs/moyuan-internal.json
```

### 3. 生成 org/private catalog

```text
python scripts/build_market_catalog.py --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py catalog --org-policy governance/orgs/moyuan-internal.json
```

### 4. 生成 org/private recommendation 与 feed

```text
python scripts/skills_market.py recommend --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py federation-feed --org-policy governance/orgs/moyuan-internal.json
```

### 5. 复用 installed history alert policy

```text
python scripts/skills_market.py list-installed-history-policies
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --strict
```

## 相关文件

- [market-spec.md](./market-spec.md)
- [market-registry.md](./market-registry.md)
- [../scripts/check_market_governance.py](../scripts/check_market_governance.py)
- [../scripts/build_org_market_index.py](../scripts/build_org_market_index.py)
- [../scripts/build_market_catalog.py](../scripts/build_market_catalog.py)
- [../scripts/build_market_recommendations.py](../scripts/build_market_recommendations.py)
- [../scripts/build_federation_feed.py](../scripts/build_federation_feed.py)
- [../scripts/list_installed_baseline_history_policies.py](../scripts/list_installed_baseline_history_policies.py)
