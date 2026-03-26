# Skills Market Registry

这份文档说明当前仓库里已经落地的 `skills market` 分发层，包括：

- provenance 证明链
- starter bundles
- recommendation 输出
- public / org federation feed
- hosted registry 静态输出

## 当前已经具备的能力

当前仓库已经不只是“能写 skill”，也不只是“能做一个本地 install demo”，而是已经具备了完整的本地 market 分发闭环：

1. `manifest`
   每个 skill 都有 `skills/<skill>/market/skill.json`
2. `package`
   每个 skill 可以被打成 zip 包
3. `provenance`
   每个包都会生成 attestation JSON
4. `install spec`
   每个包都会生成带 checksum 和 provenance 引用的安装描述
5. `index / catalog`
   public market 和 org/private market 都可以生成 index 与静态 catalog
6. `recommendations`
   market 会生成 starter bundle 和 skill-to-skill recommendations
7. `federation feed`
   market 会导出 metadata-only feed 给下游 aggregator / marketplace 消费
8. `hosted registry`
   仓库可以直接生成一份适合静态托管的 registry 输出目录

## 关键产物

### 1. Provenance

打包后会生成：

```text
dist/market/provenance/<skill-name>-<version>.json
```

它包含：

- package checksum
- manifest checksum
- source tree checksum
- builder 信息
- quality 信号
- lifecycle 状态
- source file checksums

当前命令：

```text
python scripts/skills_market.py package release-note-writer
python scripts/skills_market.py provenance-check dist/market/install/release-note-writer-0.1.0.json
```

### 2. Starter Bundles

当前 bundle 定义在：

```text
bundles/*.json
```

它们用于表达“相关能力组合”，而不是单个 skill。当前仓库内已经有：

- `release-engineering-starter`
- `incident-ops-starter`
- `skill-authoring-starter`

这些 bundle 会进入：

- recommendation 输出
- federation feed
- static catalog 首页
- org policy 的 `featured_bundles`

### 3. Recommendations

当前 recommendation 输出目录：

```text
dist/market/recommendations/
dist/market/orgs/<org-id>/recommendations/
```

推荐分数会综合这些信号：

- `search.related_skills`
- shared categories
- shared tags
- shared capabilities
- shared starter bundles
- channel 稳定性
- publisher verified 信号
- lifecycle 状态

命令：

```text
python scripts/skills_market.py recommend
python scripts/skills_market.py recommend --org-policy governance/orgs/moyuan-internal.json
```

### 4. Federation Feed

当前 federation feed 输出：

```text
dist/market/federation/public-feed.json
dist/market/orgs/<org-id>/federation/feed.json
```

它是给 downstream marketplace / aggregator 用的 metadata-only feed，包含：

- skill metadata
- trust 信号
- lifecycle 状态
- install spec 路径
- provenance 路径
- starter bundle 摘要

命令：

```text
python scripts/skills_market.py federation-feed
python scripts/skills_market.py federation-feed --org-policy governance/orgs/moyuan-internal.json
```

### 5. Hosted Registry

当前 hosted registry 可以直接生成：

```text
python scripts/skills_market.py registry
```

默认输出：

```text
dist/market-registry/
```

它会包含：

- public market packages / install specs / provenance
- public index / catalog / recommendations / federation feed
- org-scoped index / catalog / recommendations / federation feed
- 顶层 `registry.json`

`registry.json` 负责把 public 和 org 输出组织成一个可托管、可被程序消费的目录。

## 目录结构

一次完整 registry build 之后，结构大致是：

```text
dist/market-registry/
|- registry.json
|- index.json
|- channels/
|- packages/
|- install/
|- provenance/
|- recommendations/
|- federation/
|- site/
`- orgs/
   `- moyuan-internal/
      |- index.json
      |- channels/
      |- policy.json
      |- recommendations/
      |- federation/
      `- site/
```

## 当前治理语义

分发层当前已经接入了这些治理信号：

- publisher verified
- trust level
- review status
- lifecycle status
- org allowlist
- blocked skills
- featured bundles
- provenance verification

安装侧的当前行为是：

- `active`: 正常安装
- `deprecated`: 警告后允许安装
- `blocked`: 拒绝安装
- `archived`: 拒绝安装

## 当前推荐命令

如果你想从零跑一遍完整 market 分发链，建议顺序是：

```text
python scripts/skills_market.py validate
python scripts/skills_market.py governance-check
python scripts/skills_market.py package --all
python scripts/skills_market.py index
python scripts/skills_market.py catalog
python scripts/skills_market.py recommend
python scripts/skills_market.py federation-feed
python scripts/skills_market.py registry
python scripts/skills_market.py smoke
```

## Local Client State

除了 public / org registry 产物以外，当前仓库也已经补齐了本地 market client 的安装态管理。安装侧会额外产出：

```text
dist/installed-skills/
`- skills.lock.json
```

