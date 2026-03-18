---
name: global-disclosure-gap-analysis
description: 用于披露差距分析场景。适用于金融工作中的基础任务单元。
---

# 企业披露缺口分析 Skill

## 数据来源
- 中国证监会公开法规（上市公司信息披露管理办法等）
- 上交所、深交所公开上市规则及信息披露规则
- 巨潮资讯公开公告检索平台
- 用户本地下载的年报/半年报文本

## 功能
- 检索企业最新公开年报或半年报候选公告
- 按章节级规则清单对报告文本进行披露缺口分析
- 输出已覆盖章节、疑似缺失章节、完整性得分和复核说明
- 可作为上市公司公告/定期报告质量预检查工具

## 使用示例
先检索候选报告：
```bash
python script/disclosure_gap_analysis.py --company 贵州茅台 --report-type 年度报告
```

再对本地文本做缺口分析：
```bash
python script/disclosure_gap_analysis.py \
  --company 贵州茅台 \
  --report-type 年度报告 \
  --text-file ./reports/moutai_annual_report.txt
```

## 交易说明
- 本 Skill 提供的是章节级缺口检查，不替代律师、保荐机构、会计师或交易所审核意见。
- 结果适合做披露完整性预检查、问询准备和对标复核。
- 对重大遗漏、虚假记载、误导性陈述等认定，仍需逐条比照最新法规和原始公告。

## License
MIT
