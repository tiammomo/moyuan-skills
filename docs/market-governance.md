# Skills Market Governance

这份文档专门讲当前仓库里已经落地的 `skills market` 治理层。

## 当前治理对象

仓库现在有 5 类治理资产：

1. `publisher profile`
   位置：`publishers/*.json`
2. `org market policy`
   位置：`governance/orgs/*.json`
3. `installed history alert policy`
   位置：`governance/history-alert-policies/*.json`
4. `installed history alert waiver`
   位置：`governance/history-alert-waivers/*.json`
5. `governance checker`
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

## Installed History Alert Waiver

installed history alert waiver 当前回答这些问题：

- 哪个已 review 的大变更可以被视为 approved exception
- 它对应哪条 policy gate
- 它匹配哪次 transition、哪些 metric，以及哪些 removed ids
- 这份例外是谁批准的、为什么批准、何时失效

当前参考：

- [../governance/history-alert-waivers/approved-release-engineering-downsize.json](../governance/history-alert-waivers/approved-release-engineering-downsize.json)
- [../schemas/installed-history-alert-waiver.schema.json](../schemas/installed-history-alert-waiver.schema.json)

这类 waiver 也会被 `scripts/check_market_governance.py` 一起校验，并在本地 client 的 history alert 工作流里把匹配到的 finding 转成 approved exception。
当 waiver 开始积累之后，维护者还需要定期跑本地 audit，确认没有过期、失配或已经失效的例外记录继续留在治理资产里。
再往下一步，维护者还需要把 audit finding 转成明确 remediation，而不是只留下“这里有问题”却不说明应该续期、删除还是重写 selector。

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

### 6. 应用 installed history alert waiver

```text
python scripts/skills_market.py list-installed-history-waivers
python scripts/skills_market.py alert-installed-baseline-history dist/installed-skills/snapshots/baseline-history.json --policy latest-release-gate --waiver approved-release-engineering-downsize --strict
```

### 7. 审计 installed history alert waiver

```text
python scripts/skills_market.py audit-installed-history-waivers dist/installed-skills/snapshots/baseline-history.json --strict
```

### 8. 生成 installed history waiver remediation

```text
python scripts/skills_market.py remediate-installed-history-waivers dist/installed-skills/snapshots/baseline-history.json --strict
```

### 9. 生成 installed history waiver execution draft

```text
python scripts/skills_market.py draft-installed-history-waiver-execution dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-execution --strict
```

### 10. 生成 installed history waiver preview

```text
python scripts/skills_market.py preview-installed-history-waiver-execution dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-preview --strict
```

### 11. 生成 installed history waiver apply pack

```text
python scripts/skills_market.py prepare-installed-history-waiver-apply dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --strict
```

### 12. 执行 reviewed installed history waiver apply pack

```text
python scripts/skills_market.py execute-installed-history-waiver-apply dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --stage-dir dist/installed-skills/snapshots/waiver-stage --strict
python scripts/skills_market.py execute-installed-history-waiver-apply dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --write --strict
```

### 13. 审计 reviewed installed history waiver source state

```text
python scripts/skills_market.py audit-installed-history-waiver-sources dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --strict
python scripts/skills_market.py audit-installed-history-waiver-sources dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
```

### 14. 生成 installed history waiver source reconcile pack

```text
python scripts/skills_market.py reconcile-installed-history-waiver-sources dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --strict
python scripts/skills_market.py reconcile-installed-history-waiver-sources dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
```

### 15. 执行 installed history waiver source reconcile pack

```text
python scripts/skills_market.py execute-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --stage-dir dist/installed-skills/snapshots/waiver-source-reconcile-stage --strict
python scripts/skills_market.py execute-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --write --strict
```

### 16. 验证 installed history waiver source reconcile execution

```text
python scripts/skills_market.py verify-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --stage-dir dist/installed-skills/snapshots/waiver-source-reconcile-stage --strict
python scripts/skills_market.py verify-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --strict
```

### 17. 汇总 installed history waiver source reconcile report

```text
python scripts/skills_market.py report-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root
python scripts/skills_market.py report-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json
```

### 18. 对 installed history waiver source reconcile 执行 gate

