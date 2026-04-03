# Skills Market 文档索引

`docs/` 现在按主题分目录维护，根目录只保留总索引。

## 当前状态

- 已完成：作者链 `scaffold -> doctor -> validate -> package -> provenance-check`
- 已完成：submission `build -> validate -> upload -> review -> ingest`
- 已完成：backend author API、`/studio`、remote registry browse CLI / backend API
- 进行中：前端 `/registries/*` 页面和远端 trust summary UI
- 待做：hosted publish auth、artifact store、review queue、publisher dashboard

## 推荐起点

1. [setup/dev-setup.md](./setup/dev-setup.md)
2. [market/market-spec.md](./market/market-spec.md)
3. [market/publisher-guide.md](./market/publisher-guide.md)
4. [integration/frontend-backend-integration.md](./integration/frontend-backend-integration.md)
5. [roadmap/market-pull-author-publish-plan.md](./roadmap/market-pull-author-publish-plan.md)

## 目录地图

- [setup/README.md](./setup/README.md)
  本地环境、联调入口、常用验证命令。
- [authoring/README.md](./authoring/README.md)
  skill 设计、脚手架、规范、模板与学习路径。
- [harness/README.md](./harness/README.md)
  progressive disclosure、harness engineering、runtime 与 prototype。
- [market/README.md](./market/README.md)
  market 规范、registry、governance、consumer / publisher 流程。
- [integration/README.md](./integration/README.md)
  前后端契约、页面映射、API 模式说明。
- [roadmap/README.md](./roadmap/README.md)
  主线 roadmap、按周排期和剩余 backlog。
- [skills/README.md](./skills/README.md)
  真实 skill 对应的中文说明与案例文档。
- [teaching/README.md](./teaching/README.md)
  中文课程总览、学习顺序和角色化路径。

## 文档治理

- 根目录不再堆放主题正文，正文优先进入对应子目录。
- 子目录 README 负责该主题的入口和阅读顺序。
- 会过期的临时说明不作为长期文档保留。
