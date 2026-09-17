# Paper Macros 数字单一真相源

## 何时读取

在 S6 开始写作前读取；生成或校验 `paper_macros.json` 时同时参考
[paper_macros.schema.json](paper_macros.schema.json)。

## 推荐格式

```json
{
  "schema_version": "1.0",
  "metadata": {
    "run_id": "cumcm-2026-a-001",
    "contest": "CUMCM",
    "problem_id": "A",
    "source_manifest": "pipeline_manifest.json"
  },
  "macros": {
    "data": {
      "valid_records": {
        "value": 878042,
        "unit": "条",
        "source": "results/preprocessing_report.json#/valid_records",
        "precision": 0,
        "formats": ["878,042"]
      }
    },
    "validation": {
      "r2": {
        "value": 0.9431,
        "unit": "dimensionless",
        "source": "results/validation_metrics.json#/r2",
        "precision": 3,
        "formats": ["0.943"]
      },
      "relative_error": {
        "value": 0.067,
        "unit": "ratio",
        "source": "results/validation_metrics.json#/relative_error",
        "formats": ["6.7%"]
      }
    }
  },
  "allowlist": {
    "years": [2026],
    "values": [2, 3.141592653589793],
    "tokens": ["1e-8"]
  }
}
```

## 规则

- 每个宏必须有 `value` 和非空 `source`。
- `source` 指向可复算的文件和字段，不写“人工填写”“来自记忆”。
- 论文采用的舍入形式写入 `formats`；原始精度仍保留在 `value`。
- 比率若以百分数展示，将百分数字符串写入 `formats`，避免歧义。
- 章节号、公式号、图表号和引用号由校验器识别为结构数字。
- 年份、固定数学常数、超参数或法定阈值必须显式进入 `allowlist` 或宏，不使用隐式全局白名单。
- 旧版纯键值 JSON 仍可读取，但严格工作流应迁移到 schema 1.0。

## 命令

```powershell
python scripts/paper_number_validator.py `
  --paper paper.md `
  --macros results/paper_macros.json `
  --report results/paper_number_report.json
```

仅检查宏文件：

```powershell
python scripts/paper_number_validator.py `
  --macros results/paper_macros.json `
  --validate-macros-only
```

