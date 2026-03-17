import argparse
from typing import Dict, List

from common import fetch_text, keyword_hits, parse_args_common, save_json

REGULATION_SOURCES = [
    {
        "rule_id": "DISCLOSURE-001",
        "title": "上市公司信息披露管理办法",
        "publisher": "中国证监会",
        "url": "https://www.csrc.gov.cn/csrc/c101953/c7547359/content.shtml",
    },
    {
        "rule_id": "LAW-001",
        "title": "中华人民共和国公司法",
        "publisher": "全国人大",
        "url": "https://www.npc.gov.cn/c2/c30834/202312/t20231229_433999.html",
    },
    {
        "rule_id": "SSE-001",
        "title": "上海证券交易所上市公司自律监管指引第1号——规范运作",
        "publisher": "上海证券交易所",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/mainipo/c/c_20250516_10779126.shtml",
    },
    {
        "rule_id": "SSE-002",
        "title": "上海证券交易所股票上市规则（相关公开版本入口）",
        "publisher": "上海证券交易所",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/mainipo/",
    },
    {
        "rule_id": "SZSE-001",
        "title": "深圳证券交易所股票上市规则 / 信息披露事务管理相关公开规则线索",
        "publisher": "深圳证券交易所",
        "url": "https://www.szse.cn/lawrules/rule/stock/listing/index.html",
    },
]


def run(keyword_text: str, max_items: int) -> Dict:
    keywords = [x.strip() for x in keyword_text.split() if x.strip()]
    regulations: List[Dict] = []
    for item in REGULATION_SOURCES[:max_items]:
        try:
            payload = fetch_text(item["url"])
            hits = keyword_hits(payload["text"], keywords or ["审计", "留痕", "信息披露", "内部控制"])
            regulations.append({
                **item,
                "trace": payload["trace"],
                "matched_snippets": hits[:20],
            })
        except Exception as exc:
            regulations.append({
                **item,
                "error": str(exc),
                "matched_snippets": [],
            })
    return {
        "keyword_text": keyword_text,
        "regulations": regulations,
    }


if __name__ == "__main__":
    parser = parse_args_common("抓取公开法规与交易所规则")
    parser.add_argument("--keyword", default="信息披露 审计 留痕 内部控制", help="空格分隔关键词")
    parser.add_argument("--max-items", type=int, default=10)
    args = parser.parse_args()

    result = run(keyword_text=args.keyword, max_items=args.max_items)
    save_json(result, args.output)
    print(f"saved: {args.output}")
