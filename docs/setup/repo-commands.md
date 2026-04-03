# 仓库常用命令

这份文档只保留当前主线开发最常用的命令。

更细的单点脚本说明，应该回写到对应权威文档，不再把所有一次性命令无限堆在这里。

## 1. 最小基线检查

第一次进入仓库，先跑这 4 条：

```text
python scripts/check_progressive_skills.py
python scripts/check_docs_links.py
python scripts/skills_market.py smoke
python scripts/check_python_market_backend.py
```

这组命令覆盖：

- skill 结构
- docs 链接
- market 主链路
- backend 基本可用性

## 2. 作者链

创建一个新 skill：

```text
python scripts/skills_market.py scaffold-skill my-skill --template market-ready
```

检查一个 skill：

```text
python scripts/skills_market.py doctor-skill skills/my-skill
python scripts/skills_market.py validate skills/my-skill/market/skill.json
```

打包与校验：

```text
python scripts/skills_market.py package my-skill
python scripts/skills_market.py provenance-check dist/market/install/my-skill-0.1.0.json
```

如果你正在做发布前交接，再补：

```text
python scripts/skills_market.py build-submission my-skill
python scripts/skills_market.py validate-submission dist/submissions/moyuan/my-skill/0.1.0/submission.json
python scripts/skills_market.py upload-submission dist/submissions/moyuan/my-skill/0.1.0/submission.json --inbox-dir incoming/submissions
python scripts/skills_market.py review-submission incoming/submissions/moyuan/my-skill/0.1.0/submission.json --review-status approved --reviewer "Market Maintainer" --summary "Submission passed inbox review."
python scripts/skills_market.py ingest-submission incoming/submissions/moyuan/my-skill/0.1.0/submission.json
```

## 3. Market 构建与远端安装

```text
python scripts/skills_market.py index
python scripts/skills_market.py catalog
python scripts/skills_market.py recommend
python scripts/skills_market.py federation-feed
python scripts/skills_market.py registry
python scripts/skills_market.py search --query release
python scripts/skills_market.py search --registry http://127.0.0.1:8765 --query release
python scripts/skills_market.py catalog --registry http://127.0.0.1:8765
python scripts/skills_market.py inspect-remote-skill moyuan.release-note-writer --registry http://127.0.0.1:8765
python scripts/skills_market.py install dist/market/install/release-note-writer-0.1.0.json --dry-run
python scripts/skills_market.py install moyuan.release-note-writer --registry http://127.0.0.1:8765 --dry-run
python scripts/skills_market.py install-bundle release-engineering-starter --registry http://127.0.0.1:8765 --target-root dist/installed-remote-bundles
```

## 4. Frontend / Backend 联调

启动 backend：

```text
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 38083
```

启动 frontend：

```text
npm ci --prefix frontend
SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083 npm run dev:local --prefix frontend
```

构建与端到端验证：

```text
npm run build --prefix frontend
npm run e2e --prefix frontend
```

说明：

- `npm run e2e --prefix frontend` 依赖已有 `.next` 构建产物。
- Playwright 当前会优先复用仓库 `.venv` 里的 Python 启动 backend 和 registry fixture。

如果你要手动验证 remote registry UI，再补：

```text
python scripts/serve_market_registry_fixture.py --host 127.0.0.1 --port 38765 --output-dir dist/playwright-registry --clean
```

## 5. Installed-State 运维

```text
python scripts/skills_market.py doctor-installed --target-root dist/installed-skills --strict
python scripts/skills_market.py repair-installed --target-root dist/installed-skills --dry-run
python scripts/skills_market.py snapshot-installed --target-root dist/installed-skills --output-path dist/installed-skills/snapshots/latest.json --markdown-path dist/installed-skills/snapshots/latest.md
python scripts/skills_market.py verify-installed dist/installed-skills/snapshots/baseline.json --target-root dist/installed-skills --output-dir dist/installed-skills/verification --strict
```

## 6. 业务与案例回归

如果你改动的是 skill 内容或案例逻辑，再补这组：

```text
python skills/release-note-writer/scripts/check_release_note_writer.py
python skills/issue-triage-report/scripts/check_issue_triage_report.py
python skills/incident-postmortem-writer/scripts/check_incident_postmortem_writer.py
python skills/api-change-risk-review/scripts/check_api_change_risk_review.py
python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json
```

## 7. 维护规则

- 这里只保留主线开发经常使用的命令。
- 某个能力线如果已经有专属文档，应在专属文档里维护详细命令。
- 一次性验证命令不要继续追加到这份文档。

## Skills Market Client Lifecycle

