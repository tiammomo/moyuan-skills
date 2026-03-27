# Market Client Operations

这篇文档专门讲本地 `skills market client` 怎么运转。

它解决的不是“如何打包 skill”，而是：

- 如何安装、更新、移除 skill
- 如何安装和维护 starter bundle
- 如何检查本地状态有没有漂移
- 如何用 baseline、history、waiver 和 gate 管理本地消费侧风险

## 先理解四组对象

1. `install spec`
   说明客户端该装什么。
2. `skills.lock.json`
   说明客户端现在已经装了什么。
3. `bundle report`
   说明这次 bundle install 或 update 的结果。
4. `snapshot / baseline / history`
   说明客户端状态如何被留档、对比、接受或拒绝。

## 推荐先跑的链路

### 单个 skill

```text
python scripts/skills_market.py install dist/market/install/release-note-writer-0.1.0.json --target-root dist/installed-skills
python scripts/skills_market.py list-installed --target-root dist/installed-skills
python scripts/skills_market.py update moyuan.release-note-writer --index dist/market/channels/stable.json --target-root dist/installed-skills --dry-run
python scripts/skills_market.py remove moyuan.release-note-writer --target-root dist/installed-skills
```

### starter bundle

```text
python scripts/skills_market.py list-bundles
python scripts/skills_market.py install-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
python scripts/skills_market.py list-installed-bundles --target-root dist/installed-bundles
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
```

### 状态体检与修复

```text
python scripts/skills_market.py doctor-installed --target-root dist/installed-skills --strict
python scripts/skills_market.py repair-installed --target-root dist/installed-skills --dry-run
python scripts/skills_market.py snapshot-installed --target-root dist/installed-skills --output-path dist/installed-skills/snapshots/latest.json --markdown-path dist/installed-skills/snapshots/latest.md
python scripts/skills_market.py verify-installed dist/installed-skills/snapshots/baseline.json --target-root dist/installed-skills --output-dir dist/installed-skills/verification --strict
```

## 为什么这一层很重要

- 如果没有 client lifecycle，market 只剩“能下载”
- 如果没有 lock、bundle report 和 baseline，consumer 侧状态不可维护
- 如果没有 doctor、repair、waiver 和 gate，安装后的长期运行不可治理

## 学完后下一步看什么

- 治理与交付：看 [21-market-governance-and-delivery.md](./21-market-governance-and-delivery.md)
- 更底层 consumer 说明：看 [../consumer-guide.md](../consumer-guide.md)
