# 开发环境准备

这份文档面向这个仓库的维护者和贡献者。

目标是让你能在本地稳定跑通：

- 仓库级 lint
- skill-local checker
- 最小 eval harness 示例

## 基础要求

建议环境：

- Python 3.11 或更新版本
- PowerShell、bash 或任意能运行 Python 命令的终端

当前仓库自带的检查脚本都只依赖 Python 标准库。

如果你还想运行外部 skill-creator 里的 `quick_validate.py`，或者希望本地依赖和仓库文档保持一致，建议安装 `requirements-dev.txt` 里的依赖。

## 推荐初始化步骤

在仓库根目录执行：

```text
python -m venv .venv
```

激活虚拟环境：

PowerShell:

```text
.venv\Scripts\Activate.ps1
```

bash:

```text
source .venv/bin/activate
```

如果你需要跑额外的 YAML 相关工具，再安装：

```text
python -m pip install -r requirements-dev.txt
```

## 第一轮建议跑什么

推荐进入仓库后先跑：

```text
python scripts/check_progressive_skills.py
python scripts/check_docs_links.py
python scripts/check_harness_prototypes.py
python skills/build-skills/scripts/check_build_skills.py
python skills/progressive-disclosure/scripts/check_progressive_disclosure.py
python skills/harness-engineering/scripts/check_harness_engineering.py
python skills/release-note-writer/scripts/check_release_note_writer.py
python skills/issue-triage-report/scripts/check_issue_triage_report.py
python skills/incident-postmortem-writer/scripts/check_incident_postmortem_writer.py
python skills/api-change-risk-review/scripts/check_api_change_risk_review.py
python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json
python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml
```

这样可以同时确认：

- skill 结构没坏
- 教学型 skill 资源没丢
- 业务 skill 主链路可用
- eval 示例可运行，而且能和 baseline 做回归比较
- harness 原型资产已经有 schema、checker、stub 和最小 runtime，可继续被接到更大的系统设计里

## 常见问题

### 1. `quick_validate.py` 报缺少 `yaml`

原因：

- 当前环境没有安装 `PyYAML`

处理方式：

- `python -m pip install pyyaml`

### 2. `rg` 在当前环境不可用

仓库默认推荐 `rg`，但不是强依赖。

在 PowerShell 里可以用：

```text
Get-ChildItem -Recurse -File | Select-String -Pattern "pattern"
```

### 3. checker 通过，但你仍然不确定改动是否合理

这很正常。

仓库 checker 主要保障结构和样例链路，不替代人工设计判断。

## 开发者建议

推荐把修改顺序固定成：

1. 先改文档或 skill
2. 再改 checker / lint
3. 再跑仓库级检查
4. 最后跑 skill-local checker 和 eval 示例

这样更容易定位问题是“设计变更”还是“检查逻辑变更”。

