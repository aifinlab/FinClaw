---
name: global-knowledge-chunking
description: 用于知识分块场景。适用于金融工作中的基础任务单元。
---

# Global Skill: 法律条文或公司报告的知识片段切分

## 数据来源
- 国家法律法规数据库（flk.npc.gov.cn）
- 中国证监会法规与规章（csrc.gov.cn）
- 上海证券交易所规则库（sse.com.cn）
- 深圳证券交易所规则库（szse.cn）
- 巨潮资讯公告与定期报告（cninfo.com.cn）
- 美国 SEC EDGAR 公司文件（sec.gov）

说明：本 Skill 只使用公网可查数据。优先采用国家机关、监管机构、交易所、上市公司公告平台与公司官网公开页面；如接入评论、趋势、流量等公开数据源，需在实际部署时确认目标站点 robots、服务条款与访问频率限制。

## 功能
- 将公开法律条文、规则条款、年报、审计报告等长文切分为适合检索与问答的知识片段。
- 抓取公开文档正文或链接的 PDF/HTML 文本
- 按条、章、节、标题、表格上下文进行规则化切分
- 支持滑动窗口切分与去重
- 输出 chunk_id、parent_doc_id、标题路径、正文、token 估算、页码/条号、URL、哈希
- 适合后续用于 RAG、法规问答、合规核查

## 使用示例
```bash
cd script
pip install -r requirements.txt
python script/run_demo.py --url "https://www.csrc.gov.cn/csrc/c101953/c7547359/content.shtml" --mode regulation
```

## 交易说明
本 Skill 不执行证券交易；“交易说明”仅说明其可服务于研究、合规、法务、审计场景，而非实时交易系统。

补充边界：
- 本 Skill 仅基于公开资料进行检索、抽取、规则分析或代理评分。
- 不构成法律意见、审计结论、信贷审批结论或任何证券投资建议。
- 对“客户分群/客户价值评估”类结果，应明确标注其为公开数据 proxy，而非企业内部真实经营明细。

## License
代码示例采用 MIT License；原始法规与公告文本版权归原发布机关或原披露主体。
