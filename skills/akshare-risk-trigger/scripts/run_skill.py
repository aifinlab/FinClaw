#!/usr/bin/env python3
"""CLI entrypoint for the AKShare A-share risk sentiment trigger skill."""

from __future__ import annotations

from config import DEFAULT_NEGATIVE_KEYWORDS
from data_loader import AkshareRiskDataLoader
from datetime import date, timedelta

from risk_engine import RiskSentimentEngine
from utils import split_keywords
import argparse
import json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AKShare A股风险舆情触发机制")
    parser.add_argument("--symbol", required=True, help="6位 A 股股票代码，例如 603777")
    parser.add_argument(
        "--start-date",
        default=(date.today() - timedelta(days=180)).strftime("%Y%m%d"),
        help="开始日期，格式 YYYYMMDD，默认最近 180 天",
    )
    parser.add_argument(
        "--end-date",
        default=date.today().strftime("%Y%m%d"),
        help="结束日期，格式 YYYYMMDD，默认今天",
    )
    parser.add_argument(
        "--report-date",
        default=None,
        help="商誉减值预期使用的报告期，例如 20241231；不传则跳过该特征",
    )
    parser.add_argument(
        "--negative-keywords",
        default=None,
        help="自定义负面关键词，逗号分隔；不传则使用内置词表",
    )
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="输出格式",
    )
    return parser


def render_text(result: dict) -> str:
    lines = [
        f"symbol: {result['symbol']}",
        f"as_of_date: {result['as_of_date']}",
        f"risk_score: {result['risk_score']}",
        f"risk_level: {result['risk_level']}",
        f"headline_negative_ratio: {result['headline_negative_ratio']}",
        f"negative_news_count: {result['negative_news_count']}",
        f"total_news_count: {result['total_news_count']}",
        f"pledge_ratio: {result['pledge_ratio']}",
        f"goodwill_warning: {result['goodwill_warning']}",
        f"latest_rank: {result['latest_rank']}",
        f"comment_score: {result['comment_score']}",
        "metrics:",
    ]
    for key, value in result["metrics"].items():
        lines.append(f"  - {key}: {value}")
    lines.append("triggers:")
    if result["triggers"]:
        for item in result["triggers"]:
            lines.append(f"  - {item}")
    else:
        lines.append("  - 无触发项")
    return "\n".join(lines)


def main() -> None:
    args = build_parser().parse_args()
    negative_keywords = split_keywords(args.negative_keywords) or DEFAULT_NEGATIVE_KEYWORDS

    loader = AkshareRiskDataLoader(
        symbol=args.symbol,
        start_date=args.start_date,
        end_date=args.end_date,
        report_date=args.report_date,
    )
    data = loader.load()

    engine = RiskSentimentEngine(symbol=loader.symbol, negative_keywords=negative_keywords)
    result = engine.evaluate(data).to_dict()

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))


if __name__ == "__main__":
    main()
