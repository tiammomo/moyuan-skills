# Skills 制作指南

这篇文档面向“要在这个仓库里新增或重构一个 skill”的人。

重点不是定义什么叫 skill，而是给出一条可落地、可维护、适合教学与长期演进的制作路径。

如果你只想先做出一个最小版本，先看 [skill-quickstart.md](./skill-quickstart.md)。
如果你想先核对仓库边界，再看 [skill-spec.md](./skill-spec.md)。

## 制作目标

一个成熟 skill 至少应该满足：

- 能被正确触发
- `SKILL.md` 足够短，能做路由而不是堆背景
- 复杂说明拆到了 `references/`
- 重复实现沉到了 `scripts/`
- 模板或样例沉到了 `assets/`
- 留下了最小可回归的检查入口

如果这个 skill 计划继续进入 market 链路，还应该能顺着作者链跑到：

- `doctor-skill`
- `validate`
- `package`
- `provenance-check`

## 推荐制作流程

### 1. 先收窄边界

开工前先回答五个问题：

1. 这个 skill 解决哪一类任务？
2. 用户通常会怎么描述这个需求？
3. 哪些内容是模型记忆不稳定、必须显式提供的？
4. 哪些逻辑会反复重写，值得做成脚本？
5. 哪些内容以后大概率会进入 harness，而不是继续留在 skill 里？

如果这一步没想清楚，最常见的后果就是：

- `description` 写太泛，skill 不容易被正确触发
- `SKILL.md` 越写越长，最后失去入口功能

### 2. 先设计渐进式结构

在写正文之前，先把内容拆层：

- frontmatter：只负责触发
- `SKILL.md`：只负责路由、安全约束、默认工作流
- `references/`：放专题规则与按需知识
- `scripts/`：放稳定执行逻辑
- `assets/`：放模板、样例和输出资源

一个很实用的判断标准是：

- 会稳定执行、反复复用：放 `scripts/`
- 很长、不是每次都读：放 `references/`
- 用于复制、输出、填空：放 `assets/`

### 3. 先写 frontmatter，再写 `SKILL.md`

推荐顺序是：

1. 先写 `name`
2. 再写 `description`
3. 再写 `SKILL.md` 的路由

因为 skill 的第一价值不是解释自己，而是被正确触发。

### 4. 让 `SKILL.md` 成为入口，而不是总文档

推荐保留这些部分：

- 一句目标说明
- `## Safety First`
- `## Task Router`
- `## Progressive Loading`
- `## Default Workflow`
- `## Reference Files`
- `## Bundled Resources`

其中：

- 核心路由和默认动作留在 `SKILL.md`
- 细节说明拆到 `references/`
- 复杂实现沉到 `scripts/`

### 5. 先把资源放到位，再回写路由

比较稳妥的顺序是：

1. 先建 `references/`、`scripts/`、`assets/`
2. 再写 `Task Router`
3. 最后补 `Bundled Resources`

这样做的好处是：

- 路由更贴近真实资源
- 更容易看出哪些内容重复了
- 后续维护时更容易判断该改路由还是该改实现

### 6. 给 skill 留下可回归入口

至少建议两层检查：

1. 仓库级结构 lint
2. skill 自己的最小 smoke/check

当前仓库推荐：

```text
python scripts/check_progressive_skills.py
python skills/<skill-name>/scripts/check_<skill_name>.py
```

### 7. 把 market 打包链接进作者流程

如果这个 skill 已经有 `market/skill.json`，不要把作者链停在 checker。

推荐继续跑到：

```text
python scripts/skills_market.py doctor-skill skills/<skill-name> --run-checker
python scripts/skills_market.py validate skills/<skill-name>/market/skill.json
python scripts/skills_market.py package skills/<skill-name>
python scripts/skills_market.py provenance-check dist/market/install/<skill-name>-<version>.json
```

如果你只是把 skill 先 scaffold 到 `dist/authoring-smoke/` 这种预演目录，也可以直接按路径打包：

```text
python scripts/skills_market.py package dist/authoring-smoke/<skill-name>
```

这一步的意义是：

- 提前暴露 manifest、artifact 路径和 provenance 问题
- 让作者在真正提交流程前先看到 install spec 长什么样
- 把后续 submission 流程建立在已验证的 package 上

### 8. 提前为 harness 留接口

这一步不是强制实现，而是强制思考。

每做一个 skill，都建议顺手想三件事：

1. 哪些规则未来应该从 `references/` 上移到 harness？
2. 哪些执行路径未来应该交给外部 orchestration、memory 或 eval？
3. 哪些危险动作需要未来交给系统级 safety gate，而不是继续靠文字提醒？

如果不提前想这一层，skill 很容易慢慢被迫承担系统职责。

## 最常见的反模式

- 把所有背景都堆进 `SKILL.md`
- 参考资料拆很多，但没有明确路由
- reference 再套 reference，形成深层迷宫
- 已经有复杂脚本，却没有统一检查入口
- manifest 已经写了，但从来没跑过 package / provenance-check
- skill 明明已经在承担 orchestration 和 safety gate，却还没有 harness 视角

## 交付前快速自查

- `description` 是否清楚包含 `Use when ...`？
- `SKILL.md` 是否仍然是入口？
- 每个 reference 是否都能在两跳内到达？
- 是否已经把重复逻辑沉到 `scripts/`？
- 是否已经把模板和样例沉到 `assets/`？
- 是否已经留下可回归命令？
- 如果要进入 market，是否已经跑过 package / provenance-check？
- 是否已经考虑哪些东西未来应该进入 harness？
