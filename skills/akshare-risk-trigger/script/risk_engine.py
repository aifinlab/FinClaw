"""Rule-based risk sentiment engine for A-share stocks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd

from config import LEVELS, THRESHOLDS, WEIGHTS
from data_loader import LoadedData, filter_row_by_symbol
from utils import pick_first_existing


@dataclass
class RiskResult:
    symbol: str
    as_of_date: str
    risk_score: int
    risk_level: str
    triggers: list[str]
    headline_negative_ratio: float | None
    negative_news_count: int
    total_news_count: int
    pledge_ratio: float | None
    goodwill_warning: bool
    latest_rank: int | None
    comment_score: float | None
    metrics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RiskSentimentEngine:
    def __init__(self, symbol: str, negative_keywords: list[str]):
        self.symbol = symbol
        self.negative_keywords = negative_keywords

    def evaluate(self, data: LoadedData) -> RiskResult:
        price = data.price.copy()
        close_col = pick_first_existing(price, ["收盘", "close"])
        pct_col = pick_first_existing(price, ["涨跌幅", "pct_chg"])
        turnover_col = pick_first_existing(price, ["换手率", "turnover"])
        date_col = pick_first_existing(price, ["日期", "date"])

        if close_col is None or pct_col is None or date_col is None:
            raise ValueError("Price dataframe is missing required columns")

        price[close_col] = pd.to_numeric(price[close_col], errors="coerce")
        price[pct_col] = pd.to_numeric(price[pct_col], errors="coerce")
        if turnover_col:
            price[turnover_col] = pd.to_numeric(price[turnover_col], errors="coerce")

        price["daily_return"] = price[close_col].pct_change()
        latest = price.iloc[-1]
        last_5 = price.tail(5)
        last_20 = price.tail(20)
        last_60 = price.tail(60)

        five_day_return_pct = ((last_5[close_col].iloc[-1] / last_5[close_col].iloc[0]) - 1.0) * 100 if len(last_5) >= 2 else np.nan
        vol20 = last_20["daily_return"].std(ddof=0) * np.sqrt(252) if len(last_20) >= 5 else np.nan
        vol60 = last_60["daily_return"].std(ddof=0) * np.sqrt(252) if len(last_60) >= 20 else np.nan
        volatility_ratio = (vol20 / vol60) if pd.notna(vol20) and pd.notna(vol60) and vol60 not in (0, np.nan) else np.nan
        max_close_60 = last_60[close_col].max() if not last_60.empty else np.nan
        drawdown_pct = ((max_close_60 - latest[close_col]) / max_close_60) * 100 if pd.notna(max_close_60) and max_close_60 else np.nan

        turnover_spike_ratio = np.nan
        if turnover_col and len(last_20) >= 5:
            avg_turnover_20 = last_20[turnover_col].mean()
            if avg_turnover_20 and pd.notna(avg_turnover_20):
                turnover_spike_ratio = latest[turnover_col] / avg_turnover_20

        score = 0
        triggers: list[str] = []

        latest_pct = float(latest[pct_col])
        if latest_pct <= THRESHOLDS["daily_drop_pct"]:
            score += WEIGHTS["daily_drop"]
            triggers.append(f"单日跌幅触发: {latest_pct:.2f}% <= {THRESHOLDS['daily_drop_pct']}%")

        if pd.notna(five_day_return_pct) and five_day_return_pct <= THRESHOLDS["five_day_return_pct"]:
            score += WEIGHTS["five_day_drop"]
            triggers.append(
                f"5日累计跌幅触发: {five_day_return_pct:.2f}% <= {THRESHOLDS['five_day_return_pct']}%"
            )

        if pd.notna(volatility_ratio) and volatility_ratio >= THRESHOLDS["volatility_ratio"]:
            score += WEIGHTS["volatility_expansion"]
            triggers.append(
                f"波动放大触发: 20日/60日波动率比值 {volatility_ratio:.2f} >= {THRESHOLDS['volatility_ratio']}"
            )

        if pd.notna(turnover_spike_ratio) and turnover_spike_ratio >= THRESHOLDS["turnover_spike_ratio"]:
            score += WEIGHTS["turnover_spike"]
            triggers.append(
                f"换手异常触发: 最新换手/20日均值 {turnover_spike_ratio:.2f} >= {THRESHOLDS['turnover_spike_ratio']}"
            )

        if pd.notna(drawdown_pct) and drawdown_pct >= THRESHOLDS["drawdown_pct"]:
            score += WEIGHTS["drawdown"]
            triggers.append(f"60日回撤触发: {drawdown_pct:.2f}% >= {THRESHOLDS['drawdown_pct']}%")

        news_metrics = self._score_news(data.news)
        if news_metrics["negative_ratio"] is not None and news_metrics["negative_ratio"] >= THRESHOLDS["negative_news_ratio"]:
            score += WEIGHTS["negative_news"]
            triggers.append(
                f"舆情风险触发: 负面新闻占比 {news_metrics['negative_ratio']:.2%} >= {THRESHOLDS['negative_news_ratio']:.0%}"
            )
        if news_metrics["negative_ratio"] is not None and news_metrics["negative_ratio"] >= THRESHOLDS["severe_negative_news_ratio"]:
            score += WEIGHTS["severe_negative_news"]
            triggers.append(
                f"严重舆情触发: 负面新闻占比 {news_metrics['negative_ratio']:.2%} >= {THRESHOLDS['severe_negative_news_ratio']:.0%}"
            )

        hot_rank, hot_deteriorated = self._score_hotness(data.hot_rank, data.hot_rank_detail)
        if hot_rank is not None and hot_rank <= THRESHOLDS["hot_rank_top_n"] and hot_deteriorated:
            score += WEIGHTS["hot_rank_deterioration"]
            triggers.append(f"热度失衡触发: 当前人气排名 {hot_rank} 且近期排名恶化")

        pledge_ratio = self._get_pledge_ratio(data.pledge)
        if pledge_ratio is not None and pledge_ratio >= THRESHOLDS["pledge_ratio_warn"]:
            score += WEIGHTS["pledge_warn"]
            triggers.append(f"高质押触发: 质押比例 {pledge_ratio:.2f}% >= {THRESHOLDS['pledge_ratio_warn']}%")
        if pledge_ratio is not None and pledge_ratio >= THRESHOLDS["pledge_ratio_severe"]:
            score += WEIGHTS["pledge_severe"]
            triggers.append(f"严重高质押触发: 质押比例 {pledge_ratio:.2f}% >= {THRESHOLDS['pledge_ratio_severe']}%")

        goodwill_warning = self._has_goodwill_warning(data.goodwill)
        if goodwill_warning:
            score += WEIGHTS["goodwill_warning"]
            triggers.append("商誉减值预期触发")

        comment_score = self._get_comment_score(data.comment)
        if comment_score is not None and comment_score <= THRESHOLDS["comment_score_low"]:
            score += WEIGHTS["low_comment_score"]
            triggers.append(f"辅助低评分触发: 千股千评综合得分 {comment_score:.2f}")

        level = next(label for cutoff, label in LEVELS if score >= cutoff)
        return RiskResult(
            symbol=self.symbol,
            as_of_date=str(pd.to_datetime(latest[date_col]).date()),
            risk_score=int(score),
            risk_level=level,
            triggers=triggers,
            headline_negative_ratio=news_metrics["negative_ratio"],
            negative_news_count=news_metrics["negative_count"],
            total_news_count=news_metrics["total_count"],
            pledge_ratio=pledge_ratio,
            goodwill_warning=goodwill_warning,
            latest_rank=hot_rank,
            comment_score=comment_score,
            metrics={
                "latest_pct_change": round(latest_pct, 4),
                "five_day_return_pct": round(float(five_day_return_pct), 4) if pd.notna(five_day_return_pct) else None,
                "volatility_ratio_20_60": round(float(volatility_ratio), 4) if pd.notna(volatility_ratio) else None,
                "turnover_spike_ratio": round(float(turnover_spike_ratio), 4) if pd.notna(turnover_spike_ratio) else None,
                "drawdown_pct_60d": round(float(drawdown_pct), 4) if pd.notna(drawdown_pct) else None,
            },
        )

    def _score_news(self, news_df: pd.DataFrame) -> dict[str, Any]:
        if news_df.empty:
            return {"negative_ratio": None, "negative_count": 0, "total_count": 0}

        title_col = pick_first_existing(news_df, ["新闻标题", "title"])
        content_col = pick_first_existing(news_df, ["新闻内容", "content"])
        if title_col is None and content_col is None:
            return {"negative_ratio": None, "negative_count": 0, "total_count": 0}

        total = len(news_df)
        negative_count = 0
        for _, row in news_df.iterrows():
            text = f"{row.get(title_col, '')} {row.get(content_col, '')}".upper()
            if any(keyword.upper() in text for keyword in self.negative_keywords):
                negative_count += 1
        ratio = negative_count / total if total else None
        return {"negative_ratio": ratio, "negative_count": negative_count, "total_count": total}

    def _score_hotness(self, hot_df: pd.DataFrame, detail_df: pd.DataFrame) -> tuple[int | None, bool]:
        latest_rank = None
        deteriorated = False

        row = filter_row_by_symbol(hot_df, self.symbol, ["代码", "股票代码", "证券代码"])
        if row:
            for key in ("当前排名", "最新排名", "排名"):
                if key in row and pd.notna(row[key]):
                    latest_rank = int(row[key])
                    break

        if not detail_df.empty:
            rank_col = pick_first_existing(detail_df, ["排名", "当前排名"])
            if rank_col is not None and len(detail_df) >= 3:
                series = pd.to_numeric(detail_df[rank_col], errors="coerce").dropna()
                if len(series) >= 3:
                    recent = series.tail(3)
                    deteriorated = recent.iloc[-1] > recent.iloc[0]
                    if latest_rank is None:
                        latest_rank = int(recent.iloc[-1])
        return latest_rank, deteriorated

    def _get_pledge_ratio(self, pledge_df: pd.DataFrame) -> float | None:
        row = filter_row_by_symbol(pledge_df, self.symbol, ["股票代码", "代码", "证券代码"])
        if not row:
            return None
        for key in ("质押比例", "最新质押比例", "上市公司质押比例"):
            if key in row and pd.notna(row[key]):
                try:
                    return float(row[key])
                except Exception:
                    return None
        return None

    def _has_goodwill_warning(self, goodwill_df: pd.DataFrame) -> bool:
        row = filter_row_by_symbol(goodwill_df, self.symbol, ["股票代码", "代码", "证券代码"])
        return row is not None

    def _get_comment_score(self, comment_df: pd.DataFrame) -> float | None:
        row = filter_row_by_symbol(comment_df, self.symbol, ["代码", "股票代码", "证券代码"])
        if not row:
            return None
        for key in ("综合得分", "评分"):
            if key in row and pd.notna(row[key]):
                try:
                    return float(row[key])
                except Exception:
                    return None
        return None
