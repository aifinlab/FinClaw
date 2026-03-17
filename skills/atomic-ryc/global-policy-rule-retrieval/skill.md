---
name: global-policy-rule-retrieval
description: 用于政策规则检索场景。适用于金融工作中的基础任务单元。
---

# global-policy-rule-retrieval

## 数据来源
- 国家法律法规数据库中的公开法律、行政法规、司法解释、部门规章。
- 中国证监会公开规则、章程指引、股东会规则、治理准则、信息披露制度。
- 上交所、深交所公开的规范运作、自律监管、公告格式等规则。
- 上市公司章程、治理制度、审议规则、内控制度等公开文件。

## 功能
- 对制度规则进行检索，定位最相关条文和程序性要求。
- 适合查询“谁审批、谁负责、是否必须披露、是否需要回避、流程是什么”等问题。
- 支持法律文本和公司制度文本统一检索。
- 输出片段中尽量保留条号线索，方便二次核对。

## 使用示例
```bash
python script/main.py   --source "https://flk.npc.gov.cn/detail?id=..."   --query "董事会 对外担保 审批程序"
```

```bash
python script/main.py   --source "./samples/governance_rules.pdf"   --query "关联交易 回避 审议"
```

## 交易说明
- 推荐优先输入官方规则文本或上市公司正式披露制度文件。
- 输出结果是检索命中，不等同于正式法律解释。
- 可作为制度库检索、制度问答和冲突校验的底层能力。
- 本 skill 不替代律师、合规、审计或交易所正式意见。

## License
MIT License. See `LICENSE`.