```text
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
python scripts/skills_market.py gate-installed-history-waiver-source-reconcile dist/installed-skills/snapshots/baseline-history.json --policy source-reconcile-review-handoff --output-dir dist/installed-skills/snapshots/waiver-apply --target-root dist/governance-write-root --execute-summary-path dist/installed-skills/snapshots/waiver-apply/source-reconcile-execute-write-summary.json --strict
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
- [../scripts/list_installed_baseline_history_waivers.py](../scripts/list_installed_baseline_history_waivers.py)
- [../scripts/audit_installed_baseline_history_waivers.py](../scripts/audit_installed_baseline_history_waivers.py)
- [../scripts/remediate_installed_baseline_history_waivers.py](../scripts/remediate_installed_baseline_history_waivers.py)
- [../scripts/draft_installed_baseline_history_waiver_execution.py](../scripts/draft_installed_baseline_history_waiver_execution.py)
- [../scripts/preview_installed_baseline_history_waiver_execution.py](../scripts/preview_installed_baseline_history_waiver_execution.py)
- [../scripts/prepare_installed_baseline_history_waiver_apply.py](../scripts/prepare_installed_baseline_history_waiver_apply.py)
- [../scripts/execute_installed_baseline_history_waiver_apply.py](../scripts/execute_installed_baseline_history_waiver_apply.py)
- [../scripts/audit_installed_baseline_history_waiver_sources.py](../scripts/audit_installed_baseline_history_waiver_sources.py)
- [../scripts/reconcile_installed_baseline_history_waiver_sources.py](../scripts/reconcile_installed_baseline_history_waiver_sources.py)
- [../scripts/execute_reconcile_installed_baseline_history_waiver_sources.py](../scripts/execute_reconcile_installed_baseline_history_waiver_sources.py)
- [../scripts/verify_installed_baseline_history_waiver_source_reconcile.py](../scripts/verify_installed_baseline_history_waiver_source_reconcile.py)
- [../scripts/report_source_reconcile_gate_waiver_apply.py](../scripts/report_source_reconcile_gate_waiver_apply.py)
- [../scripts/check_source_reconcile_gate_waiver_apply_gate.py](../scripts/check_source_reconcile_gate_waiver_apply_gate.py)
- [../scripts/list_source_reconcile_gate_waiver_apply_policies.py](../scripts/list_source_reconcile_gate_waiver_apply_policies.py)
- [../scripts/list_source_reconcile_gate_waiver_apply_waivers.py](../scripts/list_source_reconcile_gate_waiver_apply_waivers.py)
- [../scripts/audit_source_reconcile_gate_waiver_apply_waivers.py](../scripts/audit_source_reconcile_gate_waiver_apply_waivers.py)
- [../scripts/report_installed_baseline_history_waiver_source_reconcile.py](../scripts/report_installed_baseline_history_waiver_source_reconcile.py)
- [../scripts/check_installed_baseline_history_waiver_source_reconcile_gate.py](../scripts/check_installed_baseline_history_waiver_source_reconcile_gate.py)
- [../scripts/list_installed_baseline_history_waiver_source_reconcile_policies.py](../scripts/list_installed_baseline_history_waiver_source_reconcile_policies.py)
- [../scripts/list_installed_baseline_history_waiver_source_reconcile_waivers.py](../scripts/list_installed_baseline_history_waiver_source_reconcile_waivers.py)
- [../scripts/audit_installed_baseline_history_waiver_source_reconcile_waivers.py](../scripts/audit_installed_baseline_history_waiver_source_reconcile_waivers.py)
- [../scripts/remediate_installed_baseline_history_waiver_source_reconcile_waivers.py](../scripts/remediate_installed_baseline_history_waiver_source_reconcile_waivers.py)
- [../scripts/draft_source_reconcile_gate_waiver_execution.py](../scripts/draft_source_reconcile_gate_waiver_execution.py)
- [../scripts/preview_source_reconcile_gate_waiver_execution.py](../scripts/preview_source_reconcile_gate_waiver_execution.py)
- [../scripts/prepare_source_reconcile_gate_waiver_apply.py](../scripts/prepare_source_reconcile_gate_waiver_apply.py)
- [../scripts/execute_source_reconcile_gate_waiver_apply.py](../scripts/execute_source_reconcile_gate_waiver_apply.py)
- [../scripts/verify_source_reconcile_gate_waiver_apply.py](../scripts/verify_source_reconcile_gate_waiver_apply.py)
- [../schemas/installed-history-waiver-source-reconcile-policy.schema.json](../schemas/installed-history-waiver-source-reconcile-policy.schema.json)
- [../schemas/installed-history-waiver-source-reconcile-waiver.schema.json](../schemas/installed-history-waiver-source-reconcile-waiver.schema.json)
