# 项目完善规划

这份文档回答的是：

- `moyuan-skills` 这个仓库接下来还应该补什么
- 哪些补充最能提升它的教学价值、工程价值和长期演进能力

## 总体判断

当前仓库已经完成了第一阶段重构：

- 有清晰的仓库定位
- 有三条核心方法论主线
- 有三个教学型 skill
- 有仓库级结构校验和 skill-local smoke check

但它还主要停留在“方法论首版”阶段。下一步要做的，不是继续堆概念，而是把它从“能讲”推进到“能学、能练、能验证、能演进”。

## 六大建设方向总表

| 方向 | 目标 | 代表交付物 | 当前优先级 |
| --- | --- | --- | --- |
| 教学体系完善 | 把文档集合变成课程化学习系统 | `docs/teaching/`、练习题、capstone、分层学习地图 | P0 |
| 示范案例 | 用真实 skill 验证方法论落地 | 轻量案例、中量案例、案例复盘文档 | P1 |
| 渐进式披露 lint | 把风格建议变成工程约束 | 更强的 `check_progressive_skills.py`、fixture、约束说明 | P1 |
| Harness 原型 | 把未来路线从概念变成原型资产 | tool contract、eval harness、safety gate、automation 示例 | P1 |
| 仓库运维能力 | 提升长期维护与 onboarding 体验 | 开发环境说明、命令索引、CI 补强、docs lint | P1 |
| 模板资产沉淀 | 降低学习者和维护者的起手成本 | beginner 模板、advanced 模板、eval/safety 模板 | P2 |

## 推荐推进顺序

建议按下面顺序推进，而不是六条线同时平均发力：

1. 先把教学体系补完整
2. 再引入示范案例
3. 同步增强渐进式披露 lint
4. 再开始做 harness 原型
5. 然后补运维与开发者体验
6. 最后系统化沉淀模板资产

这个顺序的原因是：

- 没有教学路径，仓库难学
- 没有案例，方法论难落地
- 没有 lint，结构容易漂移
- 没有 harness 原型，未来方向容易停留在口头上

## 优先级一：把教学体系做完整

这一层最重要，因为仓库当前最大的价值是教学和方法论沉淀。

建议补充：

- 明确的课程化学习路径
- 初级 / 中级 / 高级分层阅读建议
- 每个主题对应的练习题和作业
- 从“看文档”到“亲手做 skill”的 workshop 路径
- 一个 capstone 任务，把 `build-skills`、`progressive-disclosure`、`harness-engineering` 串起来

目标是把现在的“文档集合”升级成“学习系统”。

建议继续补的具体交付物：

- beginner / intermediate / advanced 三层学习路径
- 每个模块的练习题与复盘问题
- 一个从 0 到 1 的 capstone 项目
- 面向团队 onboarding 的教学首页

建议里程碑：

- M1：课程目录、学习地图、练习入口齐全
- M2：capstone 和标准答案框架上线
- M3：教学路径可直接用于新成员 onboarding

## 优先级二：补示范型案例

现在仓库主要是教学型 skill，本身足够清楚，但还缺“真实案例”来证明方法论如何落地。

建议补充两类案例：

- 轻量案例
  例如：`release-note-writer`、`api-schema-audit`、`doc-review-checker`
- 中量案例
  例如：带 `references/`、`scripts/`、`assets/` 和 checker 的完整 skill

每个案例都应当明确说明：

- 为什么这样命名
- 为什么这样拆层
- 为什么某些东西留在 skill，某些东西上移到 harness

建议优先落地的案例类型：

- 轻量教学案例
  目标是练 trigger、router 和最小 checker
- 中量结构案例
  目标是练 `references/`、`scripts/`、`assets/` 的协同
- harness 过渡案例
  目标是练“哪些内容已经不该继续留在 skill 里”

## 优先级三：把渐进式披露做成更强的工程约束

目前已经有 `check_progressive_skills.py`，但还可以继续增强。

建议补充：

- 对 `agents/openai.yaml` 与 `SKILL.md` 一致性的检查
- 对 `description` 长度、触发语义质量的更细粒度检查
- 对 `Task Router` 中 reference/script 入口格式的一致性检查
- 对示例反模式的 lint 或 fixture
- 对 teaching 模板完整性的自动检查

