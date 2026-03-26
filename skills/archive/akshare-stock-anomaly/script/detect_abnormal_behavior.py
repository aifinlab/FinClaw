#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用 AkShare 对单只 A 股进行异常行为识别。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import akshare as ak
import argparse

import json
import numpy as np
import pandas as pd


@dataclass
class DetectionConfig:
    symbol: str
    start: str
    end: str
    period: str = "daily"
    adjust: str = "qfq"
    window: int = 20
    z_threshold: float = 2.5


def safe_zscore(series: pd.Series, window: int) -> pd.Series:
    rolling_mean = series.rolling(window).mean()
    rolling_std = series.rolling(window).std(ddof=0)
    z = (series - rolling_mean) / rolling_std.replace(0, np.nan)
    return z.replace([np.inf, -np.inf], np.nan)


def fetch_hist(config: DetectionConfig) -> pd.DataFrame:
    df = ak.stock_zh_a_hist(
        symbol=config.symbol,
        period=config.period,
        start_date=config.start,
        end_date=config.end,
        adjust=config.adjust,
    )
    if df.empty:
        raise ValueError("未获取到行情数据，请检查股票代码或日期区间。")

    df = df.copy()
    df["日期"] = pd.to_datetime(df["日期"])
    numeric_cols = [
        "开盘",
        "收盘",
        "最高",
        "最低",
        "成交量",
        "成交额",
        "振幅",
        "涨跌幅",
        "涨跌额",
        "换手率",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("日期").reset_index(drop=True)


def add_features(df: pd.DataFrame, window: int) -> pd.DataFrame:
    out = df.copy()
    out["return"] = out["收盘"].pct_change()
    out["pct_change_decimal"] = out["涨跌幅"] / 100.0 if "涨跌幅" in out.columns else out["return"]
    out["volume_z"] = safe_zscore(out["成交量"], window)
    out["amount_z"] = safe_zscore(out["成交额"], window) if "成交额" in out.columns else np.nan
    out["amplitude_z"] = safe_zscore(out["振幅"], window) if "振幅" in out.columns else np.nan
    out["pct_change_z"] = safe_zscore(out["涨跌幅"], window) if "涨跌幅" in out.columns else safe_zscore(out["return"], window)
    out["turnover_z"] = safe_zscore(out["换手率"], window) if "换手率" in out.columns else np.nan

    out["large_up"] = out["涨跌幅"] >= 5 if "涨跌幅" in out.columns else out["return"] >= 0.05
    out["large_down"] = out["涨跌幅"] <= -5 if "涨跌幅" in out.columns else out["return"] <= -0.05
    out["volume_spike_flag"] = out["volume_z"] >= 2.0

    out["consecutive_large_move_3d"] = (
        out["large_up"].rolling(3).sum().fillna(0) >= 2
    ) | (
        out["large_down"].rolling(3).sum().fillna(0) >= 2
    )
    out["consecutive_volume_spike_3d"] = out["volume_spike_flag"].rolling(3).sum().fillna(0) >= 2
    return out


def detect_labels(df: pd.DataFrame, z_threshold: float) -> Dict[str, object]:
    latest = df.iloc[-1]
    recent3 = df.tail(3)

    labels: List[str] = []
    explanations: List[str] = []
    score = 0.0

    pct_col = "涨跌幅" if "涨跌幅" in df.columns else "return"
    latest_pct = float(latest[pct_col]) if pd.notna(latest[pct_col]) else np.nan

    pct_z = latest.get("pct_change_z", np.nan)
    if pd.notna(pct_z) and pct_z >= z_threshold:
        labels.append("price_spike_up")
        explanations.append("最新交易日涨跌幅显著高于滚动历史分布")
        score += 18
    elif pd.notna(pct_z) and pct_z <= -z_threshold:
        labels.append("price_spike_down")
        explanations.append("最新交易日涨跌幅显著低于滚动历史分布")
        score += 18

    vol_z = latest.get("volume_z", np.nan)
    if pd.notna(vol_z) and vol_z >= z_threshold:
        labels.append("volume_spike")
        explanations.append("最新交易日成交量显著高于滚动历史均值")
        score += 16

    amp_z = latest.get("amplitude_z", np.nan)
    if pd.notna(amp_z) and amp_z >= z_threshold:
        labels.append("amplitude_spike")
        explanations.append("最新交易日振幅显著高于滚动历史分布")
        score += 14

    turnover_z = latest.get("turnover_z", np.nan)
    if pd.notna(turnover_z) and turnover_z >= z_threshold:
        labels.append("turnover_spike")
        explanations.append("最新交易日换手率显著高于滚动历史分布")
        score += 14

    if bool(recent3["consecutive_large_move_3d"].iloc[-1]):
        labels.append("consecutive_abnormal_move")
        explanations.append("最近3个交易日存在连续大幅波动现象")
        score += 16

    if bool(recent3["consecutive_volume_spike_3d"].iloc[-1]):
        labels.append("consecutive_volume_anomaly")
        explanations.append("最近3个交易日存在连续放量异常")
        score += 12

    if labels:
        labels.append("behavior_watchlist")
        score += 4

    score = min(100.0, round(score, 2))

    result = {
        "symbol": str(latest.get("股票代码", "")) if "股票代码" in latest.index else None,
        "last_date": latest["日期"].strftime("%Y-%m-%d"),
        "risk_score": score,
        "labels": labels,
        "latest_metrics": {
            "pct_change": None if pd.isna(latest_pct) else round(float(latest_pct), 4),
            "volume_zscore": None if pd.isna(vol_z) else round(float(vol_z), 4),
            "amplitude": None if "振幅" not in latest.index or pd.isna(latest.get("振幅")) else round(float(latest["振幅"]), 4),
            "amplitude_zscore": None if pd.isna(amp_z) else round(float(amp_z), 4),
            "turnover": None if "换手率" not in latest.index or pd.isna(latest.get("换手率")) else round(float(latest["换手率"]), 4),
            "turnover_zscore": None if pd.isna(turnover_z) else round(float(turnover_z), 4),
        },
        "explanations": explanations,
    }
    return result


def run_detection(config: DetectionConfig) -> Dict[str, object]:
    df = fetch_hist(config)
    min_required = max(config.window + 5, 30)
    if len(df) < min_required:
        raise ValueError(f"历史数据不足，至少需要 {min_required} 条记录，当前仅有 {len(df)} 条。")

    feat = add_features(df, config.window)
    result = detect_labels(feat, config.z_threshold)
    result["symbol"] = config.symbol
    result["window"] = config.window
    result["z_threshold"] = config.z_threshold
    return result


def parse_args() -> DetectionConfig:
    parser = argparse.ArgumentParser(description="A股单股票异常行为识别")
    parser.add_argument("--symbol", required=True, help="A股股票代码，如 600519 或 000001")
    parser.add_argument("--start", required=True, help="开始日期，格式 YYYYMMDD")
    parser.add_argument("--end", required=True, help="结束日期，格式 YYYYMMDD")
    parser.add_argument("--period", default="daily", help="周期，默认 daily")
    parser.add_argument("--adjust", default="qfq", help="复权方式，默认 qfq")
    parser.add_argument("--window", type=int, default=20, help="滚动窗口长度，默认 20")
    parser.add_argument("--z-threshold", type=float, default=2.5, help="异常阈值，默认 2.5")
    args = parser.parse_args()
    return DetectionConfig(
        symbol=args.symbol,
        start=args.start,
        end=args.end,
        period=args.period,
        adjust=args.adjust,
        window=args.window,
        z_threshold=args.z_threshold,
    )


if __name__ == "__main__":
    cfg = parse_args()
    output = run_detection(cfg)
    print(json.dumps(output, ensure_ascii=False, indent=2))
