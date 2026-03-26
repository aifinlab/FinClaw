
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
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
)
# ====================================

SCENARIO_RULES = {
    "扩产/投资": ["扩产", "项目", "投建", "产能", "基地", "募投"],
    "融资/资本运作": ["定增", "可转债", "配股", "回购", "并购", "重大资产重组"],
    "经营承压": ["亏损", "预亏", "减值", "下滑", "停产", "订单减少"],
    "监管/合规": ["问询函", "监管函", "立案", "处罚", "警示函"],
    "治理变动": ["辞职", "选举", "董事长", "总经理", "控制权", "实控人"],
    "诉讼/纠纷": ["诉讼", "仲裁", "冻结", "执行", "纠纷"],
    "产品/技术进展": ["新品", "认证", "中标", "合作", "发布", "试产"]
}

def diagnose(company: str, max_items: int = 30) -> Dict:
    rows = cninfo_search(company, page_size=max_items)
    scenario_scores = Counter()
    evidence = []
    for item in rows:
        title = normalize_text(item.get("announcementTitle", ""))
        hits = []
        for scenario, kws in SCENARIO_RULES.items():
        pass
    w.lower() in title.lower() for kw in kws):
                scenario_scores[scenario] += 1
                hits.append(scenario)
        if hits:
            evidence.append({
                "title": title,
                "scenarios": hits,
                "url": f"https://static.cninfo.com.cn/{item.get('adjunctUrl', '')}" if item.get("adjunctUrl") else ""
            })
    ranked = [{"scenario": scenario, "signal_count": cnt, "strength": "high" if cnt >= 4 else "medium" if cnt >= 2 else "low"} for scenario, cnt in scenario_scores.most_common()]
    return {
        "company": company,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "scenario_diagnosis": ranked or [{"scenario": "公开公告中未形成清晰场景", "signal_count": 0, "strength": "low"}],
        "evidence": evidence[:12],
        "notes": [
            "场景诊断反映的是公开信息中出现频率较高的经营/治理/合规情景，不等同于最终投资判断。",
            "建议与财报、电话会纪要、监管文书及产业链价格数据联合使用。"
        ]
    }

def main():
    parser = argparse.ArgumentParser(description="企业场景诊断")
    parser.add_argument("--company", required=True)
    parser.add_argument("--max-items", type=int, default=30)
    args = parser.parse_args()
    print(format_result(diagnose(args.company, max_items=args.max_items)))

if __name__ == "__main__":
    main()
