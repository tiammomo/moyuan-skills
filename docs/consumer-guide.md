# Consumer Guide

这份文档面向使用者，说明当前仓库里怎样搜索、判断、安装和消费一个 `skills market` 里的 skill。

## 先看什么

作为使用者，你最关心的不应该只是“有没有这个 skill”，而应该是：

- 它适不适合你的任务
- 它能不能在你的环境里跑
- 它风险大不大
- 它值不值得信任
- 装了它以后，还该不该顺手装别的相关能力

## 怎么找 skill

当前本地 market 支持这些入口：

```text
python scripts/skills_market.py search --query release
python scripts/skills_market.py search --category release-engineering
python scripts/skills_market.py search --channel stable --query release
python scripts/skills_market.py catalog
python scripts/skills_market.py recommend
```

当前搜索会利用：

- 名称
- summary
- tags
- keywords
- capabilities
- starter bundle ids
- lifecycle 状态

## 怎么看 org/private market

如果你使用的是团队或组织内 market，可以看：

```text
python scripts/skills_market.py org-index governance/orgs/moyuan-internal.json
python scripts/skills_market.py catalog --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py recommend --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py federation-feed --org-policy governance/orgs/moyuan-internal.json
```

## 怎么判断一个 skill 值不值得装

当前至少看这 7 件事：

1. `summary`
2. `channel`
3. `permissions`
4. `review_status`
5. `lifecycle_status`
6. `publisher / verified / trust_level`
7. `starter bundles / related recommendations`

## 怎么安装

当前安装模型是：

1. 先有 package
2. 再有 install spec
3. 再在安装时校验 checksum 和 provenance

示例：

```text
python scripts/skills_market.py package release-note-writer
python scripts/skills_market.py provenance-check dist/market/install/release-note-writer-0.1.0.json
python scripts/skills_market.py install dist/market/install/release-note-writer-0.1.0.json --dry-run
```

真正安装后，当前本地 client 还支持继续做这几件事：

```text
python scripts/skills_market.py install dist/market/install/release-note-writer-0.1.0.json --target-root dist/installed-skills
python scripts/skills_market.py list-installed --target-root dist/installed-skills
python scripts/skills_market.py update moyuan.release-note-writer --index dist/market/channels/stable.json --target-root dist/installed-skills --dry-run
python scripts/skills_market.py remove moyuan.release-note-writer --target-root dist/installed-skills
```

`skills.lock.json` 会记录当前安装状态，所以使用者不需要自己记住安装目录、版本和 channel。

## 怎么用 starter bundle 一次装一组能力

如果你还不确定该先装哪几个 skill，比起逐个搜索，更自然的入口往往是先看 starter bundle：

```text
python scripts/skills_market.py list-bundles
python scripts/skills_market.py list-bundles --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py install-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
```

当前 bundle 安装的语义是：

- 会按 bundle 内每个 skill 自己所在的 channel 解析 install spec
- `active` skill 正常安装
- `deprecated` skill 继续允许安装，但会保留 warning
- `blocked` 和 `archived` skill 会被跳过，并在结果摘要里说明原因

如果你只是想先看安装计划而不落盘：

```text
python scripts/skills_market.py install-bundle skill-authoring-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
```

真实安装后，目标目录下会生成 `bundle-reports/<bundle-id>.json`，方便回看这次 bundle 安装到底装了哪些、跳过了哪些。

## 装完 bundle 之后怎么看、怎么删

starter bundle 真正好用的地方，不只是“一次装一组”，也包括后续能看懂自己装了什么、删的时候不误删：

```text
python scripts/skills_market.py list-installed --target-root dist/installed-bundles
python scripts/skills_market.py list-installed-bundles --target-root dist/installed-bundles
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles
```

当前的语义是：

- `skills.lock.json` 会记录每个 skill 的 `sources`
- direct install 会保留 `direct:direct-install`
- bundle install 会额外追加 `bundle:<bundle-id>`
- 所以 `remove-bundle` 只会移除当前 bundle 的 ownership，而不会误删仍被 direct install 或其他 bundle 持有的 skill

## 装好的 bundle 怎么更新

如果 market 里的 starter bundle 定义或对应 skill 的 install spec 有变化，当前可以直接做 bundle 级更新：

```text
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
```

当前 update 的语义是：

- 先按当前 bundle 定义重新解析目标成员
- 再刷新这些 skill 的安装内容
- 最后 reconcile 当前 bundle 的 ownership，把已经不属于 bundle 的旧成员移出去

