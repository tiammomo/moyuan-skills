# Skills Market 演进课

这篇内容专门回答一个问题：

当 `moyuan-skills` 不再只是一个教学型 skills 仓库，而是已经开始具备 market 分发能力时，我们应该怎么理解它的演进。

## 学习目标

读完后，你应该能说清楚：

- 为什么 market 不是“再多放几个 skill”
- 为什么 skill 要从内容包演进成可发布能力包
- 为什么 manifest、install spec、provenance、bundle、registry 会变成基础设施
- 为什么 teaching、checker、eval 和 runtime 仍然要保留

## 先用四层模型看项目

理解这条演进线，最稳的方式不是先看网站，而是先看四层：

1. `source repo`
   skill source、docs、checker、eval、templates
2. `package pipeline`
   package、install spec、provenance
3. `registry / market`
   index、catalog、recommendation、federation feed
4. `consumer / installer`
   search、install、org/private curated market

当前仓库已经覆盖了这四层的最小可运行版本。

## 现在已经有哪些 market 前置能力

当前仓库里已经有：

- `skills/*/market/skill.json`
- `publishers/*.json`
- `governance/orgs/*.json`
- `bundles/*.json`
- package / install / provenance 脚本
- catalog / recommendation / federation / registry 脚本
- 一个完整 smoke pipeline

也就是说，项目已经不是“只有规划”，而是已经有可验证的分发闭环。

## 为什么 teaching 仍然重要

market 解决的是“怎么发现、怎么安装、怎么治理”，但 teaching 解决的是：

- skill 为什么这么设计
- 内容为什么要分层
- 哪些能力应该留在 skill 里
- 哪些能力应该上移到 harness

如果没有 teaching，market 只会把越来越多难维护的 skill 分发出去。

## 当前最值得理解的 3 个升级点

### 1. 安装链不再只有 package

现在真正的安装链是：

```text
manifest -> package -> provenance -> install spec -> install verify
```

### 2. market 不再只有 catalog

现在 public / org market 都已经有：

- index
- static catalog
- recommendations
- federation feed

### 3. private market 不是单独一套系统

当前 org/private market 不是重新造一套结构，而是沿用同一套：

- manifest
- org policy
- bundle
- catalog
- federation feed

只是多了一层 allowlist / lifecycle / verified publisher 过滤。

## 推荐阅读顺序

1. [09-project-learning-roadmap.md](./09-project-learning-roadmap.md)
2. [08-evals-and-prototypes.md](./08-evals-and-prototypes.md)
3. [../market-spec.md](../market-spec.md)
4. [../market-governance.md](../market-governance.md)
5. [../market-registry.md](../market-registry.md)
6. [../publisher-guide.md](../publisher-guide.md)
7. [../consumer-guide.md](../consumer-guide.md)
8. [17-market-registry-and-federation.md](./17-market-registry-and-federation.md)

## 学完后下一步看什么

- 想继续从项目全貌进入：看 [../../README.md](../../README.md)
- 想从作者视角继续：看 [11-skill-author-path.md](./11-skill-author-path.md)
- 想从维护者视角继续：看 [12-maintainer-path.md](./12-maintainer-path.md)
- 想直接学分发层：看 [17-market-registry-and-federation.md](./17-market-registry-and-federation.md)
