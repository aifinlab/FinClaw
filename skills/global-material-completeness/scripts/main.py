from __future__ import annotations

from fetch_public_data import fetch_cninfo_announcements, search_official_rule_sources
from law_rules import match_rules, summarize_overall
from pathlib import Path
from typing import Any, Dict

import argparse
import json


def build_report(
    company_code: str,
    company_name: str,
    report_type: str,
    year: int,
) -> Dict[str, Any]:
    announcements = fetch_cninfo_announcements(
        company_code=company_code,
        company_name=company_name,
        year=year,
    )
    rule_results = match_rules(announcements, report_type)
    overall = summarize_overall(rule_results)

    return {
        "company_code": company_code,
        "company_name": company_name,
        "report_type": report_type,
        "year": year,
        "announcement_count": len(announcements),
        "overall_status": overall,
        "rule_results": rule_results,
        "rule_sources": search_official_rule_sources(),
    }


def print_human_report(report: Dict[str, Any]) -> None:
    print("=" * 80)
    print("上市企业材料完整性校验结果")
    print("=" * 80)
    print(f"公司代码: {report['company_code']}")
    print(f"公司名称: {report['company_name']}")
    print(f"报告类型: {report['report_type']}")
    print(f"年份: {report['year']}")
    print(f"公告抓取数量: {report['announcement_count']}")
    print(f"总体结论: {report['overall_status']}")
    print("-" * 80)

    for key, item in report["rule_results"].items():
        print(f"[{item['status']}] {item['display_name']}  (required={item['required']})")
        print(f"  说明: {item['evidence_hint']}")
        if item["legal_basis"]:
            print("  规则依据:")
            for basis in item["legal_basis"]:
                print(f"    - {basis}")
        if item["evidence"]:
            print("  命中公告:")
            for ev in item["evidence"][:5]:
                print(f"    - {ev['publish_time']} | {ev['title']}")
                if ev["url"]:
                    print(f"      {ev['url']}")
        else:
            print("  命中公告: 无")
        print("-" * 80)

    print("规则来源（元数据）:")
    for k, v in report["rule_sources"].items():
        print(f"  - {v['name']} | {v['source']} | {v['url']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="上市企业材料完整性校验（公网公开数据版）")
    parser.add_argument("--company-code", required=True, help="上市公司代码，如 300433")
    parser.add_argument("--company-name", required=True, help="上市公司名称，如 蓝思科技")
    parser.add_argument(
        "--report-type",
        required=True,
        choices=["annual_report", "semiannual_report"],
        help="校验类型：年度报告或半年度报告",
    )
    parser.add_argument("--year", required=True, type=int, help="报告年份，如 2025")
    parser.add_argument("--output", help="可选：输出 JSON 文件路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(
        company_code=args.company_code,
        company_name=args.company_name,
        report_type=args.report_type,
        year=args.year,
    )
    print_human_report(report)

    if args.output:
        path = Path(args.output)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n已写入输出文件: {path.resolve()}")


if __name__ == "__main__":
    main()
