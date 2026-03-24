# Skills 学习指南

这篇文档面向两类读者：

- 想学会“一个好的 skill 到底怎么构建”的人
- 想进一步理解“skills 为什么会走向 harness engineering”的人

如果你只想先做一个最小版本，先读 [skill-quickstart.md](./skill-quickstart.md)。
如果你想先看结构硬约束，先读 [skill-spec.md](./skill-spec.md)。
如果你想按课程顺序完整学习整个项目，先从 [teaching/README.md](./teaching/README.md) 开始。

## 先建立一个心智模型

在这个仓库里，skill 不是“写一篇长说明”。

它更像一个可触发的能力包，通常分成几层：

1. frontmatter
   决定是否触发
2. `SKILL.md`
   决定 agent 进入哪条路径
3. `references/`
   提供按需加载的知识
4. `scripts/`
   承接稳定执行逻辑
5. `assets/`
   提供模板与输出资源

先记住一句话：

- `SKILL.md` 是入口，不是百科全书

## 推荐学习顺序

推荐按下面顺序学：

1. 先看教学入口 [teaching/README.md](./teaching/README.md)
   先建立课程化学习路径
2. 再看仓库首页 [../README.md](../README.md)
   先理解这个仓库为什么从“业务 skill 仓库”转成“教学型 skills 实验室”
3. 再看 [skill-spec.md](./skill-spec.md)
   先把结构边界看清楚
4. 然后看 [skill-authoring.md](./skill-authoring.md)
   学从 0 到 1 怎么做 skill
5. 再看 [progressive-disclosure.md](./progressive-disclosure.md)
   学怎么把内容拆到合适的层级
6. 接着看 [harness-engineering.md](./harness-engineering.md)
   学怎么把 skill 放进更大的 agent system
7. 最后看 [skill-future-roadmap.md](./skill-future-roadmap.md)
   把静态 skill、动态 harness、eval 和 automation 放到一条演进线上看

## 三个教学型 skill 分别学什么

### `build-skills`

这个 skill 用来教“怎么把一个需求变成可维护的 skill”。

你应该重点看：

- `skills/build-skills/SKILL.md`
  看它怎么把 skill 设计、资源规划、校验闭环路由到不同 reference
- `skills/build-skills/references/`
  看它怎么把制作流程拆成几个最常见的问题
- `skills/build-skills/assets/skill-design-canvas.md`
  看一个 skill 设计表应该包含哪些决策

从它身上最该学到的是：

- 先收窄边界，再开始写 skill
- 先规划资源层，再开始写 `SKILL.md`
- skill 不是写完就结束，还要留下回归入口

### `progressive-disclosure`

这个 skill 用来教“怎么切分上下文层级”。

你应该重点看：

- `skills/progressive-disclosure/SKILL.md`
  看它如何把不同类型的问题送去不同 reference
- `skills/progressive-disclosure/references/loading-splits.md`
  看如何决定一段知识应该放在哪一层
- `skills/progressive-disclosure/assets/loading-plan-template.md`
  看重构时如何显式地写出加载计划

从它身上最该学到的是：

- 不是内容越多越好，而是分层越清晰越好
- 不是拆得越细越好，而是路由越清楚越好
- 渐进式披露的目标不是省 token，而是提高命中率、清晰度和可维护性

### `harness-engineering`

这个 skill 用来教“当 skill 不够用了，系统应该怎么继续长”。

你应该重点看：

- `skills/harness-engineering/SKILL.md`
  看它怎么把 harness primitives、eval、future roadmap 分开
- `skills/harness-engineering/references/harness-primitives.md`
  看 skill 和 harness 的边界怎么分
- `skills/harness-engineering/assets/harness-blueprint.md`
  看一个 agent system 设计图最少要写哪些字段

从它身上最该学到的是：

- skill 解决的是“知识与流程如何被加载”
- harness 解决的是“系统如何稳定运行、如何被观察、如何持续回归”
- 未来成熟的 agent 系统通常同时需要 skill 和 harness，而不是二选一

## 如何把这三个 skill 串起来看

推荐把它们看成一条连续的设计链：

1. `build-skills`
   回答“这个能力包应该怎么做出来”
2. `progressive-disclosure`
   回答“做出来以后，信息应该怎样分层”
3. `harness-engineering`
   回答“再往前走，系统应该怎样围绕这些 skill 建起来”

如果你只学第一步，很容易把 skill 做成长文档。
如果你学到第二步，skill 会更像真正的能力入口。
如果你学到第三步，就会开始思考 eval、tool contract、automation、memory 和 safety。

## 最适合的实践方式

推荐的实践顺序不是“先读完所有文档”，而是：

1. 先用 [skill-design-template.md](./skill-design-template.md) 把一个需求翻译成结构
2. 再照着 [skill-quickstart.md](./skill-quickstart.md) 做出一个最小版本
3. 然后用 [skill-spec.md](./skill-spec.md) 和仓库脚本做结构检查
4. 最后再回头看 [progressive-disclosure.md](./progressive-disclosure.md) 和 [harness-engineering.md](./harness-engineering.md)，思考怎样升级
