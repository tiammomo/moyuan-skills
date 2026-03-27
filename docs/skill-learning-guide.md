# Skills Market 学习指南

这份指南的目标，是把“skill 设计逻辑”一路串到“skills market 运行逻辑”。

如果你已经知道怎么写 prompt，但还不知道为什么这个仓库会继续演进到 package、registry、client lifecycle、governance 和 frontend delivery，那么这份指南就是给你准备的。

## 先建立一个统一心智模型

这个项目可以按五层来看：

1. `skill design`
   先回答 trigger、router、progressive loading 和 default workflow。
2. `harness`
   再回答 tool contract、state、eval、safety、automation。
3. `market packaging`
   再把 skill 变成可验证、可打包、可安装的 capability artifact。
4. `client lifecycle`
   再解决 install、bundle、doctor、snapshot、baseline、waiver 和 gate。
5. `product delivery`
   最后让 frontend、backend 和 HTML 交付层能稳定消费这些能力。

## 推荐学习顺序

### 第一阶段：先学 skill 设计逻辑

1. [teaching/README.md](./teaching/README.md)
2. [teaching/01-learning-map.md](./teaching/01-learning-map.md)
3. [teaching/03-build-your-first-skill.md](./teaching/03-build-your-first-skill.md)
4. [skill-quickstart.md](./skill-quickstart.md)
5. [skill-authoring.md](./skill-authoring.md)
6. [progressive-disclosure.md](./progressive-disclosure.md)

这一阶段的目标不是先做 market，而是先搞清楚一个“可维护的 skill”长什么样。

### 第二阶段：再理解 harness 和 eval

1. [harness-engineering.md](./harness-engineering.md)
2. [teaching/05-harness-roadmap.md](./teaching/05-harness-roadmap.md)
3. [teaching/08-evals-and-prototypes.md](./teaching/08-evals-and-prototypes.md)
4. [harness-prototypes.md](./harness-prototypes.md)
5. [harness-runtime.md](./harness-runtime.md)

这一阶段的目标，是理解为什么 skill 不是系统的全部，真正稳定运行还需要 harness。

### 第三阶段：进入 skills market

1. [teaching/16-skills-market-evolution.md](./teaching/16-skills-market-evolution.md)
2. [teaching/17-market-registry-and-federation.md](./teaching/17-market-registry-and-federation.md)
3. [teaching/18-skills-market-learning-map.md](./teaching/18-skills-market-learning-map.md)
4. [teaching/19-market-packaging-and-publishing.md](./teaching/19-market-packaging-and-publishing.md)
5. [market-spec.md](./market-spec.md)
6. [market-registry.md](./market-registry.md)

这一阶段的目标，是把 skill 看成可发布的能力包，而不是一份静态文档。

### 第四阶段：理解 client、治理与交付

1. [teaching/20-market-client-operations.md](./teaching/20-market-client-operations.md)
2. [teaching/21-market-governance-and-delivery.md](./teaching/21-market-governance-and-delivery.md)
3. [consumer-guide.md](./consumer-guide.md)
4. [market-governance.md](./market-governance.md)
5. [frontend-backend-integration.md](./frontend-backend-integration.md)

这一阶段的目标，是看懂本地 client state、waiver/gate、前后端联调为什么也是 skills market 的一部分。

## 按角色进入

- 只想先学会写 skill：
  看 [teaching/10-learner-path.md](./teaching/10-learner-path.md) 和 [teaching/11-skill-author-path.md](./teaching/11-skill-author-path.md)。
- 想维护整个仓库：
  看 [teaching/12-maintainer-path.md](./teaching/12-maintainer-path.md)。
- 想研究 harness 和系统层：
  看 [teaching/13-harness-builder-path.md](./teaching/13-harness-builder-path.md)。
- 想从项目 owner 视角理解 skills market：
  从 [teaching/18-skills-market-learning-map.md](./teaching/18-skills-market-learning-map.md) 开始。

## 最小实践路径

如果你想边学边确认仓库真的能跑，最小命令链路是：

```text
python scripts/check_progressive_skills.py
python scripts/skills_market.py smoke
python scripts/check_python_market_backend.py
npm run e2e --prefix frontend
```

这四条命令分别对应：

- skill 结构是否完整
- market pipeline 是否连通
- Python backend 是否能正确聚合仓库数据
- frontend 是否能真实消费 backend 数据

## 学完这份指南后你应该能回答

- skill 设计逻辑为什么会自然延伸到 skills market
- market manifest、install spec、bundle 和 provenance 为什么不是“附加物”
- client lifecycle 和 governance 为什么必须进入教学内容
- 为什么 `docs/teaching/` 要专门承担整个 skills market 的课程化入口
