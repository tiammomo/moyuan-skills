# Market Registry 与 Federation

这篇内容专门讲 `moyuan-skills` 现在已经怎样从“skills 仓库”走到“可分发的 skills market”。

## 学完后你应该能回答什么

读完这篇以后，你应该能说清楚：

- 为什么 market 不只是一个页面
- provenance 为什么是安装链的一部分
- starter bundle 和 recommendation 在市场里分别解决什么问题
- public market 和 org/private market 为什么要同时存在
- federation feed 为什么适合给下游 aggregator 消费

## 先看 5 个固定对象

理解当前这套 market，最稳的方式不是先看脚本，而是先把 5 个对象记住：

1. `manifest`
   描述 skill 的身份、权限、质量、生命周期和分发信号
2. `install spec`
   描述包怎么装、从哪装、校验什么
3. `provenance`
   描述这个包是谁打的、包内容对应哪一份源码、checksum 是什么
4. `bundle / recommendation`
   描述“相关能力组合”和“装了这个之后还该装什么”
5. `federation / registry`
   描述“如何把这些 metadata 给别的 market 或客户端消费”

## 当前仓库里这些对象在哪

- manifest:
  `skills/*/market/skill.json`
- provenance:
  `dist/market/provenance/*.json`
- bundle:
  `bundles/*.json`
- recommendations:
  `dist/market/recommendations/`
- federation feed:
  `dist/market/federation/public-feed.json`
- hosted registry:
  `dist/market-registry/`

## 当前命令链怎么跑

如果你要带着新人真正跑一遍，不建议一上来就从 `registry` 开始。更适合的顺序是：

```text
python scripts/skills_market.py package --all
python scripts/skills_market.py provenance-check dist/market/install/release-note-writer-0.1.0.json
python scripts/skills_market.py recommend
python scripts/skills_market.py federation-feed
python scripts/skills_market.py registry
python scripts/skills_market.py smoke
```

这条链分别在回答：

1. skill 能不能变成包
2. 包有没有 provenance 证明链
3. market 能不能推荐相关能力
4. 能不能把 metadata 导给下游
5. 能不能生成 public/private 一体的托管输出
6. 整条链有没有回归

## 当前已经具备的治理含义

现在这套分发链不只是“能打包”，而是已经带着治理信号一起跑：

- verified publisher
- review status
- lifecycle status
- org allowlist
- blocked skills
- featured bundles

安装侧的实际语义是：

- `active`: 可以安装
- `deprecated`: 会警告，但仍然允许安装
- `blocked`: 不允许安装
- `archived`: 不允许安装

这也是为什么 market 不是单独从 UI 开始做，而是先从 schema、package、install、governance 和 smoke 做起。

## 为什么这篇内容对整个项目学习很重要

到这里，项目的四层学习模型已经连起来了：

- `docs/teaching/`
  教你怎么理解
- `skills/`
  给你真实样例
- `scripts/`
  把规则变成可验证命令
- `dist/market*`
  把规则变成可分发产物

也就是说，这个项目现在已经不只是“讲 skills 怎么写”，而是已经能讲“skills 怎么发布、怎么被发现、怎么被治理、怎么被下游消费”。

## 推荐下一步阅读

1. [16-skills-market-evolution.md](./16-skills-market-evolution.md)
2. [../market-spec.md](../market-spec.md)
3. [../market-governance.md](../market-governance.md)
4. [../market-registry.md](../market-registry.md)
5. [../publisher-guide.md](../publisher-guide.md)
6. [../consumer-guide.md](../consumer-guide.md)

## 本地 Client 生命周期怎么教

如果你要带新人理解“market 不只是 catalog，也包含安装后的状态管理”，建议把下面这 4 条命令一起演示：

```text
python scripts/skills_market.py install dist/market/install/release-note-writer-0.1.0.json --target-root dist/installed-skills
python scripts/skills_market.py list-installed --target-root dist/installed-skills
python scripts/skills_market.py update moyuan.release-note-writer --index dist/market/channels/stable.json --target-root dist/installed-skills --dry-run
python scripts/skills_market.py remove moyuan.release-note-writer --target-root dist/installed-skills
```

这样新人能更直观地理解 3 件事：

1. `install spec` 不是静态说明，而是客户端可执行输入
2. `skills.lock.json` 是本地消费侧状态，而不是 registry 元数据
3. registry / install / lifecycle / smoke 是一条连续链路，不是彼此独立的几份脚本

## starter bundle 为什么是下一步

带新人继续往下学时，一个很自然的问题是：“既然 market 已经会推荐 bundles，为什么还要单个 skill 一个个装？”

这也是当前仓库把 bundle install 补上的原因。现在你可以直接演示：

```text
python scripts/skills_market.py list-bundles
python scripts/skills_market.py install-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
python scripts/skills_market.py install-bundle skill-authoring-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
```

用这 3 条命令，新人会更容易理解：

1. starter bundle 不是 marketing 文案，而是可执行的消费入口
2. market 的治理语义会继续传导到 bundle 安装，比如 archived skill 会被跳过
3. recommendation, bundle metadata, install spec, lifecycle 和 client state 最终会在消费端汇合

## bundle 状态管理为什么重要

再往下一步，新人通常会问：“如果一个 bundle 装了 3 个 skill，我后来只想删掉这组能力怎么办？会不会把手工安装的 skill 也删掉？”

当前仓库已经把这层也补上了，可以直接演示：

