---
name: global-product-knowledge-retrieval
description: 用于产品知识检索场景。适用于金融工作中的基础任务单元。
---

# global-product-knowledge-retrieval

## 数据来源
- 上市公司年报、半年报、招股说明书、募集说明书、公告等公开文件。
- 巨潮资讯、上交所、深交所等官方披露平台。
- 中国证监会及交易所规则文本中与产品合规、适配、信息披露相关的制度材料。
- 用户指定的公网链接或本地公开文件。

## 功能
- 针对“产品名称 / 技术路线 / 应用场景 / 客户群 / 收入结构 / 研发方向”等问题做检索。
- 从公司报告中抽取最相关片段，帮助形成产品知识卡片。
- 对公司报告和制度材料统一做文本切分与排序。
- 适合作为产品调研、投研辅助、售前知识检索的基础能力。

## 使用示例
```bash
python script/main.py   --source "https://static.cninfo.com.cn/finalpage/2025-04-19/1219876543.PDF"   --query "储能逆变器 应用场景 客户"
```

```bash
python script/main.py   --source "./samples/annual_report.pdf"   --query "核心产品 毛利率 研发投入"
```

## 交易说明
- 输入为单个公司报告、公告或公开制度文本。
- 输出为按相关度排序的片段集合，便于上层应用继续问答或摘要。
- 对于“产品知识”检索，最适合年报、招股书、业绩说明材料等文本。
- 本 skill 只做公开资料检索，不验证商业真实性，不构成投资建议。

## License
MIT License. See `LICENSE`.
