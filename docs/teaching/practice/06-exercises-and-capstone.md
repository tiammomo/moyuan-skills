# 练习题与 Capstone

这份文档用来把教学目录从“阅读路径”推进到“实践路径”。

如果前面的文档回答的是“应该怎么理解这个项目”，这份文档回答的是：

- 学完之后该怎么练

## 练习一：写一个最小 Skill

目标：

- 完成一个最小可用 skill 的设计草稿

要求：

- 给 skill 起一个窄且清晰的名字
- 写出一条包含 `Use when ...` 的 `description`
- 写出 `Task Router`
- 写出 `Progressive Loading`
- 判断是否需要 `references/`、`scripts/`、`assets/`

验收标准：

- skill 的触发足够清楚
- `SKILL.md` 仍然短小
- 路由比背景说明更突出

## 练习二：重构一个臃肿 Skill

目标：

- 把一个已经过长的 skill 重新拆层

要求：

- 标出哪些内容属于 trigger、router、topic detail、script、asset
- 把长说明迁移到 `references/`
- 把重复执行逻辑迁移到 `scripts/`
- 补一份 refactor plan

验收标准：

- 路由更清楚
- reference 可达性更好
- skill 本体明显变轻

## 练习三：判断 Skill 与 Harness 的边界

目标：

- 练习识别“哪些东西不该继续留在 skill 里”

要求：

- 选择一个你熟悉的 skill
- 写出其中的 trigger、tool、state、eval、safety、automation 要素
- 判断哪些仍属于 skill
- 判断哪些应该逐步上移到 harness

验收标准：

- 边界判断有清晰理由
- 不是把所有复杂度都继续塞回 `SKILL.md`

## Capstone：从 0 到 1 设计一个可演进的 Skill 项目

这个 capstone 建议把整个仓库的三条主线串起来。

### 任务

请完成一个完整方案，内容包括：

1. 一个 skill 主题
2. 一份 skill design canvas
3. 一份最小 `SKILL.md` 草稿
4. 一份渐进式拆层方案
5. 一份最小 checker 方案
6. 一份未来 harness 演进草图

### 推荐输出结构

- 项目目标
- 用户原话样例
- skill 命名与 `description`
- router 设计
- resource 设计
- validation 设计
- harness roadmap

### 推荐搭配资料

- [03-build-your-first-skill.md](../foundations/03-build-your-first-skill.md)
- [04-progressive-disclosure-workshop.md](../foundations/04-progressive-disclosure-workshop.md)
- [05-harness-roadmap.md](../foundations/05-harness-roadmap.md)
- [../../skills/build-skills/assets/skill-design-canvas.md](../../../skills/build-skills/assets/skill-design-canvas.md)
- [../../skills/progressive-disclosure/assets/loading-plan-template.md](../../../skills/progressive-disclosure/assets/loading-plan-template.md)
- [../../skills/harness-engineering/assets/harness-blueprint.md](../../../skills/harness-engineering/assets/harness-blueprint.md)

## 建议的学习节奏

如果按 workshop 方式推进，推荐这样安排：

1. 第 1 天：完成最小 skill 草稿
2. 第 2 天：完成渐进式拆层
3. 第 3 天：完成 checker 设计和 harness 草图

## 完成后的能力目标

做完这些练习后，应该至少能做到：

- 自己做一个最小可用 skill
- 自己重构一个臃肿 skill
- 自己判断 skill 与 harness 的边界

