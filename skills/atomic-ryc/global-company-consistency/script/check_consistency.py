from __future__ import annotations

import argparse
from typing import Any, Dict, List

from common import pretty_print
from fetch_company_profile import fetch_company_profile
from fetch_regulations import search_regulations


CORE_FIELDS = {
    "company_name": "公司名称",
    "legal_representative": "法定代表人",
    "registered_address": "注册地址",
    "office_address": "办公地址",
    "registered_capital": "注册资本",
    "established_date": "成立日期",
    "listed_date": "上市日期",
    "industry": "所属行业",
}


def detect_risk(field_results: List[Dict[str, Any]], change_hints: List[str]) -> Dict[str, Any]:
    mismatch_fields = [item for item in field_results if item["status"] in {"疑似不一致", "疑似未及时更新"}]
    missing_fields = [item for item in field_results if item["status"] == "信息缺失"]
    has_change_hints = len(change_hints) > 0

    if mismatch_fields and has_change_hints:
        level = "较高"
        summary = "近期公告存在变更线索，且核心字段跨来源不一致，建议立即复核最新公告、年报与工商信息。"
    elif mismatch_fields:
        level = "中"
        summary = "核心字段存在跨来源不一致，可能是口径差异、页面未更新或披露不同步。"
    elif missing_fields:
        level = "低"
        summary = "未发现明显冲突，但存在字段缺失，建议补充年报或公告来源后再次校验。"
    else:
        level = "低"
        summary = "当前公开资料未发现明显冲突。"

    return {"risk_level": level, "summary": summary}


def run_consistency_check(symbol: str, exchange: str, announcement_keywords: List[str] | None = None) -> Dict[str, Any]:
    profile = fetch_company_profile(symbol, exchange)
    change_hints = profile.get("announcement_hints", {}).get("recent_change_hints", [])

    if announcement_keywords:
        change_hints = [
            hint for hint in change_hints if any(keyword in hint for keyword in announcement_keywords)
        ]

    field_results: List[Dict[str, Any]] = []
    for field_key, field_label in CORE_FIELDS.items():
        value = profile.get(field_key)
        # 当前版本默认来源是资料页 + 公告变更线索；因此在无第二个明确值时，
        # 以“有值 + 无冲突线索”为基础判断为一致/待补证。
        status = "一致" if value else "信息缺失"
        note = "来源字段存在" if value else "公开资料页未提取到该字段"

        if field_key in {"legal_representative", "registered_address", "registered_capital"} and change_hints:
            status = "疑似未及时更新" if value else "信息缺失"
            note = "存在近期变更公告线索，建议与公告正文和最新年报逐项复核。"

        field_results.append(
            {
                "field": field_label,
                "value": value,
                "status": status,
                "note": note,
            }
        )

    regulations = search_regulations("信息披露")
    risk = detect_risk(field_results, change_hints)

    return {
        "symbol": symbol,
        "exchange": exchange,
        "company_profile": profile,
        "field_check_results": field_results,
        "relevant_regulations": regulations,
        "recent_change_hints": change_hints,
        "risk_assessment": risk,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="对上市企业做字段一致性校验")
    parser.add_argument("--symbol", required=True, help="股票代码，例如 600519")
    parser.add_argument("--exchange", default="SSE", help="交易所：SSE 或 SZSE")
    parser.add_argument(
        "--announcement-keywords",
        nargs="*",
        default=None,
        help="只保留包含这些关键词的公告线索，例如 法定代表人 注册地址 注册资本",
    )
    args = parser.parse_args()

    result = run_consistency_check(args.symbol, args.exchange.upper(), args.announcement_keywords)
    pretty_print(result)


if __name__ == "__main__":
    main()
