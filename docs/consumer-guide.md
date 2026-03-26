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
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --strict
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --waiver approved-release-engineering-downsize --strict
python scripts/skills_market.py restore-installed-baseline dist/installed-skills/snapshots/baseline-history.json latest --baseline-path dist/installed-skills/snapshots/baseline.json --markdown-path dist/installed-skills/snapshots/baseline.md
python scripts/skills_market.py prune-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --keep-last 5
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
- `verify-installed-history` 会直接读取某个 archived history entry 做同样的校验，不需要先改写当前 baseline 文件

如果你不是要对 live state 做校验，而是想直接看“两个历史基线之间差了什么”，当前也可以直接比较 history entry：

- `diff-installed-history` 会直接读取两个 archived history entry
- 它适合做基线演进 review、故障复盘和运维审计
- 这样你就不需要先 restore 两次、再额外导出 snapshot diff

如果你想快速看整条基线演进轨迹，而不是手工把每个 entry 一个个拼起来，当前也可以直接导出 history report：

- `report-installed-baseline-history` 会输出 timeline 和 transition summary
- 它会把 retained entry 的 sequence、时间、摘要计数和关键 transition 汇总成一份 JSON/Markdown 报告
- 这样维护者在 review accepted baseline 演进时，不需要先手工跑多次 `list` 和 `diff`

如果你想把“基线演进过大”这件事直接变成提醒或门禁，当前也可以先看可复用 policy，再直接跑 history alert：

- `list-installed-history-policies` 会列出内置的 history alert policy profile
- 这些 profile 位于 `governance/history-alert-policies/`，并由 `schemas/installed-history-alert-policy.schema.json` 约束
- `alert-installed-baseline-history` 会按阈值检查 retained transition
- 它适合把“移除 skill 太多”“bundle 变化过大”“installed_count 波动过大”直接转成 alert
- `--policy latest-release-gate --strict` 适合接在最新一次 accepted baseline 之后，作为本地 gate 或 review 提醒
- 如果团队需要临时覆盖某个阈值，也可以在 `--policy` 之外继续叠加单独的 threshold flag

如果某次大变更已经被 review 接受，当前也可以把它落成明确 waiver，而不是让团队一直口头记忆：

- `list-installed-history-waivers` 会列出当前可复用的 waiver record
- 这些 waiver 位于 `governance/history-alert-waivers/`，并由 `schemas/installed-history-alert-waiver.schema.json` 约束
- `alert-installed-baseline-history --waiver ...` 会把匹配到的 alert 标记成 approved exception
- 这样 `passes` 会按未豁免的 active alert 来判断，而不是把所有历史大变更一律当成失败

如果团队已经开始积累 waiver，当前也应该把它们当成需要巡检的治理资产，而不是只会新增不会回收：

- `audit-installed-history-waivers` 会主动检查 expired、unmatched、stale waiver
- `expired` 表示这份批准记录已经过期
- `unmatched` 表示它已经匹配不到任何 retained transition，通常说明对应历史已经被 prune 或条件写错
- `stale` 表示它还能对上 retained transition，但已经对不上任何 active alert，通常说明这份例外已经没有继续保留的必要

当 audit 已经告诉你“哪里坏了”之后，当前也可以直接看 remediation 建议，而不是自己再翻译一遍：

