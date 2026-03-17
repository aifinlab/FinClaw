---
name: global-reporting-caliber
description: 用于报告口径场景。适用于金融工作中的基础任务单元。
---

# Global Skill: Listed Company Reporting Caliber Validator

## Skill 名称
上市企业报送口径校验（Listed Company Reporting Caliber Validator）

## 数据来源
本 Skill 仅使用公网可查、优先官方来源的数据，默认数据源包括：

1. **国家法律法规数据库**：用于检索法律、行政法规、监察法规、司法解释等上位规则。
2. **中国证监会证券期货法规数据库**：用于检索证券期货规章、规范性文件、信息披露准则、披露内容与格式要求。
3. **上海证券交易所规则与指南**：用于检索主板/科创板股票上市规则、自律监管指南、公告格式及业务办理规则。
4. **深圳证券交易所规则与指南**：用于检索主板/创业板股票上市规则、公告格式、业务办理规则。
5. **巨潮资讯**：用于检索上市公司公告、年报、临时公告、董事会/股东大会公告、关联交易公告、会计政策变更公告等公开披露文件。

> 说明：本 Skill 采取“**法规规则 + 交易所口径 + 上市公司已披露公告**”三层交叉校验思路。默认不依赖付费数据库，不依赖登录态。

## 功能
本 Skill 面向“某个上市企业是否按适当报送口径披露”的场景，提供以下能力：

### 1. 法规与规则索引输出
输出当前 Skill 内置的公开数据源清单和规则目录，便于扩展内部规则库。

### 2. 上市企业公告检索
通过公开可访问的巨潮资讯检索接口，按公司名称、证券代码、关键字拉取公告标题与链接，作为规则引擎的输入材料。

### 3. 报送口径校验
对公告文本或标题摘要做启发式规则校验，重点覆盖：
- 定期报告口径一致性
- 关联交易报送口径
- 重大交易报送口径
- 募集资金使用报送口径
- 会计政策/会计估计变更口径

### 4. 结果输出
输出：
- 总体口径风险分数
- 每条规则的 `pass / review / alert` 结论
- 已命中字段
- 缺失字段
- 解释说明
- 公开来源清单与公告链接

## 文件结构
```text
global-listed-company-reporting-caliber-validator/
├── skill.md
├── LICENSE
├── requirements.txt
└── script/
    ├── rule_catalog.py
    ├── public_sources.py
    ├── rules_engine.py
    ├── company_validator.py
    ├── fetch_rules_index.py
    └── example_run.py
```

## 使用示例

### 1）安装依赖
```bash
pip install -r requirements.txt
```

### 2）查看内置规则目录与公开数据源
```bash
python script/fetch_rules_index.py
```

### 3）对某家上市公司做“关联交易”报送口径校验
```bash
python script/company_validator.py \
  --company "贵州茅台" \
  --code "600519" \
  --keyword "关联交易" \
  --limit 5
```

### 4）将结果输出到 JSON 文件
```bash
python script/company_validator.py \
  --company "宁德时代" \
  --code "300750" \
  --keyword "会计政策变更" \
  --limit 5 \
  --output result.json
```

### 5）最小演示
```bash
python script/example_run.py
```

## 交易说明
1. 本 Skill 的目标是 **监管口径/报送口径核查辅助**，不是投资建议系统。
2. 输出的 `risk_score` 与 `pass/review/alert` 为 **启发式规则结果**，不能直接替代律师、会计师、董办、证券事务代表或信披专员的专业判断。
3. 若将本 Skill 用于二级市场研究、风控或事件驱动策略，请注意：
   - 公告发布时间与规则生效时间可能存在差异；
   - 不同板块（上交所主板、科创板、深交所主板、创业板）适用规则可能不同；
   - 同一事项可能同时涉及法律、证监会规章、交易所规则、公告格式指南和公司章程；
   - 重大交易、关联交易、募集资金、财务口径等事项往往需要结合附件、审计/评估报告、法律意见书进行复核。
4. 任何交易决策应独立评估信息时效性、完整性与适用范围。

## 可扩展方向
- 接入更细颗粒度的条款解析器
- 对 PDF/HTML 公告正文做结构化抽取
- 对不同交易所板块分别配置规则集
- 增加时间生效性校验（规则生效日/废止日）
- 增加企业自定义口径模板与内部报送制度映射

## License
本 Skill 代码采用 **MIT License**。

### 第三方来源说明
- Skill 代码本身按 MIT License 发布。
- 公网数据来源的版权、使用条件和公开访问政策分别以各官方网站声明为准。
- 使用者应遵守目标网站 Robots、服务条款、版权声明及适用法律法规。