如果你要验证“安装后的客户端动作”而不只是打包与索引，补跑下面这组命令：

```text
python scripts/skills_market.py package release-note-writer
python scripts/skills_market.py install dist/market/install/release-note-writer-0.1.0.json --target-root dist/installed-skills
python scripts/skills_market.py list-installed --target-root dist/installed-skills
python scripts/skills_market.py update moyuan.release-note-writer --index dist/market/channels/stable.json --target-root dist/installed-skills --dry-run
python scripts/skills_market.py remove moyuan.release-note-writer --target-root dist/installed-skills
python scripts/skills_market.py install moyuan.release-note-writer --registry http://127.0.0.1:8765 --target-root dist/installed-remote-skills
```

如果你只想让 smoke 一次性把这条链路也覆盖进去，直接跑：

```text
python scripts/check_market_pipeline.py
```

## Skills Market Starter Bundles

如果你要验证 bundle 级消费链路，补跑下面这组命令：

```text
python scripts/skills_market.py list-bundles
python scripts/skills_market.py list-bundles --org-policy governance/orgs/moyuan-internal.json
python scripts/skills_market.py install-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
python scripts/skills_market.py install-bundle skill-authoring-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py install-bundle release-engineering-starter --registry http://127.0.0.1:8765 --target-root dist/installed-remote-bundles
```

它们分别在验证：

- bundle 是否能被发现
- org/private scope 是否会正确过滤 bundle
- bundle 是否能跨 stable / beta channel 一次性安装
- archived skill 是否会在 bundle 安装里被跳过而不是直接中断

## Skills Market Bundle State

如果你要验证 bundle 安装后的查看和回收动作，补跑下面这组命令：

```text
python scripts/skills_market.py list-installed --target-root dist/installed-bundles
python scripts/skills_market.py list-installed-bundles --target-root dist/installed-bundles
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py remove-bundle release-engineering-starter --target-root dist/installed-bundles
```

它们分别在验证：

- `skills.lock.json` 是否记录了来源信息
- bundle report 和当前安装状态能否对应起来
- bundle 移除是否会先给出安全预览
- shared ownership 是否会保留 direct install 或其他 bundle 仍然需要的 skill

## Skills Market Bundle Update

如果你要验证已安装 bundle 的刷新和对齐动作，补跑下面这组命令：

```text
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles --dry-run
python scripts/skills_market.py update-bundle release-engineering-starter --market-dir dist/market --target-root dist/installed-bundles
```

它们分别在验证：

- bundle 当前定义能否重新解析成 install plan
- 已安装的 bundle members 能否按最新 market 重新刷新
- 不再属于 bundle 的旧成员能否在 reconcile 阶段安全移除 ownership

## Skills Market Installed-State Doctor