- `remediate-installed-history-waivers` 会把 audit finding 转成下一步建议
- `draft-installed-history-waiver-execution` 会把 remediation 继续落成 execution pack，直接给出 renewal draft、replacement draft 或 cleanup review 草稿
- `preview-installed-history-waiver-execution` 会把 source waiver 和生成的 draft 放在一起比对，直接告诉你哪些字段会变化
- `prepare-installed-history-waiver-apply` 会把已经 review 过的 preview 继续变成 apply-ready patch、combined patch 和 target candidate 文件
- `execute-installed-history-waiver-apply` 会在 source hash 校验通过后，把 apply pack 安全地 stage 到单独目录，或按 `--write` 写回治理镜像目录
- `audit-installed-history-waiver-sources` 会拿 reviewed apply / execute 工件反查当前治理源文件，明确区分 pending、applied 和 drifted
- `reconcile-installed-history-waiver-sources` 会把 source-audit 里的 drift finding 收口成 restore target、restore delete 或 review artifact，方便后续恢复治理源文件
- `execute-installed-history-waiver-source-reconcile` 会继续对 reviewed reconcile pack 做 source hash 校验，再把恢复动作 stage 到单独目录，或按 `--write` 写回治理镜像目录
- `verify-installed-history-waiver-source-reconcile` 会在 source-reconcile execute 之后复核 staged 或 written 结果，确认治理源镜像仍然和 reviewed reconcile target 一致
- `report-installed-history-waiver-source-reconcile` 会把 source-audit、source-reconcile、execute、verify 四步聚合成一份交接报告，适合 reviewer 一次看完整条修复链路
- `list-installed-history-waiver-source-reconcile-policies` 会先列出内置的 source-reconcile gate profile
- `list-installed-history-waiver-source-reconcile-waivers` 会列出可复用的 source-reconcile gate waiver 例外
- `gate-installed-history-waiver-source-reconcile --policy ...` 会把这份 report 直接转成可复用 gate，默认推荐走命名 policy 而不是手写一串状态规则
- `gate-installed-history-waiver-source-reconcile --gate-waiver ...` 可以只豁免某个已知 finding 组合，而不是放宽整条 policy
- `audit-installed-history-waiver-source-reconcile-waivers` 会审计 source-reconcile gate waiver 是否已经过期、失配、陈旧，或者挂在错误 policy 上
- `remediate-installed-history-waiver-source-reconcile-waivers` 会把这些 audit finding 翻译成具体动作，比如续期、重定向匹配范围、替换或删除 waiver
- `draft-installed-history-waiver-source-reconcile-waiver-execution` 会把这些 remediation 动作继续落成 review-ready draft，例如 renewal draft、selector retarget draft、replacement draft 或 policy review
- `preview-installed-history-waiver-source-reconcile-waiver-execution` 会把这些 execution draft 和当前 source waiver 做字段级对比，方便 reviewer 先看变化再决定是否继续 apply
- `prepare-installed-history-waiver-source-reconcile-waiver-apply` 会把已审过的 preview 落成 apply-ready artifact，包括 per-waiver target、patch、combined patch，以及保留 review-only 的 policy mismatch
- `execute-installed-history-waiver-source-reconcile-waiver-apply` 会把这些 apply pack 安全地 stage 到临时 root，或者在 `--write` 下写进目标 mirror，同时留下 execution summary
- `verify-installed-history-waiver-source-reconcile-waiver-apply` 会把 apply execution summary 和当前 stage/write 目标重新对账，确认没有 drift，也会把 review-only action 继续保留成 manual review
- `report-installed-history-waiver-source-reconcile-waiver-apply` 会把 apply pack、execution summary 和 verification 结果聚合成单一 review pack，方便 handoff 和后续 gate 复用
- `list-installed-history-waiver-source-reconcile-waiver-apply-policies` 可以先列出内置的 release 和 review-handoff profile，避免每次手工拼 `--allow-state`
- `gate-installed-history-waiver-source-reconcile-waiver-apply --policy source-reconcile-waiver-apply-release-gate` 适合做严格 release 门禁
- `gate-installed-history-waiver-source-reconcile-waiver-apply --policy source-reconcile-waiver-apply-review-handoff` 适合把 drifted 或待跟进 workflow 固化成 review handoff，而不是直接拦死
- `renew_or_remove` 适合 expired waiver
- `rescope_or_remove` 适合 unmatched waiver
- `retire_or_replace` 适合 stale waiver
- 它保持只读输出，不会自动改治理文件，目的是把后续动作讲清楚而不是偷偷改审批记录

如果 drift 已经被 review 通过，当前也可以直接把 live state 提升成新的 baseline：

- `promote-installed-baseline` 会重写 baseline snapshot 和对应 Markdown 摘要
- 如果旧 baseline 已存在，它还会额外生成一份 transition diff，保留这次基线变更记录
- `--history-path`、`--history-markdown-path` 和 `--archive-dir` 可以把每次 promotion 变成可追溯、可恢复的基线归档动作

如果你想回看 baseline 是怎么一路演进过来的，当前也可以直接看 history：

