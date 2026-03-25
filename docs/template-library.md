# 模板资产库

这个仓库现在把“方法论模板”明确沉淀成了一个单独的模板资产区：`templates/`。

它的目标不是替代 skill，而是降低两类成本：

- 新作者从 0 到 1 起步的成本
- 维护者把 skill 继续推进到 harness 层的成本

## 当前模板包

- `templates/skills/beginner-skill/`
  面向第一次写 skill 的作者，只保留最小骨架。
- `templates/skills/advanced-skill/`
  面向已经需要 `references/`、`scripts/`、`assets/` 和 checker 的完整 skill。
- `templates/harness/harness-ready/`
  面向已经准备把 skill 往 tool contract、eval、safety、automation 推进的系统层模板。

## 怎么选

### 从零开始学 skill

优先用 `beginner-skill`：

- 先把 frontmatter 和 4 个核心 section 写对
- 先把 router 和 progressive loading 写清楚
- 先不急着扩 references 和 scripts

### 已经确定要做业务案例

优先用 `advanced-skill`：

- 带一份完整 `SKILL.md` 模板
- 带一个 reference 模板
- 带一个 checker 模板
- 带一个输出资产模板

### 已经进入 harness thinking

优先用 `harness-ready`：

- tool contract 模板
- eval case 模板
- safety gate 模板
- automation 模板
- runtime blueprint 模板

## 使用建议

- 不要直接把模板里的占位词留进正式仓库
- 用模板时，优先删掉不需要的部分，而不是把所有段落都保留
- 如果一个模板已经被连续复用两到三次，再考虑把它正式纳入教学路径
