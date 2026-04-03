# Skills 的发展之路

这篇文档尝试回答一个问题：

- skills 接下来会往哪里长？

这里给出的是一个工程判断，而不是唯一标准答案。

## 阶段 0：零散提示词

最初很多团队只有：

- prompt 片段
- 零散脚本
- 口口相传的经验

这个阶段最大的问题是：

- 不可复用
- 不可验证
- 不可维护

## 阶段 1：静态 Skill

当团队开始把知识和流程收拢成 `SKILL.md`，就进入了静态 skill 阶段。

优点：

- 开始可复用
- 有了统一入口

问题：

- 很容易越写越长
- 路由、知识、实现混在一起

## 阶段 2：渐进式 Skill

当 skill 被拆成 frontmatter、`SKILL.md`、`references/`、`scripts/`、`assets/`，就进入渐进式阶段。

优点：

- 上下文更省
- 路由更清楚
- 维护成本更低

问题：

- 仍然主要解决“知识加载”问题
- 对 eval、state、automation 的支持还比较弱

## 阶段 3：Skill + Eval Harness

再往前一步，团队会开始补：

- 统一检查脚本
- task replay
- regression eval
- trace 与 artifact 留存

这个阶段的 skill 不再只是文档包，而是被放进了可回归的运行环境里。

## 阶段 4：Skill + Operating Harness

继续演进后，系统会开始出现：

- tool contract
- state / memory 管理
- safety gate
- orchestration
- automation / scheduling

这时，skill 仍然存在，但它变成了系统中的一个层，而不是系统本身。

## 阶段 5：Skill Mesh / Agent OS

更成熟的组织可能会走到这一步：

- 多个 skill 组成能力网络
- 调度器根据任务自动选择 skill
- eval 和 telemetry 驱动持续迭代
- 安全、审批、记忆、自动化都在系统层统一治理

这个阶段里，skill 更像：

- 一个可组合的知识与流程模块

而 harness 更像：

- 一个可运行、可观察、可升级的 agent operating system

## 为什么这条路线重要

如果只把 skill 当成 prompt 封装，就很难理解：

- 为什么同一个 skill 在不同系统里表现差异很大
- 为什么光加说明并不能解决稳定性问题
- 为什么越到后面，eval 和 safety 越重要

## 对 `moyuan-skills` 的具体启发

这个仓库现在选择做三件事：

1. 先把“如何构建 skill”讲清楚
2. 再把“如何设计渐进式披露”讲清楚
3. 同时把“如何走向 harness engineering”提前纳入设计

这意味着本仓库不是停留在“教你写一个 skill”，而是希望把你带到：

- 会做 skill
- 会拆层
- 会提前思考 skill 未来怎样进入更大的 agent system

## 一个务实的结论

未来最有价值的，不会只是“有多少个 skill”，而是：

- 这些 skill 有没有清晰边界
- 有没有稳定路由
- 有没有检查与评测闭环
- 能不能被更大的 harness 安全地编排起来

因此，skills 的发展之路，不是从有到多，而是从“提示词资产”走向“系统级能力模块”。
