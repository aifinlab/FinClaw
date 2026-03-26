
from common import save_json, sha256_text
from fetch_company_profile import build_company_seed_urls, fetch_company_public_page
from fetch_regulations import list_regulation_sources

from typing import Dict, List
import argparse
import os


def build_evidence_bundle(company: str, ticker: str, topic: str) -> Dict:
    evidences: List[Dict] = []
    for item in list_regulation_sources():
        evidences.append({
            "source_type": "regulation_source",
            "title": item["name"],
            "url": item["url"],
            "summary": f"与主题“{topic}”相关的法规检索入口。",
            "hash": sha256_text(item["url"]),
        })
    for url in build_company_seed_urls(company, ticker, market="cn"):
        evidences.append({
            "source_type": "company_source",
            "title": company,
            "url": url,
            "summary": f"{company} 公开披露与查询入口，用于后续检索 {topic} 相关年报、公告和制度文件。",
            "hash": sha256_text(url + company),
        })
    return {
        "company": company,
        "ticker": ticker,
        "topic": topic,
        "evidence_count": len(evidences),
        "evidences": evidences,
        "note": "示例版本聚合入口级证据；生产环境可继续接入 PDF 下载、段落抽取和相似度聚类。"
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--ticker", default="")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output", default="output/evidence_bundle.json")
    args = parser.parse_args()

    result = build_evidence_bundle(args.company, args.ticker, args.topic)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    save_json(args.output, result)
    print(f"saved to {args.output}")


if __name__ == "__main__":
    main()