对应命令是：

```text
python scripts/skills_market.py install dist/market/install/release-note-writer-0.1.0.json --target-root dist/installed-skills
python scripts/skills_market.py list-installed --target-root dist/installed-skills
python scripts/skills_market.py update moyuan.release-note-writer --index dist/market/channels/stable.json --target-root dist/installed-skills --dry-run
python scripts/skills_market.py remove moyuan.release-note-writer --target-root dist/installed-skills
```

也就是说，当前的 registry 不只是“能被搜索和分发”，还已经能支撑最小的 client lifecycle：install, inspect, resolve update, remove。

## Starter Bundle Consumption

当前的 bundle 已经不只是 recommendation 输出里的静态对象，也可以直接作为本地 client 的消费入口：

```text
python scripts/skills_market.py list-bundles
python scripts/skills_market.py install-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
python scripts/skills_market.py install-bundle skill-authoring-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
```

这里有两个重要语义：

- bundle 安装可以跨 channel 解析 install spec，而不要求整组 skill 都来自同一个 channel
- lifecycle 治理会继续生效，所以 archived / blocked skill 会被跳过并写进 bundle report

这让 registry 层真正向下连到了 bundle 级客户端消费，而不只是“有 bundles.json 可以看”。

## Bundle State Management

当前 bundle 客户端链路已经继续补到了“安装后状态管理”：

```text
python scripts/skills_market.py list-installed-bundles --target-root dist/installed-bundles
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles
```

底层语义是：

- `skills.lock.json` 会记录每个 skill 的 ownership sources
- bundle report 负责记录某次 bundle install 的结果
- `remove-bundle` 会按 ownership sources 做保守回收，只删除 bundle-only skill

这意味着 registry / bundle / client state 已经形成了更完整的本地闭环。

## Bundle Reconciliation

当前本地 market client 还继续补上了 bundle update / reconcile：

```text
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
```

这一步的意义是把 registry 侧的“bundle 最新定义”真正传递到消费侧：

- 新的 bundle member 会被安装或刷新
- 旧的 bundle member 会被识别并移出当前 bundle ownership
- lifecycle 变化也会在 reconcile 里继续生效

这样 bundle 就不只是“一次性安装入口”，而是具备了持续演进能力。

## Installed-State Audit

当前本地 market client 还补上了 install-state doctor：

```text
python scripts/skills_market.py doctor-installed --target-root dist/installed-skills
python scripts/skills_market.py doctor-installed --target-root dist/installed-skills --strict
python scripts/skills_market.py repair-installed --target-root dist/installed-skills --dry-run
python scripts/skills_market.py repair-installed --target-root dist/installed-skills
python scripts/skills_market.py snapshot-installed --target-root dist/installed-skills --output-path dist/installed-skills/snapshots/latest.json --markdown-path dist/installed-skills/snapshots/latest.md
python scripts/skills_market.py diff-installed dist/installed-skills/snapshots/before.json dist/installed-skills/snapshots/after.json --output-path dist/installed-skills/snapshots/diff.json --markdown-path dist/installed-skills/snapshots/diff.md
python scripts/skills_market.py verify-installed dist/installed-skills/snapshots/baseline.json --target-root dist/installed-skills --output-dir dist/installed-skills/verification --strict
python scripts/skills_market.py verify-installed-history dist/installed-skills/snapshots/baseline-history.json latest --target-root dist/installed-skills --output-dir dist/installed-skills/verification-history --strict
python scripts/skills_market.py diff-installed-history dist/installed-skills/snapshots/baseline-history.json 1 latest --output-path dist/installed-skills/snapshots/history-diff.json --markdown-path dist/installed-skills/snapshots/history-diff.md
python scripts/skills_market.py promote-installed-baseline dist/installed-skills/snapshots/baseline.json --target-root dist/installed-skills --markdown-path dist/installed-skills/snapshots/baseline.md --diff-output-path dist/installed-skills/snapshots/baseline-transition.json --diff-markdown-path dist/installed-skills/snapshots/baseline-transition.md --history-path dist/installed-skills/snapshots/baseline-history.json --history-markdown-path dist/installed-skills/snapshots/baseline-history.md --archive-dir dist/installed-skills/snapshots/baseline-archive
python scripts/skills_market.py list-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json
python scripts/skills_market.py report-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --output-path dist/installed-skills/snapshots/history-report.json --markdown-path dist/installed-skills/snapshots/history-report.md
python scripts/skills_market.py list-installed-history-policies
python scripts/skills_market.py list-installed-history-waivers
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --strict
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --waiver approved-release-engineering-downsize --strict
python scripts/skills_market.py restore-installed-baseline dist/installed-skills/snapshots/baseline-history.json latest --baseline-path dist/installed-skills/snapshots/baseline.json --markdown-path dist/installed-skills/snapshots/baseline.md
python scripts/skills_market.py prune-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --keep-last 5
```

