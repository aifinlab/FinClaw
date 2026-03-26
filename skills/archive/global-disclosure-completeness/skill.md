---
name: global-disclosure-completeness
description: 用于披露完整性检查场景。适用于金融工作中的基础任务单元。
---

# Global Disclosure Completeness Check Skill

## Skill 名称
Global Disclosure Completeness Check

## 适用场景
基于**公网可查数据**，查询中国上市公司信息披露相关法律法规，并对**某个上市企业**已公开披露的定期报告（年报 / 半年报）进行**披露完整性校验**。

该 Skill 适合：
- 合规研究
- 证券法务/董办/内控预检查
- 上市公司信息披露研究
- 投资研究中的文本型披露完整性初筛

该 Skill **不替代**律师、会计师、保荐机构、交易所或监管机构的正式审核意见。

---

## 数据来源
本 Skill 使用**公网可查、公开访问**的数据源：

1. **中国证监会（CSRC）官网**
   - 《上市公司信息披露管理办法（证监会令第226号）》
   - 《公开发行证券的公司信息披露内容与格式准则第2号——年度报告的内容与格式》
   - 《公开发行证券的公司信息披露内容与格式准则第3号——半年度报告的内容与格式》

2. **上海证券交易所（SSE）官网**
   - 《上海证券交易所股票上市规则（2025年4月修订）》

3. **深圳证券交易所（SZSE）官网**
   - 《深圳证券交易所股票上市规则（2025年修订）》

4. **巨潮资讯（CNINFO）官网**
   - 上市公司公告检索
   - 定期报告 PDF 下载

### 规则来源说明
本 Skill 在 `script/disclosure_completeness_check.py` 中内置了法规来源元数据与报告检查清单，便于直接查询和校验。运行时会使用公开公告数据抓取公司最新对应定期报告，并基于公开披露文本进行章节/要素完整性检查。

---

## 功能
本 Skill 提供以下功能：

### 1. 法律法规查询
可查询内置的上市公司信息披露规则清单，包括：
- 监管规章
- 年报/半年报内容与格式准则
- 上市规则
- 官方公告平台

### 2. 上市公司披露文件获取
基于股票代码或“代码,简称”形式，从巨潮资讯检索对应上市公司的最新：
- 年度报告
- 半年度报告

并自动下载 PDF。

### 3. 披露完整性校验
对下载的定期报告做研究型完整性校验，当前支持：

#### 年报检查项示例
- 公司简介和主要财务指标
- 管理层讨论与分析
- 风险因素/风险提示
- 公司治理
- 控股股东及实际控制人
- 关联交易
- 利润分配/现金分红
- 审计报告/审计意见
- 财务报表
- 重大事项

#### 半年报检查项示例
- 公司简介和主要财务指标
- 管理层讨论与分析
- 风险因素/风险提示
- 重要事项
- 财务报表

### 4. 风险分级输出
输出字段包括：
- `completeness_score`：完整性得分
- `risk_level`：低 / 中 / 高
- `high_priority_gaps`：高优先级疑似缺失项
- `details`：逐项校验明细

### 5. JSON 结果导出
最终输出为 JSON，方便被其他系统、Agent 或分析流程继续调用。

---

## 目录结构
```text
global-disclosure-completeness-check/
├─ skill.md
└─ script/
   └─ disclosure_completeness_check.py
```

---

## 运行环境
建议 Python 3.10 及以上。

### 安装依赖
```bash
pip install requests pdfplumber
```

---

## 使用示例

### 示例 1：查询法规
```bash
python script/disclosure_completeness_check.py --query-laws
```

按关键词查询：
```bash
python script/disclosure_completeness_check.py --query-laws 信息披露
```

### 示例 2：校验某上市公司最新年报
```bash
python script/disclosure_completeness_check.py \
  --stock 000001,平安银行 \
  --report-type annual \
  --max-pages 80 \
  --output output/pingan_annual_check.json
```

### 示例 3：校验某上市公司最新半年报
```bash
python script/disclosure_completeness_check.py \
  --stock 600519,贵州茅台 \
  --report-type semiannual \
  --max-pages 60 \
  --output output/maotai_semiannual_check.json
```

### 示例输出摘要
```json
{
  "total_items": 10,
  "present_items": 8,
  "suspected_missing_items": 2,
  "completeness_score": 80.0,
  "risk_level": "medium"
}
```

---

## 交易说明
1. 本 Skill 面向**上市公司公开披露合规研究**，不是交易指令系统。
2. 本 Skill 的输出不能直接作为买卖依据，也不能代替法律意见、审计意见、持续督导意见或交易所审核结论。
3. “披露完整性校验”是基于**公开文本、章节关键词、规则清单**的研究型方法，适合作为：
   - 初筛
   - 内部复核前置检查
   - 风险提示辅助
4. 若公告 PDF 为扫描件、版式复杂、章节命名差异较大，可能出现：
   - 误报
   - 漏报
   - 章节识别不完整
5. 涉及重大投资、法律责任认定、监管沟通时，应由专业人士进行人工复核。

---

## 方法说明
当前实现采用“**规则清单 + 关键词/正则匹配**”方式：

1. 从公告平台获取上市公司最新定期报告；
2. 下载 PDF；
3. 提取文本；
4. 对照预置检查项检索对应章节或核心披露要素；
5. 形成完整性分数与风险等级。

### 当前局限
- 更偏向**存在性校验**，不等于内容真实、准确、充分；
- 对扫描 PDF 的识别能力有限；
- 对表格、脚注、图片型披露的识别能力有限；
- 不自动判断“披露是否实质充分”；
- 不自动处理行业特别规则、临时公告专项规则、债券/可转债/境外同步披露等复杂场景。

### 可扩展方向
后续可扩展：
- OCR 识别
- 按行业生成差异化检查清单
- 临时公告专项完整性校验
- 监管处罚案例映射
- LLM 语义审阅与规则联动
- 多家公司批量扫描

---

## License
MIT License

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
