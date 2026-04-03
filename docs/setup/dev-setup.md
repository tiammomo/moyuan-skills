# 开发环境准备

这份文档面向仓库维护者和贡献者。

目标是统一本地解释器、依赖安装和联调入口，避免 `python`、`python3`、`.venv`、系统环境混用。

## 基础要求

- Python 3.11 或更新版本
- Node.js 18 或更新版本
- `uv`
- PowerShell 或 bash

如果系统里没有裸 `python` 命令，不要硬配别名；优先使用虚拟环境里的解释器或 `python3`。

## 推荐初始化

### 1. 创建虚拟环境

```text
uv venv .venv
```

### 2. 安装 Python 依赖

```text
uv pip install --python .venv/bin/python -r backend/requirements.txt -r backend/requirements-dev.txt
```

### 3. 安装前端依赖

```text
npm ci --prefix frontend
```

### 4. 约定解释器

bash:

```text
PATH="$(pwd)/.venv/bin:$PATH"
```

PowerShell:

```text
$env:PATH = "$PWD\.venv\Scripts;$env:PATH"
```

后续文档里的 `python ...`，都默认指向当前虚拟环境内的解释器。

如果你不想改 `PATH`，就直接显式使用：

- bash: `.venv/bin/python`
- PowerShell: `.venv\Scripts\python.exe`

## 第一轮建议验证

先跑这组最小命令：

```text
python scripts/check_progressive_skills.py
python scripts/check_docs_links.py
python scripts/skills_market.py smoke
python scripts/check_python_market_backend.py
```

如果你正在改作者链，再补：

```text
python scripts/skills_market.py scaffold-skill sample-skill --template market-ready --path dist/authoring-smoke
python scripts/skills_market.py doctor-skill dist/authoring-smoke/sample-skill
python scripts/skills_market.py validate dist/authoring-smoke/sample-skill/market/skill.json
```

## 前后端联调

启动 backend：

```text
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 38083
```

启动 frontend：

```text
SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083 npm run dev:local --prefix frontend
```

推荐端口：

- frontend: `33003`
- backend: `38083`

如果你要跑 Playwright：

```text
npm run build --prefix frontend
npm run e2e --prefix frontend
```

当前 Playwright 配置会优先使用仓库 `.venv` 里的 Python 启动 backend 和 registry fixture，但仍然要求先有前端 `.next` 构建产物。

## 常见问题

### 1. `python` 不存在

优先处理方式：

- 把 `.venv/bin` 或 `.venv\Scripts` 放进 `PATH`
- 或直接使用 `.venv/bin/python` / `.venv\Scripts\python.exe`

不要继续混用系统 `python3` 和虚拟环境依赖。

### 2. checker 通过，但你仍然不确定设计是否合理

这是正常现象。

checker 只负责结构和最小回归，不替代设计判断、权限审查和生命周期判断。

### 3. `rg` 不存在

仓库默认推荐 `rg`，但不是硬依赖。

PowerShell 可替代为：

```text
Get-ChildItem -Recurse -File | Select-String -Pattern "pattern"
```

## 建议工作顺序

1. 先改文档、模板或流程说明。
2. 再改脚手架、checker、schema 或后端接口。
3. 跑仓库级检查。
4. 最后跑前后端联调和端到端验证。