这一步的意义是让消费侧也具备最小治理能力：

- lock / report / filesystem 漂移可以被直接发现
- bundle ownership 断裂不会悄悄积累
- registry 侧的 install spec / provenance 失效也能在本地暴露出来
- orphan 安装目录和失效 bundle report 可以先由消费端保守修复
- 修复前后的 installed-state 也可以被导出成 snapshot，变成可归档的 client-side 运维记录
- 前后两个 installed-state snapshot 也可以被对比成 diff，变成可 review 的 client-side 变更报告
- 当前 live state 也可以直接拿 baseline snapshot 做校验，变成可自动失败的 client-side drift gate
- 历史归档下来的 baseline 也可以直接做只读 verify，适合 client-side 复盘和历史对照
- 两个历史归档基线也可以直接彼此做 diff，适合 client-side 基线演进审计
- retained history 也可以直接导出 timeline/report，适合 client-side 的值班交接、review 和审计归档
- retained history transition 也可以直接做 alert/gate，适合 client-side 的大变更筛查和运维门禁
- 这些 alert/gate 现在还可以复用 `governance/history-alert-policies/` 里的 policy profile，而不是每次都重复写 threshold 参数
- 已审批的大变更也可以复用 `governance/history-alert-waivers/` 里的 waiver record，而不是让本地 gate 永远被同一类例外阻塞
- 当 drift 被接受之后，baseline 也可以被刷新，同时保留 transition diff 作为 client-side baseline history
- baseline promotion 本身也会留下独立 history 和 archive，变成可查询、可恢复的 client-side baseline audit trail
- 当历史积累起来之后，client 侧也可以主动 prune 旧 history 和 archive，保留可维护的 retention 边界

这样“可安装”就进一步推进到了“可巡检、可维护”。

## 相关文件

- [market-spec.md](./market-spec.md)
- [market-governance.md](./market-governance.md)
- [publisher-guide.md](./publisher-guide.md)
- [consumer-guide.md](./consumer-guide.md)
- [../schemas/skill-provenance.schema.json](../schemas/skill-provenance.schema.json)
- [../schemas/skill-bundle.schema.json](../schemas/skill-bundle.schema.json)
- [../scripts/build_market_recommendations.py](../scripts/build_market_recommendations.py)
- [../scripts/build_federation_feed.py](../scripts/build_federation_feed.py)
- [../scripts/build_market_registry.py](../scripts/build_market_registry.py)
- [../scripts/verify_market_provenance.py](../scripts/verify_market_provenance.py)
- [../scripts/list_installed_skills.py](../scripts/list_installed_skills.py)
- [../scripts/update_installed_skill.py](../scripts/update_installed_skill.py)
- [../scripts/remove_skill.py](../scripts/remove_skill.py)
- [../scripts/list_installed_baseline_history_waivers.py](../scripts/list_installed_baseline_history_waivers.py)
- [../scripts/list_skill_bundles.py](../scripts/list_skill_bundles.py)
- [../scripts/install_skill_bundle.py](../scripts/install_skill_bundle.py)
- [../scripts/list_installed_bundles.py](../scripts/list_installed_bundles.py)
- [../scripts/remove_skill_bundle.py](../scripts/remove_skill_bundle.py)
- [../scripts/update_skill_bundle.py](../scripts/update_skill_bundle.py)
- [../scripts/check_installed_market_state.py](../scripts/check_installed_market_state.py)
