# 飞书与语雀技能案例拆解

这篇教学文档把新接入的两个中文案例 `feishu-doc-sync` 和 `yuque-openapi` 放到同一条学习路径里，帮助你理解一件事：

同样是“把本地 Markdown 和云端文档系统接起来”，为什么一个 skill 会更像结构收口良好的产品化工具，另一个 skill 则更像在真实复杂业务中持续演进的能力包。

## 为什么要学这两个案例

这两个 skill 都不是玩具例子，而是完整的真实工作流：

- `yuque-openapi` 更适合学习“如何把能力收口成稳定命令族”
- `feishu-doc-sync` 更适合学习“复杂 skill 如何继续增长而不失控”

把它们放在一起看，你会更容易理解本仓库反复强调的三个原则：

- `SKILL.md` 负责路由，不负责承载所有细节
- `references/` 负责按主题拆分知识，不让单个入口越来越臃肿
- `scripts/` 负责吸收重复执行逻辑，让 skill 不只是“会解释”，还真的“能落地”

## 推荐阅读顺序

建议按下面顺序看：

1. 先读 [../yuque-openapi.md](../../skills/yuque-openapi.md)
2. 再读 [../feishu-doc-sync.md](../../skills/feishu-doc-sync.md)
3. 然后对照 [../skill-learning-guide.md](../../authoring/skill-learning-guide.md)
4. 最后回到 [03-build-your-first-skill.md](../foundations/03-build-your-first-skill.md) 或 [11-skill-author-path.md](../roles/11-skill-author-path.md)

这个顺序的重点不是先学哪个平台 API，而是先看“结构更规整的 skill”，再看“复杂度更高但仍能维持清晰边界的 skill”。

## 从 `yuque-openapi` 学什么

`yuque-openapi` 是一个很适合初学者拆结构的案例，因为它体现了“先把命令族和状态文件收口”的思路。

看它时重点观察这些点：

- `SKILL.md` 如何把 repo/doc CRUD、目录同步、TOC 重建、manifest 批量任务拆成清晰路由
- `references/` 如何一份文档只讲一类操作，而不是把所有 API 细节堆到一个文件里
- `scripts/yuque_api.py` 如何作为稳定入口，把复杂逻辑继续下沉到 `yuque_api_lib/`
- `assets/manifests/` 如何把常见批处理任务变成可复用模板

如果你正准备自己写一个新 skill，`yuque-openapi` 最值得借鉴的是：

- 先定义稳定命令族
- 再定义状态文件和批量任务入口
- 最后再扩展功能边界，而不是一开始就把所有分支揉进 `SKILL.md`

## 从 `feishu-doc-sync` 学什么

`feishu-doc-sync` 更适合学习“复杂 skill 如何在继续扩展时仍然保持渐进式结构”。

看它时重点观察这些点：

- `SKILL.md` 如何同时处理 tenant 模式和 user 模式，而没有丢掉任务路由的清晰度
- `references/` 如何把 auth、token、sync、pull/export、conflict、markdown mapping 拆开
- `scripts/feishu_doc_sync.py` 如何逐步吸收真实业务里的复杂操作，而不是把执行细节塞回说明文档
- `check_feishu_skill.py` 如何给复杂 skill 提供统一的回归入口

如果你以后会维护“功能不断增长的 skill”，这个案例最值得借鉴的是：

- 复杂度增长时，优先扩 references 和 scripts，不是扩长 `SKILL.md`
- 危险动作要放在显式确认后面
- 每增长一层复杂度，都要同步补检查入口和故障排查文档

## 两个案例放在一起时该怎么比

你可以用下面这张对照表来理解：

| 观察点 | `yuque-openapi` | `feishu-doc-sync` |
| --- | --- | --- |
| 适合的第一印象 | 收口良好的产品化案例 | 持续演进中的复杂案例 |
| 重点学习对象 | 命令族、索引文件、批量任务 | 多身份模式、冲突处理、保护式写入 |
| 最值得学的结构 | `scripts/yuque_api.py` + `yuque_api_lib/` | `SKILL.md` 路由 + `references/` 主题拆分 |
| 最值得学的工程动作 | 用 manifest 和 index 管理批量任务 | 用 guardrail、confirm、checker 管理风险增长 |

把这两个案例都看完以后，你会更容易判断自己正在写的是：

- 一个需要优先“收口”的 skill
- 还是一个需要优先“控复杂度”的 skill

## 如何把学到的东西迁移到自己的 skill

建议直接照着下面的顺序做：

1. 先写清楚你的 skill 到底解决什么任务，不要先想 API 列表
2. 再判断这个 skill 更像 `yuque-openapi` 还是更像 `feishu-doc-sync`
3. 如果你的任务是稳定批处理，先学 `yuque-openapi` 的命令族和索引设计
4. 如果你的任务天然有多模式、多权限或高风险写入，先学 `feishu-doc-sync` 的 guardrail 设计
5. 在动手写自己的 skill 前，再回看 [../skill-quickstart.md](../../authoring/skill-quickstart.md) 和 [../skill-authoring.md](../../authoring/skill-authoring.md)

## 最小实践建议

如果你想把这两个案例真正用来学习，不只是浏览文档，建议做下面这组最小实践：

1. 先读 [../yuque-openapi.md](../../skills/yuque-openapi.md)，并浏览 `skills/yuque-openapi/`
2. 再读 [../feishu-doc-sync.md](../../skills/feishu-doc-sync.md)，并浏览 `skills/feishu-doc-sync/`
3. 用 [../skill-design-template.md](../../authoring/skill-design-template.md) 给你自己的目标 skill 做一版结构草图
4. 最后回到 [../skill-quickstart.md](../../authoring/skill-quickstart.md)，开始做最小可用版本

## 学完后你应该能回答

- 为什么复杂 skill 不能只靠一份越来越长的 `SKILL.md`
- 为什么真实 skill 的增长最终一定会把逻辑推向 `references/` 和 `scripts/`
- 为什么“产品化收口”和“复杂度治理”是两种不同的设计重点
- 为什么本仓库要把这些真实案例放进中文 skills 教学路径里
