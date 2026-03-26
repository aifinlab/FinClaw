#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A-share trend judgment skill based on AkShare public market data.

- Fetch A-share historical prices with AkShare
- Compute moving averages, momentum, drawdown and volatility
- Generate rule-based trend judgment labels
- Export a structured JSON result for downstream workflow usage
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
    import akshare as ak
import argparse

import json
import numpy as np
import pandas as pd
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_stock_quote,
    get_stock_history,
    get_index_quote,
    get_bond_list,
)
# ====================================
@dataclass
class TrendResult:
    symbol: str
    name: Optional[str]
    as_of: str
    trend_label: str
    confidence: float
    close: float
    ma5: float
    ma10: float
    ma20: float
    ma60: float
    ret_5d: float
    ret_20d: float
    ret_60d: float
    annualized_volatility: float
    max_drawdown_60d: float
    breakout_20d_high: bool
    breakdown_20d_low: bool
    signals: List[str]
    summary: str


def normalize_symbol(symbol: str) -> str:
    symbol = str(symbol).strip()
    if symbol.startswith(("sh", "sz", "bj")) and len(symbol) > 2:
        return symbol[2:]
    return symbol


def get_stock_name(symbol: str) -> Optional[str]:
        spot_df = ak.stock_zh_a_spot_em()
        row = spot_df.loc[spot_df["代码"].astype(str) == symbol]
        if row.empty:
            return None
        return str(row.iloc[0]["名称"])
def fetch_hist(symbol: str, start_date: str, end_date: str, adjust: str = "qfq") -> pd.DataFrame:
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )
    if df is None or df.empty:
        raise ValueError(f"未获取到股票 {symbol} 的历史行情数据")

    rename_map = {
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "amount",
        "振幅": "amplitude",
        "涨跌幅": "pct_chg",
        "涨跌额": "change",
        "换手率": "turnover",
    }
    df = df.rename(columns=rename_map).copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for win in (5, 10, 20, 60):
        out[f"ma{win}"] = out["close"].rolling(win).mean()

    out["ret_1d"] = out["close"].pct_change()
    for win in (5, 20, 60):
        out[f"ret_{win}d"] = out["close"].pct_change(win)

    out["rolling_20d_high"] = out["high"].rolling(20).max()
    out["rolling_20d_low"] = out["low"].rolling(20).min()

    out["vol_20d"] = out["ret_1d"].rolling(20).std() * np.sqrt(252)

    rolling_peak = out["close"].rolling(60).max()
    out["drawdown_60d"] = out["close"] / rolling_peak - 1
    out["max_drawdown_60d"] = out["drawdown_60d"].rolling(60).min()
    return out


def judge_trend(df: pd.DataFrame, symbol: str, name: Optional[str]) -> TrendResult:
    if len(df) < 70:
        raise ValueError("历史数据不足，至少建议 70 个交易日")

    row = df.iloc[-1]
    prev = df.iloc[-2]
    signals: List[str] = []
    score = 0

    ma5, ma10, ma20, ma60 = [float(row[f"ma{i}"]) for i in (5, 10, 20, 60)]
    close = float(row["close"])
    ret_5d = float(row["ret_5d"])
    ret_20d = float(row["ret_20d"])
    ret_60d = float(row["ret_60d"])
    vol = float(row["vol_20d"])
    mdd60 = float(row["max_drawdown_60d"])

    if close > ma20 > ma60:
        score += 2
        signals.append("收盘价位于 MA20 之上且 MA20 高于 MA60")
    if ma5 > ma10 > ma20:
        score += 2
        signals.append("短中期均线呈多头排列")
    if ret_20d > 0.08:
        score += 1
        signals.append("20日收益率显著为正")
    if close >= float(row["rolling_20d_high"]):
        score += 2
        signals.append("价格突破近20日高点")

    if close < ma20 < ma60:
        score -= 2
        signals.append("收盘价位于 MA20 下方且 MA20 低于 MA60")
    if ma5 < ma10 < ma20:
        score -= 2
        signals.append("短中期均线呈空头排列")
    if ret_20d < -0.08:
        score -= 1
        signals.append("20日收益率显著为负")
    if close <= float(row["rolling_20d_low"]):
        score -= 2
        signals.append("价格跌破近20日低点")

    if vol > 0.55:
        score -= 1
        signals.append("20日年化波动率偏高")
    if mdd60 < -0.20:
        score -= 1
        signals.append("近60日最大回撤较大")
    if float(prev["close"]) < float(prev["ma20"]) <= close:
        score += 1
        signals.append("最新交易日向上站回 MA20")

    if score >= 5:
        trend_label = "强势上升趋势"
    elif score >= 2:
        trend_label = "震荡偏强"
    elif score <= -5:
        trend_label = "强势下降趋势"
    elif score <= -2:
        trend_label = "震荡偏弱"
    else:
        trend_label = "区间震荡"

    confidence = min(0.95, 0.45 + abs(score) * 0.08)
    breakout_20d_high = close >= float(row["rolling_20d_high"])
    breakdown_20d_low = close <= float(row["rolling_20d_low"])

    summary = (
        f"{name or symbol} 截至 {row['date'].date()} 的趋势判断为“{trend_label}”。"
        f"收盘价 {close:.2f}，MA20 {ma20:.2f}，MA60 {ma60:.2f}，"
        f"20日涨跌幅 {ret_20d:.2%}，20日年化波动率 {vol:.2%}。"
    )

    return TrendResult(
        symbol=symbol,
        name=name,
        as_of=str(row["date"].date()),
        trend_label=trend_label,
        confidence=round(confidence, 4),
        close=round(close, 4),
        ma5=round(ma5, 4),
        ma10=round(ma10, 4),
        ma20=round(ma20, 4),
        ma60=round(ma60, 4),
        ret_5d=round(ret_5d, 6),
        ret_20d=round(ret_20d, 6),
        ret_60d=round(ret_60d, 6),
        annualized_volatility=round(vol, 6),
        max_drawdown_60d=round(mdd60, 6),
        breakout_20d_high=breakout_20d_high,
        breakdown_20d_low=breakdown_20d_low,
        signals=signals,
        summary=summary,
    )


def run(symbol: str, start_date: str, end_date: str, adjust: str = "qfq") -> Dict:
    symbol = normalize_symbol(symbol)
    name = get_stock_name(symbol)
    hist = fetch_hist(symbol, start_date, end_date, adjust=adjust)
    enriched = compute_indicators(hist)
    result = judge_trend(enriched, symbol=symbol, name=name)
    return asdict(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A股趋势判断 Skill")
    parser.add_argument("--symbol", required=True, help="A股股票代码，例如 600519")
    parser.add_argument("--start-date", default="20240101", help="开始日期，格式 YYYYMMDD")
    parser.add_argument("--end-date", default=pd.Timestamp.today().strftime("%Y%m%d"), help="结束日期，格式 YYYYMMDD")
    parser.add_argument("--adjust", default="qfq", choices=["", "qfq", "hfq"], help="复权方式")
    parser.add_argument("--output", default="", help="输出 JSON 文件路径")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    result = run(
        symbol=args.symbol,
        start_date=args.start_date,
        end_date=args.end_date,
        adjust=args.adjust,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload)
    print(payload)


if __name__ == "__main__":
    main()
