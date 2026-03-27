# Market Packaging And Publishing

这篇文档专门讲“一个 skill 怎样变成 market-ready capability”。

## 你要掌握的对象

1. `market manifest`
2. `install spec`
3. `package artifact`
4. `provenance`
5. `channel index`

## 在仓库里分别看哪里

- `skills/*/market/skill.json`
- [../market-spec.md](../market-spec.md)
- [../publisher-guide.md](../publisher-guide.md)
- [../../scripts/validate_market_manifest.py](../../scripts/validate_market_manifest.py)
- [../../scripts/package_skill.py](../../scripts/package_skill.py)
- [../../scripts/build_market_index.py](../../scripts/build_market_index.py)
- [../../scripts/verify_market_provenance.py](../../scripts/verify_market_provenance.py)

## 推荐实践顺序

1. 先读一个业务 skill 的 `market/skill.json`
2. 对照 [../market-spec.md](../market-spec.md) 看 manifest 字段含义
3. 跑 `validate`
4. 跑 `package`
5. 跑 `index`
6. 跑 `provenance-check`

## 最小命令链路

```text
python scripts/validate_market_manifest.py
python scripts/package_skill.py release-note-writer
python scripts/build_market_index.py
python scripts/skills_market.py provenance-check dist/market/install/release-note-writer-0.1.0.json
```

## 这一步真正要学会什么

- skill 不是只靠 `SKILL.md` 被消费
- 可分发能力必须有明确的 metadata、install contract 和 provenance
- 发布链路的重点不是“把文件打出来”，而是把验证、追踪和后续安装入口一起打出来

## 学完后下一步看什么

- client 消费侧：看 [20-market-client-operations.md](./20-market-client-operations.md)
- registry 与聚合侧：看 [17-market-registry-and-federation.md](./17-market-registry-and-federation.md)
