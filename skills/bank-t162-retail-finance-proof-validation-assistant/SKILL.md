---
name: bank-t162-retail-finance-proof-validation-assistant
description: "用于银行零售金融场景的材料/证明核验，当需要检查完整性、一致性、真实性红旗并输出补件与复核建议时触发。"
---

# 收入与经营证明核验助手

## 这个 skill 是做什么的
对收入证明、经营证明、流水、合同/发票等材料进行结构化核验，输出完整性检查、跨材料一致性检查、异常红旗提示和补件/复核建议。输出用于支持贷前审查与运营复核，不直接给出“真伪定论”。

## 适用范围
- 经营贷/消费贷材料核验、收入与经营证明核验
- 客户经理、零售运营、贷前审核辅助团队
- 需形成可执行的补件清单、异常项与升级建议

## 何时使用
- 需要对材料完整性、字段一致性、规则符合性做检查时
- 需要将核验发现整理成结构化报告时

## 何时不要使用
- 需要伪造材料或绕过核验规则时
- 未提供任何原始材料或可核验字段时

## 默认工作流
1. 明确核验对象与规则口径（必需材料、字段定义、有效期）
2. 完整性校验（材料/字段缺失）
3. 一致性校验（跨材料字段对齐，如姓名、金额、日期）
4. 真实性红旗识别（异常时间、逻辑冲突、明显篡改迹象）
5. 输出核验结论摘要、补件与复核建议

## 输入要求
- 材料清单（材料类型、来源、时间、字段）
- 核验规则与口径（必需材料、字段一致性规则、有效期要求）
- 业务场景与时间窗口
- 如涉及影像件：必须提供结构化字段或OCR结果

## 输出要求
- 材料完整性结论与缺失清单
- 跨材料一致性异常清单
- 真实性红旗提示与优先级
- 补件清单与复核/升级建议
- 明确“待人工确认”的事项

## 风险与边界
- 不能把自动核验结果等同于最终真伪认定
- 涉嫌伪造、欺诈线索时需建议人工复核/升级
- 不得输出超出材料范围的事实

## 信息不足时的处理
- 明确缺失材料与关键字段
- 输出可继续推进的最小核验建议
- 对关键规则缺失标注[待确认]

## 配套脚本
- `scripts/proof_validation.py`：读取材料清单与核验规则，输出缺失项、一致性异常与红旗提示。

### 脚本使用
```bash
python scripts/proof_validation.py --input documents.json --rules rules.json --output out.json
```

### documents.json 示例结构
```json
{
  "documents": [
    {
      "doc_type": "income_proof",
      "issue_date": "2025-12-01",
      "fields": {
        "name": "张三",
        "id_no": "110101********1234",
        "monthly_income": 20000
      }
    },
    {
      "doc_type": "bank_statement",
      "issue_date": "2025-12-15",
      "fields": {
        "name": "张三",
        "monthly_income": 21000
      }
    }
  ]
}
```

### rules.json 示例结构
```json
{
  "required_docs": ["income_proof", "bank_statement"],
  "field_matches": [
    {"field": "name", "doc_types": ["income_proof", "bank_statement"]}
  ],
  "valid_days": {
    "income_proof": 90
  }
}
```

### out.json 输出要点
- `missing_docs`：缺失材料
- `missing_fields`：缺失字段
- `inconsistencies`：跨材料不一致项
- `red_flags`：真实性红旗（如日期异常、逻辑冲突）
- `next_steps`：补件与复核建议

## 交付标准
- 结论可追溯到具体材料与字段
- 能直接用于补件与复核推进