如果某个 skill 还有 `direct:direct-install` 或其他 bundle 来源，它只会失去当前 bundle 的 ownership，不会被删掉。

## 安装态漂移了怎么查

如果你怀疑本地安装态有点乱，比如手动删过目录、bundle report 失联，或者 lock 里的路径已经不对，当前可以直接跑：

```text
python scripts/skills_market.py doctor-installed --target-root dist/installed-skills
python scripts/skills_market.py doctor-installed --target-root dist/installed-skills --strict
python scripts/skills_market.py repair-installed --target-root dist/installed-skills --dry-run
python scripts/skills_market.py repair-installed --target-root dist/installed-skills
python scripts/skills_market.py snapshot-installed --target-root dist/installed-skills --output-path dist/installed-skills/snapshots/latest.json --markdown-path dist/installed-skills/snapshots/latest.md
python scripts/skills_market.py diff-installed dist/installed-skills/snapshots/before.json dist/installed-skills/snapshots/after.json --output-path dist/installed-skills/snapshots/diff.json --markdown-path dist/installed-skills/snapshots/diff.md
python scripts/skills_market.py verify-installed dist/installed-skills/snapshots/baseline.json --target-root dist/installed-skills --output-dir dist/installed-skills/verification --strict
python scripts/skills_market.py promote-installed-baseline dist/installed-skills/snapshots/baseline.json --target-root dist/installed-skills --markdown-path dist/installed-skills/snapshots/baseline.md --diff-output-path dist/installed-skills/snapshots/baseline-transition.json --diff-markdown-path dist/installed-skills/snapshots/baseline-transition.md
```

当前 doctor 会检查：

- `skills.lock.json` 记录的 skill 目录是不是还在
- lock 里的 `install_spec` 和 `provenance_path` 是不是还有效
- installed entrypoint 是否真的存在
- bundle ownership 是否还能对上 bundle report
- 安装根目录下有没有没被 lock 管理的 orphan 目录

当前 repair 会保守处理两类低风险漂移：

- 删除没有被 `skills.lock.json` 跟踪的 orphan 安装目录
- 删除已经没有任何 installed ownership 指向它的 stale bundle report

更高风险的问题，比如 lock / ownership 本身冲突，当前仍然要求先由 `doctor-installed` 暴露出来，再人工判断。

如果你想把“此刻本地安装态”留档给自己或团队 review，当前也可以直接导出 snapshot：

- JSON snapshot 适合归档、做后续 diff、或者喂给外部审计脚本
- Markdown summary 适合直接贴进 issue、PR 或运维记录里

如果你已经有两次 snapshot，当前也可以直接跑 diff：

- 它会告诉你哪些 skill 是新增、移除或发生了配置变化
- 它也会告诉你 bundle 是新增、移除还是成员发生了变化

如果你已经有一份“期望状态”的 baseline snapshot，当前也可以直接做基线校验：

- `verify-installed` 会先抓取当前 live state
- 然后自动和 baseline snapshot 做 diff
- `--strict` 会在 drift 出现时返回非零退出码，适合接 CI、值班脚本或本地运维门禁

如果 drift 已经被 review 通过，当前也可以直接把 live state 提升成新的 baseline：

- `promote-installed-baseline` 会重写 baseline snapshot 和对应 Markdown 摘要
- 如果旧 baseline 已存在，它还会额外生成一份 transition diff，保留这次基线变更记录

## lifecycle 对安装意味着什么

- `active`
  正常安装
- `deprecated`
  给 warning，但允许安装
- `blocked`
  安装会失败
- `archived`
  安装会失败

## starter bundle 和 recommendation 的意义

当前 market 不只在回答“装哪个”，也在回答“装完这个以后，最相关的下一个能力是什么”。

starter bundle 适合：

- 给新人一次装一组常见能力
- 给团队定义标准工作包
- 给 org/private market 做精选入口

recommendation 适合：

- 在单个 skill 详情页附近给出相关能力
- 帮用户补齐同一任务链上的下一步能力

## federation feed 是干什么的

如果 public 或 org market 要被别的客户端、站点或聚合器消费，当前可以直接导出：

```text
python scripts/skills_market.py federation-feed
python scripts/skills_market.py federation-feed --org-policy governance/orgs/moyuan-internal.json
```

这会生成 metadata-only feed，适合下游 marketplace / aggregator 使用。

## 相关文档

- [market-spec.md](./market-spec.md)
- [market-governance.md](./market-governance.md)
- [market-registry.md](./market-registry.md)
- [publisher-guide.md](./publisher-guide.md)
- [repo-commands.md](./repo-commands.md)
