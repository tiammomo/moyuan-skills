# Lint Fixtures

这里放的是“反模式示例”，不是可触发 skill。

这些文件的用途有两类：

- 帮维护者快速看到仓库刻意避免的坏结构
- 给未来更细粒度的 lint 或 fixture 测试留标准样本

## 当前包含的反模式

- `bad-router.md`
  一条 router 同时挂太多参考入口。
- `bad-setup-heading.md`
  把触发语义或安装说明塞回 skill 正文。
- `bad-openai.yaml`
  UI 元数据和 skill 标题、默认 prompt 不一致。
