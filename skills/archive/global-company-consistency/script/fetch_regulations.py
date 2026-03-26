from __future__ import annotations

from common import pretty_print
from typing import Any, Dict, List

import argparse

REGULATION_CATALOG: List[Dict[str, Any]] = [
    {
        "name": "上市公司信息披露管理办法",
        "publisher": "中国证监会",
        "effective_date": "2025-07-01",
        "url": "https://www.csrc.gov.cn/csrc/c101953/c7547359/content.shtml",
        "keywords": ["信息披露", "真实", "准确", "完整", "一致性", "重大遗漏", "误导性陈述"],
        "summary": "要求上市公司披露信息真实、准确、完整，不得有虚假记载、误导性陈述或者重大遗漏。",
    },
    {
        "name": "中华人民共和国证券法",
        "publisher": "全国人大 / 证监会法规库转引",
        "effective_date": "2020-03-01",
        "url": "https://neris.csrc.gov.cn/falvfagui/rdqsHeader/mainbody?navbarId=1&secFutrsLawId=0fc431a2a10b47909beef058f6ac3335",
        "keywords": ["证券法", "信息披露", "公开", "上市公司"],
        "summary": "为证券发行与交易、信息披露、投资者保护提供上位法依据。",
    },
    {
        "name": "上海证券交易所股票上市规则（2025年4月修订）",
        "publisher": "上海证券交易所",
        "effective_date": "2025-04-25",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/mainipo/c/c_20250515_10779023.shtml",
        "keywords": ["上交所", "上市规则", "信息披露", "公告", "重大事项"],
        "summary": "细化沪市上市公司的持续信息披露、自律监管及重大事项披露要求。",
    },
    {
        "name": "深圳证券交易所创业板股票上市规则（2025年修订）",
        "publisher": "深圳证券交易所",
        "effective_date": "2025-06-06",
        "url": "https://docs.static.szse.cn/www/lawrules/rule/stock/supervision/W020250606595019160611.pdf",
        "keywords": ["深交所", "创业板", "上市规则", "信息披露", "规范运作"],
        "summary": "细化深市创业板上市公司的持续信息披露、治理与规范运作要求。",
    },
]


def search_regulations(keyword: str) -> List[Dict[str, Any]]:
    keyword = keyword.strip().lower()
    results: List[Dict[str, Any]] = []
    for item in REGULATION_CATALOG:
        haystack = " ".join(
            [item["name"], item["publisher"], item["summary"], " ".join(item["keywords"])]
        ).lower()
        if keyword in haystack:
            results.append(item)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="检索与上市公司字段一致性相关的法律法规")
    parser.add_argument("--keyword", required=True, help="检索关键词，例如：信息披露 / 一致性 / 重大遗漏")
    args = parser.parse_args()

    results = search_regulations(args.keyword)
    pretty_print({"keyword": args.keyword, "count": len(results), "results": results})


if __name__ == "__main__":
    main()