- `list-installed-baseline-history` 会列出每次 promotion 的时间、目标安装根目录、摘要计数和归档位置
- `report-installed-baseline-history` 会把 retained history 汇总成一份 timeline/report，适合例行 review 和运维归档
- `list-installed-history-policies` 可以先列出当前可复用的 alert policy profile
- `list-installed-history-waivers` 可以先列出当前已经批准的 waiver record
- `audit-installed-history-waivers` 可以先把 waiver 做一轮健康检查，再决定哪些该续期、哪些该清理
- `remediate-installed-history-waivers` 可以把 audit 结果继续翻译成明确的 follow-up action
- `draft-installed-history-waiver-execution` 可以把 follow-up action 继续变成可 review 的 draft/review artifact
- `preview-installed-history-waiver-execution` 可以在真正应用前先把 source-vs-draft 变化列清楚，适合 reviewer 快速过一遍
- `prepare-installed-history-waiver-apply` 可以把已确认的 preview 收口成 patch/candidate 工件，方便后续人工应用或纳入 code review
- `execute-installed-history-waiver-apply` 可以把已确认的 apply pack 安全落到 staging 目录，或在 `--write` 模式下写入目标治理镜像，同时阻止 source mismatch
- `audit-installed-history-waiver-sources` 可以在 execute 之后继续核对治理源文件是否还和 reviewed target 一致，适合抓 post-execute drift
- `reconcile-installed-history-waiver-sources` 可以在 drift 出现后直接生成恢复包，区分“恢复到 reviewed target”“恢复 delete 状态”或“继续人工 review”
- `execute-installed-history-waiver-source-reconcile` 可以把 reviewed source-reconcile 恢复包真正 stage 或写回治理镜像，并继续阻止 post-review source mismatch
- `verify-installed-history-waiver-source-reconcile` 可以在 source-reconcile execute 之后继续核验 staged 或 written 结果，适合把恢复后的治理镜像再做一次 gate
- `report-installed-history-waiver-source-reconcile` 可以把当前 source drift、reconcile plan、execution 结果和 verify 状态汇总成一份 review pack，适合 handoff 和审计归档
- `list-installed-history-waiver-source-reconcile-policies` 可以先列出 `release-gate` 和 `review-handoff` 这类内置 profile
- `list-installed-history-waiver-source-reconcile-waivers` 可以先看有哪些已批准的 source-reconcile 例外可复用
- `gate-installed-history-waiver-source-reconcile --policy source-reconcile-release-gate` 适合严格 release/CI
- `gate-installed-history-waiver-source-reconcile --policy source-reconcile-release-gate --gate-waiver approved-expired-release-downsize-source-drift` 适合严格 gate 下临时接受一个已知 demo drift
- `audit-installed-history-waiver-source-reconcile-waivers` 适合在 strict gate 之前先清点这些例外是不是还有效，避免 waiver 累积成长期放行
- `remediate-installed-history-waiver-source-reconcile-waivers` 适合在 audit 之后直接生成治理动作建议，减少人工判断每条 finding 该怎么处理
- `draft-installed-history-waiver-source-reconcile-waiver-execution` 适合在 remediation 之后直接生成 review-ready draft pack，让维护者先审 renewal / retarget / replacement / policy review，再决定是否继续 apply
- `preview-installed-history-waiver-source-reconcile-waiver-execution` 适合在 draft 之后直接做 review diff，让 reviewer 先看哪些字段会变化、哪些仍然只是 review-only
- `prepare-installed-history-waiver-source-reconcile-waiver-apply` 适合在 preview 已确认后生成 patch-ready apply pack，但仍然不直接修改 `governance/source-reconcile-gate-waivers/`
- `execute-installed-history-waiver-source-reconcile-waiver-apply` 适合在 apply pack 已确认后做安全 stage/write，并把执行结果固化成可复用 summary，供后续 verify 和治理 review 使用
- `verify-installed-history-waiver-source-reconcile-waiver-apply` 适合在 stage/write 之后直接确认目标 root 仍和 reviewed apply pack 一致，并在后续 drift 出现时作为 strict gate
- `report-installed-history-waiver-source-reconcile-waiver-apply` 适合在执行与校验都完成后固化成一份 handoff report，后续不必再分别翻 apply/execute/verify 三份产物
- `gate-installed-history-waiver-source-reconcile-waiver-apply` 适合在 report 已生成后统一做 release 或 handoff 判断，让治理侧直接消费一个稳定信号
- `gate-installed-history-waiver-source-reconcile --policy source-reconcile-review-handoff` 适合 review/handoff 阶段，只要求策略里声明的条件成立
- `alert-installed-baseline-history` 会按阈值或 policy 标记 retained transition 里的大变更，适合 review 前的快速筛查
- `verify-installed-history` 可以直接拿某个 history entry 做 drift 检查，适合复盘和回看旧基线
- `diff-installed-history` 可以直接比较两个历史 entry，适合回答“这两次 accepted baseline 之间到底变了什么”
- `restore-installed-baseline` 可以把某个历史 entry 重新写回当前 baseline 文件
- `prune-installed-baseline-history` 可以清理过旧 history entry 和对应 archive，避免本地运维记录无限增长
- 这样 baseline promotion 就不再只是“覆盖文件”，而是带历史、可回放的运维动作

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