目标是让“渐进式披露”不只是风格建议，而是可回归的工程约束。

建议拆成三步实施：

1. 基础一致性检查
   检查 `SKILL.md`、`agents/openai.yaml`、resource sections 是否对齐
2. 路由质量检查
   检查 `Task Router` 的 reference/script 暴露格式是否统一
3. 教学模板检查
   检查 teaching 文档、模板和案例是否仍然符合仓库约定

## 优先级四：进入 Harness 原型阶段

这是这个仓库区别于普通 skill 仓库的关键发展方向。

建议优先做四个原型：

- tool contract 示例
  用结构化方式描述某个 skill 脚本的输入、输出、失败模式和安全边界
- eval harness 示例
  给一个 skill 配一组固定任务、期望输出和回归比较
- safety gate 示例
  给高风险路径设计 dry-run、confirm、review checkpoint
- automation 示例
  展示一个 skill 在周期性任务中的使用方式

这四类原型会把“未来发展之路”从概念变成可见的工程资产。

建议原型落地顺序：

1. tool contract
2. eval harness
3. safety gate
4. automation

因为前两项更容易给仓库带来明确的工程反馈，而后两项更依赖已有流程稳定下来。

## 优先级五：补仓库运维层能力

如果这个仓库要长期维护，还需要更稳定的工程支持。

建议补充：

- Python 依赖说明或最小开发环境文件
- 本地开发启动说明
- 文档结构检查命令汇总
- CI 中的 docs lint / markdown lint
- 版本迭代记录或 release note 机制

当前仓库已经有 CI 骨架，但还没有完整的开发者体验说明。

建议优先补的运维文件：

- `docs/dev-setup.md`
- `docs/repo-commands.md`
- `requirements-dev.txt` 或等价开发依赖说明
- markdown lint / docs lint 的 CI 步骤说明

## 优先级六：把“方法论”沉淀成模板资产

现在已经有一些模板，但还可以继续产品化。

建议继续沉淀：

- beginner 版 skill 模板
- advanced 版 skill 模板
- progressive-disclosure 重构模板
- harness blueprint 扩展模板
- eval plan 模板
- safety review 模板

目标是让学习者不仅知道“应该怎么想”，还知道“可以直接从什么开始做”。

建议模板资产最终形成三组：

- 构建型模板
  skill skeleton、design canvas、authoring checklist
- 重构型模板
  progressive-disclosure plan、router review、lint remediation
- 系统型模板
  harness blueprint、eval plan、safety review

## 一个建议的三阶段路线

### Phase 1：教学补全

重点：

- 完善 `docs/teaching/`
- 增加练习题、作业、capstone
- 补 README 和 docs 索引

产出目标：

- 新读者能按路径学完整个仓库

### Phase 2：案例补全

重点：

- 引入 2 到 3 个真实示范型 skill
- 补完整 checker 和拆层说明
- 给每个案例加“为什么这样设计”

产出目标：

- 学习者能把方法论映射到真实项目

### Phase 3：Harness 原型

重点：

- 补 tool contract、eval、safety gate、automation 原型
- 把未来 roadmap 变成可运行资产

产出目标：

- 仓库从“skills 教学仓库”升级成“skills + harness 实验仓库”

## 建议的负责人视角

如果按项目管理视角看，这六条线也可以分成三组责任面：

- 学习面
  教学体系完善、模板资产沉淀
- 工程面
  示范案例、渐进式披露 lint、仓库运维能力
- 未来面
  harness 原型

这样分组后，更容易安排阶段性 owner 和迭代节奏。

## 当前最值得立刻做的 7 件事

1. 完整建设 `docs/teaching/`，把学习路径课程化。
2. 新增一个端到端示范型业务 skill。
3. 为 `agents/openai.yaml` 增加一致性检查。
4. 补一份最小开发环境说明，解决依赖与运行问题。
5. 给每个教学主题加练习题和复盘问题。
6. 增加一个 eval harness 示例。
7. 增加一个 automation / safety gate 示例。

## 结论

这个项目下一步最重要的，不是继续扩文档体量，而是把三件事做深：

- 教学路径更完整
- 案例更真实
- harness 原型更落地

这样 `moyuan-skills` 才会从“方法论说明仓库”，继续长成“可学习、可验证、可演进的 skills 实验平台”。
