# Risk Rules

## Contents

- [Risk Level Heuristics](#risk-level-heuristics)
- [How to Write Migration Notes](#how-to-write-migration-notes)
- [Rollout Checks](#rollout-checks)

## Risk Level Heuristics

- `high`
  存在 breaking changes、auth 变化、或多个客户端可能同时受影响
- `medium`
  没有硬 breaking change，但存在弃用、默认值变化或 rollout coordination 成本
- `low`
  只有 additive change，且不涉及 auth、identity、billing、security

## How to Write Migration Notes

- 先写受影响调用方是谁
- 再写需要改什么
- 最后写 rollout 顺序或 fallback

## Rollout Checks

风险评审至少应该覆盖：

- 是否已经通知受影响调用方
- 是否有回滚路径
- 是否需要灰度或双写期
- 是否要补 contract test 或 baseline eval
