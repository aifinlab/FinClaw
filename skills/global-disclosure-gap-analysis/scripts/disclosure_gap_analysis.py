
from collections import Counter
from datetime import datetime
from typing import Dict, List, Iterable, Optional
import argparse
import json
import math
import re

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

REQUIRED_SECTIONS = {
    "年度报告": ["重要提示", "公司简介和主要财务指标", "管理层讨论与分析", "公司治理", "环境和社会责任", "重要事项", "股份变动及股东情况", "财务报告"],
    "半年度报告": ["重要提示", "公司简介和主要财务指标", "管理层讨论与分析", "公司治理", "重要事项", "股份变动及股东情况", "财务报告"]
}

def analyze_gap(text: str, report_type: str) -> Dict:
    report_type = report_type if report_type in REQUIRED_SECTIONS else "年度报告"
    missing, present = [], []
    for item in REQUIRED_SECTIONS[report_type]:
        if item in text:
            present.append(item)
        else:
            missing.append(item)
    score = round(100 * len(present) / len(REQUIRED_SECTIONS[report_type]), 2)
    return {"report_type": report_type, "present": present, "missing": missing, "score": score}

def extract_latest_report_titles(company: str, report_keyword: str = "年度报告") -> List[Dict]:
    rows = cninfo_search(f"{company} {report_keyword}", page_size=20)
    out = []
    for item in rows:
        title = normalize_text(item.get("announcementTitle", ""))
        if report_keyword in title:
            out.append({"title": title, "url": f"https://static.cninfo.com.cn/{item.get('adjunctUrl', '')}" if item.get("adjunctUrl") else ""})
    return out

def main():
    parser = argparse.ArgumentParser(description="企业披露缺口分析")
    parser.add_argument("--company", required=True)
    parser.add_argument("--report-type", default="年度报告", choices=["年度报告", "半年度报告"])
    parser.add_argument("--text-file")
    args = parser.parse_args()
    result = {
        "company": args.company,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "candidate_reports": extract_latest_report_titles(args.company, args.report_type),
    }
    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as f:
            text = f.read()
        result["gap_analysis"] = analyze_gap(text, args.report_type)
        result["notes"] = [
            "该分析以公开规则中的章节级要求为主，未覆盖全部细项披露口径。",
            "若需法律意见级别结论，应结合最新规则条款、交易所问询历史和审计事项逐项复核。"
        ]
    print(format_result(result))

if __name__ == "__main__":
    main()
