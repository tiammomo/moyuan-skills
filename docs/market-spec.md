# Skills Market 规范

这份文档定义当前仓库里已经落地的 `skills market` 结构，不再是“预留草案”，而是和脚本、schema、smoke pipeline 对齐的运行规范。

## 核心对象

当前 market 由 5 类核心对象组成：

1. `skill market manifest`
2. `install spec`
3. `channel index`
4. `provenance attestation`
5. `starter bundle`

另外还有 2 类治理对象：

1. `publisher profile`
2. `org market policy`

## 1. Skill Market Manifest

位置：

```text
skills/<skill-name>/market/skill.json
```

当前必须表达这些信息：

- `id`
- `publisher`
- `name`
- `title`
- `version`
- `channel`
- `summary`
- `description`
- `categories`
- `tags`
- `compatibility`
- `permissions`
- `quality`
- `lifecycle`
- `artifacts`
- `search`
- `distribution`

其中几个关键段的语义是：

- `quality`
  checker / eval / review_status
- `lifecycle`
  `active` / `deprecated` / `blocked` / `archived`
- `search`
  keywords / related_skills
- `distribution`
  capabilities / starter_bundle_ids

## 2. Install Spec

位置：

```text
dist/market/install/<skill-name>-<version>.json
```

install spec 由打包脚本生成，不建议手写。它描述：

- 要安装哪个 skill
- 包文件在哪里
- 包 checksum 是什么
- 安装入口是什么
- publisher / review / lifecycle 状态是什么
- provenance 在哪里

当前关键字段包括：

- `skill_id`
- `skill_name`
- `publisher`
- `version`
- `channel`
- `package_path`
- `checksum_sha256`
- `entrypoint`
- `install_target`
- `review_status`
- `lifecycle_status`
- `provenance_path`
- `provenance_sha256`

## 3. Channel Index

位置：

```text
dist/market/index.json
dist/market/channels/stable.json
dist/market/channels/beta.json
dist/market/channels/internal.json
```

channel index 是 market 消费入口。当前每个 skill 摘要会暴露：

- 标题、版本、summary
- categories、tags、capabilities
- install spec 路径
- provenance 路径
- review_status
- lifecycle_status
- replacement_skill_id

## 4. Provenance Attestation

位置：

```text
dist/market/provenance/<skill-name>-<version>.json
```

provenance 用来证明：

- 这个包是谁打出来的
- 对应哪一份 manifest
- 对应哪一份 source tree
- package checksum 是什么
- 当前 review / lifecycle 信号是什么
- source file checksums 是什么

安装链会验证：

- install spec 中的 provenance checksum
- provenance 中的 package checksum
- provenance 和 install spec 的字段一致性

## 5. Starter Bundle

位置：

```text
bundles/*.json
```

bundle 表达“相关能力组合”，不是单个 skill。当前它用于：

- catalog 首页展示
- recommendation 打分
- org policy 的 `featured_bundles`
- federation feed 输出

## 6. Channel 模型

当前保留 3 类 channel：

- `stable`
- `beta`
- `internal`

这三类已经足够覆盖：

- 默认公开推荐能力
- 灰度能力
- 组织内能力

## 7. 权限模型

manifest 当前显式暴露：

- `workspace`
  `none` / `read` / `write`
- `network`
  `none` / `limited` / `full`
- `shell`
  `none` / `limited` / `full`
- `secrets`
  `none` / `read` / `write`
- `human_review_required`

## 8. 质量信号

当前 market 已接入：

- `checker`
- `eval`
- `review_status`
- `checksum_sha256`
- `provenance`
- `publisher_verified`
- `trust_level`

## 9. 搜索与推荐信号

当前 recommendation 和 search 会使用这些结构化信号：

- `categories`
- `tags`
- `search.keywords`
- `search.related_skills`
- `distribution.capabilities`
- `distribution.starter_bundle_ids`

## 10. Federation 与 Hosted Registry

当前仓库已经支持两类下游输出：

- metadata-only federation feed
- hosted-friendly public/private registry 输出

对应脚本：

- [build_federation_feed.py](../scripts/build_federation_feed.py)
- [build_market_registry.py](../scripts/build_market_registry.py)

## 11. 当前仓库结构映射

- `skills/`
  skill source
- `schemas/`
  market schema
- `bundles/`
  starter bundles
- `publishers/`
  publisher profiles
- `governance/`
  org market policies
- `scripts/`
  validate / package / provenance / search / install / index / federation / registry

## 12. 对应文件

- [../schemas/skill-market-manifest.schema.json](../schemas/skill-market-manifest.schema.json)
- [../schemas/skill-install.schema.json](../schemas/skill-install.schema.json)
- [../schemas/skill-channel.schema.json](../schemas/skill-channel.schema.json)
- [../schemas/skill-provenance.schema.json](../schemas/skill-provenance.schema.json)
- [../schemas/skill-bundle.schema.json](../schemas/skill-bundle.schema.json)
- [../schemas/publisher-profile.schema.json](../schemas/publisher-profile.schema.json)
- [../schemas/org-market-policy.schema.json](../schemas/org-market-policy.schema.json)
- [market-governance.md](./market-governance.md)
- [market-registry.md](./market-registry.md)
- [../scripts/validate_market_manifest.py](../scripts/validate_market_manifest.py)
- [../scripts/check_market_governance.py](../scripts/check_market_governance.py)
- [../scripts/package_skill.py](../scripts/package_skill.py)
- [../scripts/verify_market_provenance.py](../scripts/verify_market_provenance.py)
- [../scripts/build_market_index.py](../scripts/build_market_index.py)
- [../scripts/build_org_market_index.py](../scripts/build_org_market_index.py)
- [../scripts/build_market_catalog.py](../scripts/build_market_catalog.py)
- [../scripts/build_market_recommendations.py](../scripts/build_market_recommendations.py)
- [../scripts/build_federation_feed.py](../scripts/build_federation_feed.py)
- [../scripts/build_market_registry.py](../scripts/build_market_registry.py)
- [../scripts/search_skills.py](../scripts/search_skills.py)
- [../scripts/install_skill.py](../scripts/install_skill.py)
- [../scripts/skills_market.py](../scripts/skills_market.py)
