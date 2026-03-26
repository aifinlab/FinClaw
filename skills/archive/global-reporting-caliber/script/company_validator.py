"""High-level validator that combines public announcement retrieval and rule checks."""
from __future__ import annotations

from dataclasses import asdict
from public_sources import CninfoAdapter, build_default_source_registry
from rules_engine import ReportingCaliberEngine
from typing import Dict, List

import argparse
import json


class ListedCompanyReportingValidator:
    def __init__(self) -> None:
        self.cninfo = CninfoAdapter()
        self.engine = ReportingCaliberEngine()

    def run(self, company_name: str, stock_code: str = "", keyword: str = "", limit: int = 5) -> Dict[str, object]:
        search_keyword = keyword or company_name
        announcements = self.cninfo.search_announcements(
            keyword=search_keyword,
            stock_code=stock_code,
            page_num=1,
            page_size=limit,
        )
        combined_text = "\n".join([a.title + "\n" + a.snippet for a in announcements])
        result = self.engine.evaluate_text(combined_text)
        return {
            "company_name": company_name,
            "stock_code": stock_code,
            "search_keyword": search_keyword,
            "sources": build_default_source_registry(),
            "announcements": [asdict(a) for a in announcements],
            "validation": result,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate reporting caliber for a listed company using public data.")
    parser.add_argument("--company", required=True, help="Listed company name, e.g. 贵州茅台")
    parser.add_argument("--code", default="", help="Stock code, e.g. 600519")
    parser.add_argument("--keyword", default="", help="Search keyword, e.g. 关联交易")
    parser.add_argument("--limit", type=int, default=5, help="Max number of announcements to analyze")
    parser.add_argument("--output", default="", help="Optional output JSON file")
    args = parser.parse_args()

    validator = ListedCompanyReportingValidator()
    result = validator.run(company_name=args.company, stock_code=args.code, keyword=args.keyword, limit=args.limit)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
