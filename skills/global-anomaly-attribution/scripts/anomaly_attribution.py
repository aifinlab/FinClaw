
from collections import Counter
from collections import Counter
from datetime import datetime
from typing import Dict, List, Iterable, Optional
import argparse
import json
import math

import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; OpenAI Skill Demo/1.0)"
}

STOPWORDS = {
    "股份有限公司", "有限公司", "公司", "产品", "业务", "系统", "项目", "方案", "平台",
    "the", "and", "for", "with", "of", "to", "a", "an"
}

def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize(text: str) -> List[str]:
    text = normalize_text(text)
    tokens = re.findall(r"[A-Za-z0-9\-\+\.]+|[\u4e00-\u9fff]{2,}", text)
    return [t.lower() for t in tokens if t.lower() not in STOPWORDS]

def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

def cosine_counter(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    num = sum(a[k] * b[k] for k in common)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)

def fetch_json(url: str, method: str = "GET", params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
    resp = requests.request(method, url, params=params, data=data, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.json()

def cninfo_search(keyword: str, page_num: int = 1, page_size: int = 20) -> List[Dict]:
    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
    data = {
        "pageNum": page_num,
        "pageSize": page_size,
        "tabName": "fulltext",
        "column": "szse",
        "plate": "",
        "stock": "",
        "searchkey": keyword,
        "secid": "",
        "category": "",
        "trade": "",
        "seDate": "",
        "sortName": "nothing",
        "sortType": "desc",
        "isHLtitle": "true",
    }
    payload = fetch_json(url, method="POST", data=data)
    return payload.get("announcements", []) or []

def format_result(result: Dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)

import requests

ANOMALY_PATTERNS = {
    "业绩波动": ["亏损", "预减", "预亏", "大幅下降", "减值", "商誉", "业绩预告修正"],
    "监管合规": ["问询函", "监管函", "立案", "行政处罚", "纪律处分", "警示函"],
    "治理变动": ["辞职", "变更", "实控人", "控制权", "董事会", "监事会"],
    "融资压力": ["质押", "冻结", "违约", "展期", "回售", "募资", "补流"],
    "诉讼仲裁": ["诉讼", "仲裁", "执行", "被告", "原告"],
    "经营事件": ["停产", "火灾", "事故", "召回", "停牌", "复牌", "重大合同"]
}

def attribute_anomaly(company: str, anomaly_text: str, max_items: int = 30) -> Dict:
    announcements = cninfo_search(company, page_size=max_items)
    anomaly_tokens = tokenize(anomaly_text)
    buckets = []
    for item in announcements:
        title = normalize_text(item.get("announcementTitle", ""))
        title_tokens = tokenize(title)
        base = jaccard(anomaly_tokens, title_tokens)
        hit_tags = [tag for tag, kws in ANOMALY_PATTERNS.items() if any(kw.lower() in title.lower() for kw in kws)]
        score = base + 0.15 * len(hit_tags)
        if score > 0:
            buckets.append({
                "title": title,
                "score": round(score, 4),
                "tags": hit_tags,
                "url": f"https://static.cninfo.com.cn/{item.get('adjunctUrl', '')}" if item.get("adjunctUrl") else ""
            })
    buckets.sort(key=lambda x: x["score"], reverse=True)
    counter = Counter()
    for b in buckets[:15]:
        for t in b["tags"]:
            counter[t] += 1
    primary = [{"factor": tag, "support_count": cnt, "confidence": "high" if cnt >= 3 else "medium" if cnt == 2 else "low"} for tag, cnt in counter.most_common(5)]
    return {
        "company": company,
        "anomaly_input": anomaly_text,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "primary_attribution": primary or [{"factor": "未识别出高置信归因", "support_count": 0, "confidence": "low"}],
        "supporting_evidence": buckets[:10],
        "notes": [
            "归因基于公开公告标题和关键词，不代表因果关系已被法律或审计程序确认。",
            "建议叠加股价成交异动、财务指标、行业新闻和监管文书进一步复核。"
        ]
    }

def main():
    parser = argparse.ArgumentParser(description="企业异常归因")
    parser.add_argument("--company", required=True)
    parser.add_argument("--anomaly", required=True)
    parser.add_argument("--max-items", type=int, default=30)
    args = parser.parse_args()
    print(format_result(attribute_anomaly(args.company, args.anomaly, max_items=args.max_items)))

if __name__ == "__main__":
    main()