如果你要验证本地安装态有没有漂移，补跑下面这组命令：

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
python scripts/skills_market.py remediate-installed-history-waiver-source-reconcile-waivers dist/installed-skills/snapshots/baseline-history.json --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
python scripts/skills_market.py draft-installed-history-waiver-source-reconcile-waiver-execution dist/installed-skills/snapshots/baseline-history.json --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
python scripts/skills_market.py preview-installed-history-waiver-source-reconcile-waiver-execution dist/installed-skills/snapshots/baseline-history.json --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
python scripts/skills_market.py prepare-installed-history-waiver-source-reconcile-waiver-apply dist/installed-skills/snapshots/baseline-history.json --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json --strict
python scripts/skills_market.py execute-installed-history-waiver-source-reconcile-waiver-apply dist/installed-skills/snapshots/baseline-history.json --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json --strict
python scripts/skills_market.py verify-installed-history-waiver-source-reconcile-waiver-apply dist/installed-skills/snapshots/baseline-history.json --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --source-reconcile-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json --apply-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-gate-waiver-apply-execute-summary.json --strict
python scripts/skills_market.py report-installed-history-waiver-source-reconcile-waiver-apply dist/installed-skills/snapshots/baseline-history.json --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --source-reconcile-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json --apply-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-gate-waiver-apply-execute-summary.json --output-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-gate-waiver-apply-report.json --markdown-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-gate-waiver-apply-report.md
python scripts/skills_market.py list-installed-history-waiver-source-reconcile-waiver-apply-policies
python scripts/skills_market.py list-installed-history-waiver-source-reconcile-waiver-apply-waivers
python scripts/skills_market.py audit-installed-history-waiver-source-reconcile-waiver-apply-waivers dist/installed-skills/snapshots/baseline-history.json --gate-waiver approved-expired-release-downsize-source-drift --apply-gate-waiver approved-expired-source-reconcile-gate-waiver-apply-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --source-reconcile-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json --apply-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-gate-waiver-apply-execute-summary.json --strict
python scripts/skills_market.py gate-installed-history-waiver-source-reconcile-waiver-apply dist/installed-skills/snapshots/baseline-history.json --policy source-reconcile-waiver-apply-release-gate --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --source-reconcile-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json --apply-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-gate-waiver-apply-execute-summary.json --strict
python scripts/skills_market.py gate-installed-history-waiver-source-reconcile-waiver-apply dist/installed-skills/snapshots/baseline-history.json --policy source-reconcile-waiver-apply-release-gate --gate-waiver approved-expired-release-downsize-source-drift --apply-gate-waiver approved-expired-source-reconcile-gate-waiver-apply-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --source-reconcile-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json --apply-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-gate-waiver-apply-execute-summary.json --strict
python scripts/skills_market.py gate-installed-history-waiver-source-reconcile-waiver-apply dist/installed-skills/snapshots/baseline-history.json --policy source-reconcile-waiver-apply-review-handoff --gate-waiver approved-expired-release-downsize-source-drift --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --source-reconcile-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json --apply-execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-gate-waiver-apply-execute-summary.json --strict
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --strict
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --waiver approved-release-engineering-downsize --strict
python scripts/skills_market.py restore-installed-baseline dist/installed-skills/snapshots/baseline-history.json 1 --baseline-path dist/installed-skills/snapshots/baseline.json --markdown-path dist/installed-skills/snapshots/baseline.md
python scripts/skills_market.py prune-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --keep-last 5
```

它们分别在验证：

- `skills.lock.json`、bundle report 和安装目录是否对得上
- `install_spec`、`provenance_path` 和 installed entrypoint 是否仍然有效
- orphan 安装目录或失联 bundle ownership 能否被及时发现
- 低风险漂移能否被 `repair-installed` 保守修掉，而不是要求手工清理全部现场
- 当前安装态能否被导出成 snapshot，供维护者后续 review 和 diff
- 两次 snapshot 之间的 skill / bundle 变化能否被稳定总结出来
- 历史归档的 baseline 能否被直接拿来做 verify，而不用先回写到当前 baseline 文件
- 两个历史归档 baseline 能否被直接拿来做 diff，而不用手动来回复制旧文件
- retained history 能否被直接汇总成 timeline/report，而不用人工整理多次 promotion
- retained history policy profile 能否被直接列出并复用，而不是每次都手敲一整组 threshold flag
- retained history waiver record 能否被直接列出并复用，而不是把已批准例外继续留在口头约定里
- retained history waiver record 能否被直接审计，而不是等它们过期或失效后还继续留在治理目录里
- retained history waiver finding 能否被直接转成 remediation 建议，而不是维护者还要自己解释“下一步该怎么处理”
- retained transition 能否按阈值或 policy 直接触发 alert/gate，而不是只靠人工目检 report
- 已批准的大变更能否在 waiver 落地后被重新视为通过，而不是让 gate 永远失败
- baseline promotion 能否被保留成 history 和 archive，而不是只有最后一个文件版本
- 历史 baseline 能否被恢复成当前运维基线，支撑回放和问题复盘
- 过旧的 baseline history / archive 能否被安全裁剪，而不是持续堆积
- 当前 live state 能否直接对比基线 snapshot，并在 drift 出现时作为门禁失败
- drift 被接受之后，当前 live state 能否被顺手提升成新 baseline，并留下 transition diff
- baseline promotion 的历史能否被查询出来，支撑后续回看和审计

## 常见维护动作

### 看某个文档是否还有占位符

```text
Get-ChildItem -Recurse -File | Select-String -Pattern "TODO|\[TODO"
```

### 查看 `docs/teaching/` 当前结构

```text
Get-ChildItem -Recurse docs\teaching
```

### 查看 skill 目录结构

```text
Get-ChildItem -Recurse skills
```

## 推荐的提交前最小命令集

如果你只想做一轮最小回归，推荐跑：

```text
python scripts/check_progressive_skills.py
python scripts/check_docs_links.py
python scripts/check_harness_prototypes.py
python skills/release-note-writer/scripts/check_release_note_writer.py
python skills/issue-triage-report/scripts/check_issue_triage_report.py
python skills/incident-postmortem-writer/scripts/check_incident_postmortem_writer.py
python skills/api-change-risk-review/scripts/check_api_change_risk_review.py
python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json
python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml
python scripts/skills_market.py smoke
python scripts/skills_market.py catalog
python scripts/skills_market.py governance-check
```
