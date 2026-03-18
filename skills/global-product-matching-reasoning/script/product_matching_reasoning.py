
import argparse
import json
import math
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Iterable, Optional

import requests

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

from collections import Counter

def build_company_corpus(company: str, max_items: int = 30) -> List[Dict]:
    announcements = cninfo_search(company, page_size=max_items)
    corpus = []
    for item in announcements:
        title = item.get("announcementTitle", "")
        adjunct_url = item.get("adjunctUrl", "")
        sec_name = item.get("secName", "")
        date = item.get("announcementTime")
        corpus.append({
            "date": date,
            "source": "cninfo",
            "title": normalize_text(title),
            "company": sec_name,
            "url": f"https://static.cninfo.com.cn/{adjunct_url}" if adjunct_url else "",
            "text": normalize_text(title),
        })
    return corpus

def score_candidate(company_tokens: List[str], evidence_tokens: List[str], candidate_tokens: List[str]) -> float:
    jc1 = jaccard(company_tokens, candidate_tokens)
    jc2 = jaccard(evidence_tokens, candidate_tokens)
    cos = cosine_counter(Counter(evidence_tokens), Counter(candidate_tokens))
    return round(0.2 * jc1 + 0.45 * jc2 + 0.35 * cos, 4)

def infer_product_match(company: str, candidates: List[str], top_k: int = 5) -> Dict:
    corpus = build_company_corpus(company)
    company_tokens = tokenize(company)
    evidence_text = " ".join(x["title"] for x in corpus)
    evidence_tokens = tokenize(evidence_text)
    scored = []
    for candidate in candidates:
        ct = tokenize(candidate)
        score = score_candidate(company_tokens, evidence_tokens, ct)
        overlap = sorted(set(ct) & set(evidence_tokens))
        reasons = [f"公告关键词重合: {', '.join(overlap[:8])}"] if overlap else []
        if not reasons:
            reasons.append("仅发现弱语义相关，建议复核企业官网/年报产品表述")
        scored.append({
            "candidate_product": candidate,
            "match_score": score,
            "risk_level": "high" if score >= 0.65 else "medium" if score >= 0.35 else "low",
            "reasons": reasons,
        })
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return {
        "company": company,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "evidence_count": len(corpus),
        "top_matches": scored[:top_k],
        "evidence_titles": [x["title"] for x in corpus[:10]],
        "notes": [
            "这是基于公网公告标题与候选产品文本的推理分数，不等同于销售收入确认或正式产品目录匹配结论。",
            "建议结合企业官网、年报主营业务描述、招股书和产品手册二次核验。"
        ]
    }

def main():
    parser = argparse.ArgumentParser(description="企业产品匹配推理")
    parser.add_argument("--company", required=True)
    parser.add_argument("--candidates", required=True, nargs="+")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    print(format_result(infer_product_match(args.company, args.candidates, top_k=args.top_k)))

if __name__ == "__main__":
    main()
