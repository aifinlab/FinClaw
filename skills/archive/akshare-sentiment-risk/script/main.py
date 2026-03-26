from __future__ import annotations

from fetch_data import fetch_stock_news, fetch_weibo_hotness
from pathlib import Path
from risk_rules import score_text, aggregate_scores
from typing import Any, Dict

import argparse

import json
import pandas as pd


def _choose_col(df: pd.DataFrame, names: list[str]) -> str | None:
    for name in names:
        if name in df.columns:
            return name
    for col in df.columns:
        if any(key in col for key in names):
            return col
    return None


def analyze_stock(symbol: str, stock_name: str | None, limit: int) -> Dict[str, Any]:
    news_df = fetch_stock_news(symbol=symbol, stock_name=stock_name, limit=limit)
    if news_df.empty:
        return {
            "symbol": symbol,
            "stock_name": stock_name,
            "summary": {
                "overall_risk_score": 0.0,
                "overall_risk_level": "low",
                "article_count": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "hotness_adjustment": 0.0,
            },
            "articles": [],
            "note": "未获取到新闻数据，请检查 AkShare 版本、股票代码或网络连通性。",
        }

    title_col = _choose_col(news_df, ["标题", "title", "新闻标题"])
    content_col = _choose_col(news_df, ["内容", "content", "摘要", "新闻内容"])
    time_col = _choose_col(news_df, ["发布时间", "日期", "时间", "date", "datetime"])
    source_col = _choose_col(news_df, ["来源", "source", "媒体"])
    url_col = _choose_col(news_df, ["链接", "url", "新闻链接"])

    articles = []
    article_scores = []

    for _, row in news_df.iterrows():
        title = str(row[title_col]) if title_col else ""
        content = str(row[content_col]) if content_col else ""
        text = f"{title} {content}"
        result = score_text(text)
        article_scores.append(result)
        articles.append(
            {
                "time": str(row[time_col]) if time_col else "",
                "source": str(row[source_col]) if source_col else "",
                "title": title,
                "url": str(row[url_col]) if url_col else "",
                "risk_score": result.risk_score,
                "risk_level": result.level,
                "negative_hits": result.negative_hits,
                "positive_hits": result.positive_hits,
                "reason": result.reason,
            }
        )

    inferred_name = stock_name
    if not inferred_name:
        name_col = _choose_col(news_df, ["名称", "简称", "name"])
        if name_col:
            inferred_name = str(news_df.iloc[0][name_col])

    hotness = fetch_weibo_hotness(inferred_name) if inferred_name else None
    summary = aggregate_scores(article_scores, hotness_rank=hotness)

    high_risk_articles = sorted(articles, key=lambda x: x["risk_score"], reverse=True)[:10]

    return {
        "symbol": symbol,
        "stock_name": inferred_name,
        "summary": summary,
        "weibo_hotness_rank": hotness,
        "articles": high_risk_articles,
        "note": "结果基于 AkShare 可获取的新闻/舆情数据与规则词典得分，仅用于研究与风控辅助，不构成投资建议。",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="基于 AkShare 的单只股票舆情风险识别")
    parser.add_argument("--symbol", required=True, help="股票代码，如 000001")
    parser.add_argument("--stock-name", default=None, help="股票名称，可选，用于舆情热度匹配")
    parser.add_argument("--limit", type=int, default=50, help="最多分析多少条新闻")
    parser.add_argument("--output", default="result.json", help="输出 JSON 文件路径")
    args = parser.parse_args()

    result = analyze_stock(symbol=args.symbol, stock_name=args.stock_name, limit=args.limit)
    output_path = Path(args.output)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
