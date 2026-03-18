"""Configuration for the AKShare A-share risk sentiment trigger skill."""

from __future__ import annotations

DEFAULT_NEGATIVE_KEYWORDS = [
    "立案",
    "处罚",
    "违规",
    "违约",
    "减值",
    "商誉",
    "质押",
    "暴跌",
    "亏损",
    "ST",
    "问询函",
    "诉讼",
    "终止",
    "下修",
    "停牌",
    "冻结",
    "被执行",
    "风险提示",
]

THRESHOLDS = {
    "daily_drop_pct": -7.0,
    "five_day_return_pct": -12.0,
    "volatility_ratio": 1.5,
    "turnover_spike_ratio": 2.0,
    "drawdown_pct": 20.0,
    "negative_news_ratio": 0.30,
    "severe_negative_news_ratio": 0.50,
    "pledge_ratio_warn": 20.0,
    "pledge_ratio_severe": 35.0,
    "comment_score_low": 45.0,
    "hot_rank_top_n": 100,
}

WEIGHTS = {
    "daily_drop": 18,
    "five_day_drop": 16,
    "volatility_expansion": 12,
    "turnover_spike": 10,
    "drawdown": 12,
    "negative_news": 12,
    "severe_negative_news": 8,
    "hot_rank_deterioration": 6,
    "pledge_warn": 10,
    "pledge_severe": 8,
    "goodwill_warning": 14,
    "low_comment_score": 4,
}

LEVELS = [
    (60, "CRITICAL"),
    (40, "HIGH"),
    (20, "MEDIUM"),
    (0, "LOW"),
]
