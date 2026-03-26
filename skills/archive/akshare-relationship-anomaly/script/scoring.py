from .config import RISK_LEVELS

from __future__ import annotations

from typing import Dict, List

import pandas as pd


def compute_market_anomaly_features(hist: pd.DataFrame) -> Dict[str, float]:
    if hist.empty or len(hist) < 5:
        return {
            "return_z_proxy": 0.0,
            "amplitude": 0.0,
            "volume_ratio": 0.0,
            "turnover": 0.0,
        }

    df = hist.copy().sort_values("日期")
    df["ret"] = pd.to_numeric(df.get("涨跌幅", 0), errors="coerce")
    df["volume"] = pd.to_numeric(df.get("成交量", 0), errors="coerce")
    df["turnover"] = pd.to_numeric(df.get("换手率", 0), errors="coerce")
    latest = df.iloc[-1]
    recent_ret_std = df["ret"].tail(20).std()
    ret_z_proxy = 0.0 if pd.isna(recent_ret_std) or recent_ret_std == 0 else abs(latest["ret"]) / recent_ret_std
    recent_volume_mean = df["volume"].tail(20).mean()
    volume_ratio = 0.0 if pd.isna(recent_volume_mean) or recent_volume_mean == 0 else latest["volume"] / recent_volume_mean

    return {
        "return_z_proxy": float(round(ret_z_proxy, 4)),
        "amplitude": float(round(pd.to_numeric(latest.get("振幅", 0), errors="coerce") or 0, 4)),
        "volume_ratio": float(round(volume_ratio, 4)),
        "turnover": float(round(pd.to_numeric(latest.get("turnover", latest.get("换手率", 0)), errors="coerce") or 0, 4)),
    }


def score_risk(
    market_features: Dict[str, float],
    graph_stats: Dict[str, float],
    edge_counter: Dict[str, int],
    lhb_stat: pd.DataFrame,
    hold_change: pd.DataFrame,
    disclosure: pd.DataFrame,
) -> Dict[str, object]:
    signals: List[str] = []
    score = 0.0

    if market_features["volume_ratio"] >= 2.0:
        score += 18
        signals.append("成交量放大异常")
    if market_features["return_z_proxy"] >= 2.0:
        score += 18
        signals.append("价格波动异常")
    if market_features["amplitude"] >= 10:
        score += 10
        signals.append("振幅偏高")
    if market_features["turnover"] >= 8:
        score += 8
        signals.append("换手率偏高")

    if edge_counter.get("broker_edges", 0) >= 3:
        score += 18
        signals.append("营业部共现异常")
    if graph_stats.get("stock_degree", 0) >= 5:
        score += 8
        signals.append("关系网络连接度偏高")
    if graph_stats.get("density", 0) >= 0.15:
        score += 8
        signals.append("关系网络密度偏高")

    if not lhb_stat.empty:
        score += 12
        signals.append("观察期内存在龙虎榜统计记录")

    if not hold_change.empty:
        score += min(10, 2 + len(hold_change.head(5)) * 2)
        signals.append("人员持股变动共振")

    if not disclosure.empty:
        score += min(8, 2 + len(disclosure.head(4)) * 1.5)
        signals.append("公告/调研披露共振")

    score = min(100.0, round(score, 2))
    return {
        "risk_score": score,
        "risk_level": _risk_level(score),
        "signals": signals,
    }


def _risk_level(score: float) -> str:
    for threshold, label in RISK_LEVELS:
        if score >= threshold:
            return label
    return "低"