```text
python scripts/skills_market.py list-installed --target-root dist/installed-bundles
python scripts/skills_market.py list-installed-bundles --target-root dist/installed-bundles
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles
```

这 4 条命令背后对应的教学点是：

1. client state 不是只有“装没装”，还包括 ownership
2. bundle removal 不是简单删目录，而是要判断 skill 还属于谁
3. registry / bundle / lock / report 这些对象，最终都会在消费侧汇成一个治理闭环

## bundle update 为什么是最后一块

当新人已经理解了 bundle install 和 bundle removal，最后一个自然问题就是：“如果 market 里的 bundle 变了，我要不要整组重装？”

当前仓库已经把这层也补上了，可以直接演示：

```text
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
```

这两条命令背后对应的教学点是：

1. bundle 不是静态清单，而是会随 market 演进的对象
2. client 端需要一条 reconcile 流程，把“当前想要的 bundle”对齐到“当前已经安装的 bundle”
3. ownership 设计的真正价值，就是让 update 和 remove 都能安全进行

## 为什么还要有 installed-state doctor

当新人理解了 install / update / remove 之后，最后一个常见问题是：“如果本地状态已经乱了，我怎么知道问题出在哪？”

当前仓库已经把这层也补上了，可以直接演示：

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
python scripts/skills_market.py audit-installed-history-waivers dist/installed-skills/snapshots/baseline-history.json --strict
python scripts/skills_market.py remediate-installed-history-waivers dist/installed-skills/snapshots/baseline-history.json --strict
python scripts/skills_market.py draft-installed-history-waiver-execution dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-execution --strict
python scripts/skills_market.py preview-installed-history-waiver-execution dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-preview --strict
python scripts/skills_market.py prepare-installed-history-waiver-apply dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --strict
python scripts/skills_market.py execute-installed-history-waiver-apply dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --stage-dir dist/installed-skills/snapshots/waiver-stage --strict
python scripts/skills_market.py audit-installed-history-waiver-sources dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --strict
python scripts/skills_market.py reconcile-installed-history-waiver-sources dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --strict
python scripts/skills_market.py execute-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --stage-dir dist/installed-skills/snapshots/waiver-source-reconcile-stage --strict
python scripts/skills_market.py verify-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
python scripts/skills_market.py report-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root
python scripts/skills_market.py list-installed-history-waiver-source-reconcile-policies --json
python scripts/skills_market.py list-installed-history-waiver-source-reconcile-waivers --json
python scripts/skills_market.py gate-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --policy source-reconcile-release-gate --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
python scripts/skills_market.py gate-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --policy source-reconcile-release-gate --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
python scripts/skills_market.py audit-installed-history-waiver-source-reconcile-waivers dist/installed-skills/snapshots/baseline-history.json --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --strict
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --waiver approved-release-engineering-downsize --strict
python scripts/skills_market.py restore-installed-baseline dist/installed-skills/snapshots/baseline-history.json latest --baseline-path dist/installed-skills/snapshots/baseline.json --markdown-path dist/installed-skills/snapshots/baseline.md
python scripts/skills_market.py prune-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --keep-last 5
```

这两条命令背后对应的教学点是：

1. market client 不只是执行安装，也要能巡检自己的状态
2. lock、bundle report 和磁盘目录之间本质上是一组必须保持一致的不变量
3. “可维护的 market” 不只是 registry 做得好，还要消费端能自查漂移
4. 自查之后还需要最小的自愈能力，但这个自愈要先从低风险场景开始
5. 当你开始修复和运维本地状态时，还需要 snapshot 把“当前状态”沉淀成可回看的记录
6. 当记录积累起来之后，还需要 diff 把“这次和上次相比变了什么”讲清楚
7. 当你真的要把安装态纳入运维门禁时，还需要 baseline verify 把 drift 变成可执行的校验规则
8. 当 drift 被接受之后，还需要 baseline history 和 restore，把运维基线从“覆盖式更新”推进到“可归档、可回放”
9. 当 history 持续累积之后，还需要 prune 和 retention，把这套运维记录从“可回放”推进到“可长期维护”
10. 当你需要复盘某个旧基线时，还需要 direct history verify，把“历史可回看”推进到“历史可直接对照和校验”
11. 当 accepted baseline 继续积累之后，还需要 direct history diff，把“历史可校验”推进到“历史之间也能直接做演进分析”
12. 当 retained history 足够多之后，还需要 history report，把“历史可分析”推进到“历史可直接阅读和复盘”
13. 当 retained transition 开始变复杂之后，还需要 history alert 和 policy profile，把“历史可阅读”推进到“历史里的大变更能被主动标记、复用同一套阈值并接进门禁”
14. 当团队开始接受某些已 review 的大变更之后，还需要 history waiver，把“门禁可复用”推进到“已批准例外也能被显式记录、复用和审计”
15. 当 waiver 自己也开始积累之后，还需要 waiver audit，把“例外可复用”推进到“例外本身也会被定期巡检、续期和清理”
16. 当 audit 开始稳定发现问题之后，还需要 waiver remediation，把“问题可发现”推进到“问题后面该怎么处理也能被显式讲清楚”
8. 当 drift 被接受时，还需要 baseline promotion 把“新期望状态”正式落盘，而不是长期停留在告警状态
9. 当 baseline 开始持续演进时，还需要 history 把这条演进链条保存下来，方便团队回看
